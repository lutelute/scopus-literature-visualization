#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
json2tag_ref_scopus_async.py ― 改良版 (DOI解決500件ずつ分割処理)
"""

import os, json, re, unicodedata, asyncio
import time, random, hashlib, logging, traceback
from urllib.parse import quote_plus
from typing import Dict, List, Set

# オプションライブラリのインポート（エラーハンドリング付き）
try:
    import aiohttp, async_timeout
    ASYNC_AVAILABLE = True
    print("✅ aiohttp利用可能 - 高速並列処理モード")
except ImportError:
    ASYNC_AVAILABLE = False
    print("⚠️  aiohttp未インストール - 標準版で実行")
    import urllib.request
    import urllib.error

try:
    import nltk
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
    print("✅ NLTK利用可能 - 高度なキーワード分析")
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️  NLTK未インストール - 基本キーワード分析のみ")

from tqdm import tqdm

# ---------- パラメータ ----------
SAFE_ASC = "-_.() " + "".join(chr(c) for c in range(0x30, 0x7B) if chr(c).isalnum())
STOP_POS = {"IN", "CC", "DT", "PRP", "WDT", "WP", "WP$", "VBZ", "VBP", "VBD", "VB", "VBG", "VBN", "RB"}
STOP_TOK = {"am", "is", "are", "was", "were", "be", "being", "been", "not", "to"}
MAX_CONC = 8
DELAY = 0.01
TIMEOUT = 15
MAILTO = "your_email@example.com"
HEAD_X = {"User-Agent": f"mdgen/2.0 (mailto:{MAILTO})"}
CHUNK_SIZE = 500

# ---------- ログ ----------
logging.basicConfig(filename="error_log.txt", filemode="a", level=logging.INFO,
                    format="%(asctime)s\tmdgen\t%(levelname)s\t%(message)s")

# ---------- ヘルパ関数 ----------
def safe_fn(title: str, maxlen: int = 120) -> str:
    norm = unicodedata.normalize("NFKC", title)
    s = "".join(ch for ch in norm if ch in SAFE_ASC)
    s = re.sub(r"\s+", "_", s).strip("_")
    s = re.sub(r"_+", "_", s)[:maxlen]
    return s or hashlib.md5(title.encode()).hexdigest()[:maxlen]

def ensure_nltk():
    """NLTK利用可能時のみリソースダウンロード"""
    if not NLTK_AVAILABLE:
        return
        
    for res in [("tokenizers/punkt", "punkt"),
                ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng")]:
        try:
            nltk.data.find(res[0])
        except LookupError:
            nltk.download(res[1])

def chunk_list(lst, n):
    """リストを n 件ごとに分割"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# ---------- 非同期 DOI 解決 (aiohttp版) ----------
async def fetch_doi_titles_async(dois: Set[str]) -> Dict[str, str]:
    """非同期版DOI解決（aiohttp使用）"""
    out = {d: "Unknown" for d in dois}
    sem = asyncio.Semaphore(MAX_CONC)

    async with aiohttp.ClientSession() as sess:
        async def fetch_one(doi):
            try:
                async with sem, async_timeout.timeout(TIMEOUT):
                    r = await sess.get(f"https://api.crossref.org/works/{quote_plus(doi)}", headers=HEAD_X)
                    if r.status == 200:
                        js = await r.json()
                        out[doi] = js["message"].get("title", ["Unknown"])[0]
                        return
            except:
                pass
            try:
                async with sem, async_timeout.timeout(TIMEOUT):
                    r = await sess.get(f"https://doi.org/{quote_plus(doi)}",
                                       headers={"Accept": "application/vnd.citationstyles.csl+json", **HEAD_X})
                    if r.status == 200:
                        js = await r.json()
                        out[doi] = js.get("title", "Unknown")
            except:
                pass

        tasks = [fetch_one(d) for d in dois]
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="DOI 解決 (高速版)"):
            await f
            await asyncio.sleep(DELAY)

    return out

# ---------- 標準版 DOI 解決 (urllib版) ----------
def fetch_doi_titles_sync(dois: Set[str]) -> Dict[str, str]:
    """標準版DOI解決（urllib使用）"""
    out = {d: "Unknown" for d in dois}
    
    for doi in tqdm(dois, desc="DOI 解決 (標準版)"):
        try:
            # Crossref API試行
            req = urllib.request.Request(
                f"https://api.crossref.org/works/{quote_plus(doi)}", 
                headers=HEAD_X
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                if response.status == 200:
                    js = json.loads(response.read().decode())
                    out[doi] = js["message"].get("title", ["Unknown"])[0]
                    time.sleep(DELAY * 10)  # 標準版はより控えめな間隔
                    continue
        except:
            pass
            
        try:
            # DOI.org API試行
            req = urllib.request.Request(
                f"https://doi.org/{quote_plus(doi)}",
                headers={"Accept": "application/vnd.citationstyles.csl+json", **HEAD_X}
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                if response.status == 200:
                    js = json.loads(response.read().decode())
                    out[doi] = js.get("title", "Unknown")
        except:
            pass
        
        time.sleep(DELAY * 10)  # 標準版はより控えめな間隔
    
    return out

# ---------- DOI解決統合関数 ----------
def fetch_doi_titles(dois: Set[str]) -> Dict[str, str]:
    """利用可能なライブラリに応じてDOI解決を実行"""
    if ASYNC_AVAILABLE:
        return asyncio.run(fetch_doi_titles_async(dois))
    else:
        return fetch_doi_titles_sync(dois)

# ---------- メイン ----------
def main():
    try:
        print("🚀 json2tag_ref_scopus_async.py の実行開始")
        print("=" * 60)
        
        ensure_nltk()
        base = os.path.dirname(os.path.abspath(__file__))
        jdir = os.path.join(base, "JSON_folder")
        mdir = os.path.join(base, "md_folder")
        os.makedirs(mdir, exist_ok=True)

        files = [f for f in os.listdir(jdir) if f.endswith(".json")]
        print(f"📁 {len(files)} 件の JSON ファイルを処理します")
        
        if not files:
            print("❌ JSONファイルが見つかりません")
            return

        ref_dois: Set[str] = set()
        for jf in files:
            try:
                data = json.load(open(os.path.join(jdir, jf)))
                for r in data.get("references", []):
                    if isinstance(r, dict) and r.get("DOI"):
                        ref_dois.add(r["DOI"].lower())
            except Exception as e:
                logging.error(f"SCAN_ERR\t{jf}\t{e}")

        doi2title: Dict[str, str] = {}
        if os.path.exists("doi_title_cache.json"):
            doi2title.update(json.load(open("doi_title_cache.json")))

        need = list(ref_dois - doi2title.keys())
        print(f"解決必要 DOI 数: {len(need)}")

        total_chunks = ((len(need)-1)//CHUNK_SIZE)+1 if need else 0
        print(f"📊 DOI解決を{total_chunks}個のチャンクに分けて処理します")
        
        for i, chunk in enumerate(chunk_list(need, CHUNK_SIZE), 1):
            print(f"\n🔍 === DOI チャンク {i}/{total_chunks} 処理中 ({len(chunk)}件) ===")
            chunk_start = time.time()
            res = fetch_doi_titles(set(chunk))
            chunk_time = time.time() - chunk_start
            
            # 成功/失敗統計
            成功数 = sum(1 for v in res.values() if v != "Unknown")
            失敗数 = len(res) - 成功数
            
            doi2title.update(res)
            with open("doi_title_cache.json", "w", encoding="utf-8") as fp:
                json.dump(doi2title, fp, ensure_ascii=False, indent=0)
            
            print(f"✅ チャンク{i}完了: 成功{成功数}件, 失敗{失敗数}件, 時間{chunk_time:.1f}秒")
            print(f"📁 累計解決DOI数: {len([v for v in doi2title.values() if v != 'Unknown'])}")
            
            if i < total_chunks:
                print(f"⏳ 次のチャンクまで1秒待機...")
                time.sleep(1)

        bar = tqdm(total=len(files), desc="MD 生成")
        for jf in files:
            try:
                data = json.load(open(os.path.join(jdir, jf), encoding="utf-8"))
                ttl = data.get("title", "")
                year = data.get("year", "Unknown")
                if not ttl:
                    bar.update(1)
                    continue

                # キーワード抽出（NLTK利用可能時は高度な分析、不可時は基本分析）
                if NLTK_AVAILABLE:
                    tags = [t.lower() for t, p in nltk.pos_tag(word_tokenize(ttl))
                            if p not in STOP_POS and t.lower() not in STOP_TOK]
                else:
                    # 基本的なキーワード抽出（単語分割のみ）
                    words = re.findall(r'\b[a-zA-Z]{3,}\b', ttl.lower())
                    tags = [w for w in words if w not in STOP_TOK]
                tags.append(f"year_{year}")
                md_p = os.path.join(mdir, safe_fn(ttl) + ".md")
                with open(md_p, "w", encoding="utf-8") as fp:
                    fp.write("#" + " #".join(tags))
                    fp.write("\n\n## Abstract\n\n" + data.get("abstract", ""))

                refs = data.get("references", [])
                with open(md_p, "a", encoding="utf-8") as fp:
                    if refs:
                        fp.write("\n\n## 参考文献\n\n")
                        for r in refs:
                            if isinstance(r, dict):
                                art = r.get("article-title")
                                doi = r.get("DOI", "").lower()
                                if doi:
                                    title = art or doi2title.get(doi, "Unknown")
                                    safe_title = safe_fn(title)
                                    fp.write(f"- DOI: {doi}\n  - [[{safe_title}]]\n")
                                else:
                                    safe_title = safe_fn(art or "Unknown")
                                    fp.write(f"- [[{safe_title}]]\n")
                            else:
                                safe_title = safe_fn(r)
                                fp.write(f"- [[{safe_title}]]\n")
                bar.update(1)
            except Exception as e:
                logging.error(f"MD_ERR\t{jf}\t{e}")
                bar.update(1)

        bar.close()
        
        # 最終統計
        print("\n" + "=" * 60)
        print("🎉 処理完了統計")
        print(f"📊 処理したJSONファイル: {len(files)}件")
        print(f"📊 解決したDOI数: {len([v for v in doi2title.values() if v != 'Unknown'])}")
        print(f"📊 総DOI数: {len(doi2title)}")
        print(f"📁 出力ディレクトリ: {mdir}")
        
        # 生成されたMarkdownファイル数確認
        md_count = len([f for f in os.listdir(mdir) if f.endswith('.md')])
        print(f"📝 生成Markdownファイル: {md_count}件")
        print("✅ Markdown生成完了")
        
    except Exception:
        logging.error(f"FATAL\n{traceback.format_exc()}")
        print(f"❌ 致命的エラーが発生しました。error_log.txt を確認してください。")

if __name__ == "__main__":
    main()