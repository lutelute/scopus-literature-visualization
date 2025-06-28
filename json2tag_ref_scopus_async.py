#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
json2tag_ref_scopus_async.py ― 改良版 (DOI解決500件ずつ分割処理)
"""

import os, json, re, unicodedata, asyncio, aiohttp, async_timeout
import time, random, hashlib, logging, traceback
from urllib.parse import quote_plus
from typing import Dict, List, Set

import nltk
from nltk.tokenize import word_tokenize
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

# ---------- 非同期 DOI 解決 ----------
async def fetch_doi_titles(dois: Set[str]) -> Dict[str, str]:
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
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="DOI 解決"):
            await f
            await asyncio.sleep(DELAY)

    return out

# ---------- メイン ----------
def main():
    try:
        print("json2tag_ref_scopus_async.py の実行開始")
        ensure_nltk()
        base = os.path.dirname(os.path.abspath(__file__))
        jdir = os.path.join(base, "JSON_folder")
        mdir = os.path.join(base, "md_folder")
        os.makedirs(mdir, exist_ok=True)

        files = [f for f in os.listdir(jdir) if f.endswith(".json")]
        print(f"{len(files)} 件の JSON ファイルを処理します")

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

        for i, chunk in enumerate(chunk_list(need, CHUNK_SIZE), 1):
            print(f"=== DOI チャンク {i} / {((len(need)-1)//CHUNK_SIZE)+1} 開始 ===")
            res = asyncio.run(fetch_doi_titles(set(chunk)))
            doi2title.update(res)
            with open("doi_title_cache.json", "w", encoding="utf-8") as fp:
                json.dump(doi2title, fp, ensure_ascii=False, indent=0)

        bar = tqdm(total=len(files), desc="MD 生成")
        for jf in files:
            try:
                data = json.load(open(os.path.join(jdir, jf), encoding="utf-8"))
                ttl = data.get("title", "")
                year = data.get("year", "Unknown")
                if not ttl:
                    bar.update(1)
                    continue

                tags = [t.lower() for t, p in nltk.pos_tag(word_tokenize(ttl))
                        if p not in STOP_POS and t.lower() not in STOP_TOK]
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
        print("Markdown 完了")
    except Exception:
        logging.error(f"FATAL\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()