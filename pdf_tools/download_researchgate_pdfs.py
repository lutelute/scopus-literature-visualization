#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_researchgate_pdfs.py - ResearchGateからの積極的PDF取得
"""

import os
import json
import re
import unicodedata
import urllib.request
import urllib.parse
import urllib.error
import time
import random
from urllib.parse import urljoin, urlparse, quote
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import List, Dict, Tuple

def safe_filename(title: str, maxlen: int = 120) -> str:
    """安全なファイル名生成"""
    SAFE_CHARS = "-_.() " + "".join(chr(c) for c in range(0x30, 0x7B) if chr(c).isalnum())
    norm = unicodedata.normalize("NFKC", title)
    s = "".join(ch for ch in norm if ch in SAFE_CHARS)
    s = re.sub(r"\s+", "_", s).strip("_")
    s = re.sub(r"_+", "_", s)[:maxlen]
    return s or "untitled"

def get_random_headers() -> Dict[str, str]:
    """ランダムなUser-Agentとヘッダーを生成"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def search_researchgate_for_paper(title: str, doi: str = "", authors: List[str] = None) -> List[str]:
    """ResearchGateで論文を検索してPDF URLを取得"""
    potential_urls = []
    
    try:
        # 検索クエリ作成
        search_terms = []
        if title:
            # タイトルから重要なキーワードを抽出
            title_words = re.findall(r'\b\w{4,}\b', title.lower())
            search_terms.extend(title_words[:5])  # 最初の5つの重要な単語
        
        if doi:
            search_terms.append(doi)
        
        if authors:
            # 著者の姓を追加
            for author in authors[:2]:  # 最初の2人の著者
                if isinstance(author, str):
                    name_parts = author.split()
                    if name_parts:
                        search_terms.append(name_parts[-1])  # 姓
        
        # 検索URL構築
        query = " ".join(search_terms[:8])  # 最大8つのキーワード
        encoded_query = quote(query)
        search_url = f"https://www.researchgate.net/search?q={encoded_query}"
        
        headers = get_random_headers()
        req = urllib.request.Request(search_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
            # ResearchGateの論文ページURLを抽出
            publication_urls = re.findall(r'href="(/publication/\d+[^"]*)"', content)
            
            for url_path in publication_urls[:5]:  # 最初の5つの結果
                full_url = f"https://www.researchgate.net{url_path}"
                potential_urls.append(full_url)
        
        time.sleep(random.uniform(1, 3))  # ランダムな待機時間
        
    except Exception as e:
        print(f"[NG] ResearchGate search error: {e}")
    
    return potential_urls

def extract_pdf_from_researchgate_page(page_url: str) -> List[str]:
    """ResearchGateの論文ページからPDF URLを抽出"""
    pdf_urls = []
    
    try:
        headers = get_random_headers()
        req = urllib.request.Request(page_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
            # ResearchGateのPDF URLパターンを検索
            pdf_patterns = [
                r'href="([^"]*\.pdf[^"]*)"',  # 直接PDF リンク
                r'data-url="([^"]*\.pdf[^"]*)"',  # data-url属性のPDF
                r'src="([^"]*\.pdf[^"]*)"',  # src属性のPDF
                r'"pdf_url":"([^"]*)"',  # JSON内のPDF URL
                r'"fullTextUrl":"([^"]*)"',  # フルテキストURL
                r'href="(/publication/\d+[^"]*\.pdf[^"]*)"',  # 相対パスのPDF
            ]
            
            for pattern in pdf_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match.startswith('/'):
                        pdf_url = f"https://www.researchgate.net{match}"
                    else:
                        pdf_url = match
                    
                    # 不適切なURLを除外
                    if not any(skip in pdf_url.lower() for skip in ['thumbnail', 'preview', 'icon']):
                        pdf_urls.append(pdf_url)
            
            # ResearchGateの直接ダウンロードリンクも探す
            download_patterns = [
                r'"downloadUrl":"([^"]*)"',
                r'data-download-url="([^"]*)"',
                r'href="([^"]*download[^"]*)"'
            ]
            
            for pattern in download_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match.startswith('/'):
                        download_url = f"https://www.researchgate.net{match}"
                    else:
                        download_url = match
                    pdf_urls.append(download_url)
        
        time.sleep(random.uniform(0.5, 2))  # ランダムな待機時間
        
    except Exception as e:
        print(f"[NG] Error extracting PDF from {page_url}: {e}")
    
    return list(set(pdf_urls))  # 重複削除

def download_pdf_from_researchgate(url: str, filepath: str) -> bool:
    """ResearchGateからPDFをダウンロード"""
    try:
        headers = get_random_headers()
        headers['Referer'] = 'https://www.researchgate.net/'
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            # Content-Type チェック
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                # HTMLページの場合、さらにPDFリンクを探す
                if 'text/html' in content_type:
                    content = response.read().decode('utf-8', errors='ignore')
                    pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', content)
                    if pdf_links:
                        # 最初のPDFリンクを試行
                        return download_pdf_from_researchgate(pdf_links[0], filepath)
                print(f"[NG] Not a PDF file: {content_type}")
                return False
            
            # ファイルサイズチェック
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb < 0.1 or size_mb > 100:  # ResearchGateは大きなファイルもある
                    print(f"[NG] File size out of range: {size_mb:.1f}MB")
                    return False
            
            # ダウンロード実行
            with open(filepath, 'wb') as f:
                while True:
                    chunk = response.read(64*1024)  # 64KB chunks
                    if not chunk:
                        break
                    f.write(chunk)
        
        # ファイルサイズ最終チェック
        file_size = os.path.getsize(filepath)
        if file_size < 100 * 1024:  # 100KB未満
            os.remove(filepath)
            print(f"[NG] Downloaded file too small: {file_size} bytes")
            return False
        
        print(f"[OK] Successfully downloaded from ResearchGate: {os.path.basename(filepath)} ({file_size/1024:.0f}KB)")
        return True
        
    except Exception as e:
        print(f"[NG] Download failed from {url}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def add_pdf_embed_to_markdown(md_path: str, pdf_filename: str) -> None:
    """MarkdownファイルにPDF埋め込みを追加"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # PDF埋め込みセクションが既に存在するかチェック
        if "## PDF" in content:
            return  # 既に追加済み
        
        # PDF埋め込みセクションを作成
        pdf_section = f"""

## PDF

**フルテキストPDF**: [[FILE] {pdf_filename}](PDF/{pdf_filename})

<embed src="PDF/{pdf_filename}" type="application/pdf" width="100%" height="600px" />

*ブラウザでPDFが表示されない場合は、上記リンクから直接ダウンロードしてください。*"""
        
        # 参考文献の前に挿入
        if "## 参考文献" in content:
            content = content.replace("## 参考文献", pdf_section + "\n\n## 参考文献")
        else:
            content += pdf_section
        
        # ファイル保存
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📝 Added PDF embed to: {os.path.basename(md_path)}")
        
    except Exception as e:
        print(f"[NG] Error adding PDF embed to {md_path}: {e}")

def process_json_for_researchgate_pdf(json_path: str, pdf_dir: str, md_dir: str) -> Tuple[bool, str]:
    """JSONファイルを処理してResearchGateからPDFダウンロードを試行"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        title = data.get('title', 'untitled')
        doi = data.get('doi', '')
        authors = data.get('authors', [])
        
        if not title or title == 'untitled':
            return False, f"No valid title found"
        
        # 安全なファイル名生成
        safe_title = safe_filename(title)
        pdf_filename = f"{safe_title}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        md_path = os.path.join(md_dir, f"{safe_title}.md")
        
        # 既にPDFが存在する場合はスキップ
        if os.path.exists(pdf_path):
            return False, f"PDF already exists: {pdf_filename}"
        
        thread_id = threading.current_thread().name
        print(f"[INFO] [{thread_id}] Searching ResearchGate for: {title[:50]}...")
        
        # ResearchGateで検索
        researchgate_pages = search_researchgate_for_paper(title, doi, authors)
        
        if not researchgate_pages:
            return False, f"No ResearchGate pages found for: {title}"
        
        print(f"📋 [{thread_id}] Found {len(researchgate_pages)} ResearchGate pages")
        
        # 各ページからPDF URLを抽出してダウンロード試行
        for i, page_url in enumerate(researchgate_pages[:3]):  # 最大3ページを試行
            print(f"[PROC] [{thread_id}] Checking page {i+1}: {page_url}")
            
            pdf_urls = extract_pdf_from_researchgate_page(page_url)
            
            for j, pdf_url in enumerate(pdf_urls[:3]):  # 各ページから最大3つのPDF URL
                print(f"📥 [{thread_id}] Trying PDF {j+1}: {pdf_url[:80]}...")
                
                if download_pdf_from_researchgate(pdf_url, pdf_path):
                    # ダウンロード成功時、MarkdownにPDF埋め込みを追加
                    if os.path.exists(md_path):
                        add_pdf_embed_to_markdown(md_path, pdf_filename)
                    return True, f"Successfully downloaded from ResearchGate: {pdf_filename}"
                
                time.sleep(random.uniform(1, 3))  # 試行間隔
        
        return False, f"All ResearchGate download attempts failed for: {title}"
        
    except Exception as e:
        return False, f"Error processing {json_path}: {e}"

def main():
    """メイン処理"""
    print("[START] ResearchGate積極的PDF取得開始...")
    start_time = time.time()
    
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_dir = os.path.join(base, "JSON_folder")
    md_dir = os.path.join(base, "md_folder")
    pdf_dir = os.path.join(base, "PDF")
    
    # PDF ディレクトリ作成
    os.makedirs(pdf_dir, exist_ok=True)
    
    # 全JSONファイルを取得
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    print(f"[DATA] Processing {len(json_files)} files with ResearchGate search...")
    
    # 並列処理実行（ResearchGateの負荷を考慮して制限）
    max_workers = min(3, len(json_files))  # 最大3スレッド（サーバー負荷考慮）
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 全ファイルをタスクとして提出
        future_to_file = {}
        for json_file in json_files:
            json_path = os.path.join(json_dir, json_file)
            future = executor.submit(process_json_for_researchgate_pdf, json_path, pdf_dir, md_dir)
            future_to_file[future] = json_file
        
        # 完了したタスクから結果を取得
        completed = 0
        for future in as_completed(future_to_file):
            json_file = future_to_file[future]
            completed += 1
            
            try:
                success, message = future.result()
                if success:
                    success_count += 1
                    print(f"[OK] [{completed}/{len(json_files)}] {message}")
                else:
                    print(f"ℹ️  [{completed}/{len(json_files)}] {message}")
            except Exception as e:
                print(f"[NG] [{completed}/{len(json_files)}] Error with {json_file}: {e}")
            
            # 進行状況表示
            if completed % 3 == 0 or completed == len(json_files):
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"[WAIT] Progress: {completed}/{len(json_files)} files | {elapsed:.1f}s | {rate:.2f} files/sec")
    
    # 結果集計
    total_pdfs = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"\n[DONE] ResearchGate PDF取得完了!")
    print(f"[CHART] 処理時間: {elapsed:.1f}秒")
    print(f"[DATA] 新規PDF取得: {success_count}件")
    print(f"[DIR] 総PDF数: {total_pdfs}件")
    print(f"📂 PDFフォルダ: {pdf_dir}")
    print(f"⚡ 処理速度: {len(json_files)/elapsed:.2f} files/sec")
    print(f"🧵 並列度: {max_workers} threads")

if __name__ == "__main__":
    main()