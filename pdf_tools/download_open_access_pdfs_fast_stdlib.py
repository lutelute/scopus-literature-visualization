#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_open_access_pdfs_fast_stdlib.py - オープンアクセス論文PDF高速並列取得（標準ライブラリ版）
"""

import os
import json
import re
import unicodedata
import urllib.request
import urllib.parse
import urllib.error
import time
from urllib.parse import urljoin, urlparse
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

def make_request(url: str, method: str = 'GET', timeout: int = 10) -> Tuple[bool, Dict, bytes]:
    """HTTP リクエスト実行"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        if method == 'HEAD':
            req.get_method = lambda: 'HEAD'
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_headers = dict(response.headers)
            content = response.read() if method == 'GET' else b''
            return True, response_headers, content
            
    except Exception as e:
        print(f"❌ Request failed for {url}: {e}")
        return False, {}, b''

def check_open_access_status(crossref_data: dict) -> dict:
    """Crossrefデータからオープンアクセス情報を確認"""
    oa_info = {
        'is_open_access': False,
        'license_type': None,
        'pdf_urls': [],
        'oa_locations': []
    }
    
    # ライセンス情報をチェック
    licenses = crossref_data.get('license', [])
    for license_info in licenses:
        if isinstance(license_info, dict):
            license_url = license_info.get('URL', '')
            if any(oa_indicator in license_url.lower() for oa_indicator in 
                   ['creativecommons', 'cc-by', 'open-access']):
                oa_info['is_open_access'] = True
                oa_info['license_type'] = license_url
                break
    
    # リンク情報からPDF URLを探す
    links = crossref_data.get('link', [])
    for link in links:
        if isinstance(link, dict):
            content_type = link.get('content-type', '')
            url = link.get('URL', '')
            if content_type == 'application/pdf' or 'pdf' in url.lower():
                oa_info['pdf_urls'].append(url)
    
    # URLフィールドもチェック
    main_url = crossref_data.get('URL', '')
    if main_url:
        oa_info['oa_locations'].append(main_url)
    
    return oa_info

def find_pdf_urls_from_doi(doi: str) -> List[str]:
    """DOIから複数のソースでPDF URLを探索"""
    pdf_urls = []
    
    # 1. Unpaywall API (オープンアクセス情報)
    try:
        unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email=research@example.com"
        success, headers, content = make_request(unpaywall_url, timeout=5)
        if success and content:
            data = json.loads(content.decode('utf-8'))
            if data.get('is_oa', False):
                # ベストOA locationを取得
                best_oa = data.get('best_oa_location')
                if best_oa and best_oa.get('url_for_pdf'):
                    pdf_urls.append(best_oa['url_for_pdf'])
                
                # その他のOA locationsも取得
                oa_locations = data.get('oa_locations', [])
                for location in oa_locations:
                    if location.get('url_for_pdf'):
                        pdf_urls.append(location['url_for_pdf'])
        time.sleep(0.1)  # API制限対応
    except Exception as e:
        print(f"Unpaywall API error for {doi}: {e}")
    
    # 2. DOI直接アクセスでPDFリダイレクトをチェック
    try:
        doi_url = f"https://doi.org/{doi}"
        
        # urllib でリダイレクトを追跡
        redirected_url = doi_url
        try:
            req = urllib.request.Request(doi_url, headers={
                'User-Agent': 'Mozilla/5.0 (Academic Research Bot 1.0)'
            })
            with urllib.request.urlopen(req, timeout=5) as response:
                redirected_url = response.url
        except:
            pass
        
        # IEEE, arXiv, PLoS ONE等のオープンアクセスパターン
        if any(pattern in redirected_url.lower() for pattern in 
               ['arxiv.org', 'plos', 'biomedcentral', 'frontiersin', 'mdpi.com', 'ieee']):
            # PDF URLパターンを試行
            pdf_patterns = [
                redirected_url.replace('/abs/', '/pdf/') + '.pdf',  # arXiv
                redirected_url + '.pdf',  # 一般的なパターン
                redirected_url.replace('/article/', '/pdf/'),  # 学術誌パターン
            ]
            pdf_urls.extend(pdf_patterns)
        time.sleep(0.1)
    except Exception as e:
        print(f"DOI redirect check error for {doi}: {e}")
    
    return list(set(pdf_urls))  # 重複削除

def download_pdf_fast(url: str, filepath: str) -> bool:
    """PDF ファイルをダウンロード（高速版）"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            # Content-Type をチェック
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                print(f"❌ Not a PDF file: {content_type}")
                return False
            
            # ファイルサイズチェック（最小100KB、最大50MB）
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb < 0.1 or size_mb > 50:
                    print(f"❌ File size out of range: {size_mb:.1f}MB")
                    return False
            
            # 高速ダウンロード
            with open(filepath, 'wb') as f:
                while True:
                    chunk = response.read(64*1024)  # 64KB chunks
                    if not chunk:
                        break
                    f.write(chunk)
        
        # ダウンロード後のファイルサイズチェック
        file_size = os.path.getsize(filepath)
        if file_size < 100 * 1024:  # 100KB未満
            os.remove(filepath)
            print(f"❌ Downloaded file too small: {file_size} bytes")
            return False
        
        print(f"✅ Successfully downloaded: {os.path.basename(filepath)} ({file_size/1024:.0f}KB)")
        return True
        
    except Exception as e:
        print(f"❌ Download failed from {url}: {e}")
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

**フルテキストPDF**: [📄 {pdf_filename}](PDF/{pdf_filename})

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
        print(f"❌ Error adding PDF embed to {md_path}: {e}")

def process_json_for_pdf(json_path: str, pdf_dir: str, md_dir: str) -> Tuple[bool, str]:
    """JSONファイルを処理してPDFダウンロードを試行"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        title = data.get('title', 'untitled')
        doi = data.get('doi', '')
        
        if not doi:
            return False, f"No DOI found for: {title}"
        
        # 安全なファイル名生成
        safe_title = safe_filename(title)
        pdf_filename = f"{safe_title}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        md_path = os.path.join(md_dir, f"{safe_title}.md")
        
        # 既にPDFが存在する場合はスキップ
        if os.path.exists(pdf_path):
            return False, f"PDF already exists: {pdf_filename}"
        
        thread_id = threading.current_thread().name
        print(f"🔍 [{thread_id}] Processing: {title[:50]}...")
        print(f"📋 [{thread_id}] DOI: {doi}")
        
        # Crossrefデータからオープンアクセス情報を確認
        crossref_data = data.get('_crossref_full', {})
        oa_info = check_open_access_status(crossref_data)
        
        # PDF URL を探索
        pdf_urls = find_pdf_urls_from_doi(doi)
        pdf_urls.extend(oa_info['pdf_urls'])
        
        if not pdf_urls:
            return False, f"No PDF URLs found for: {title}"
        
        # PDF ダウンロードを試行
        for i, url in enumerate(pdf_urls[:3]):  # 最大3つのURLを試行
            print(f"🔄 [{thread_id}] Trying URL {i+1}/{min(3, len(pdf_urls))}: {url[:80]}...")
            if download_pdf_fast(url, pdf_path):
                # ダウンロード成功時、MarkdownにPDF埋め込みを追加
                if os.path.exists(md_path):
                    add_pdf_embed_to_markdown(md_path, pdf_filename)
                return True, f"Successfully downloaded: {pdf_filename}"
            time.sleep(0.5)  # 試行間隔
        
        return False, f"All download attempts failed for: {title}"
        
    except Exception as e:
        return False, f"Error processing {json_path}: {e}"

def main():
    """メイン処理（threading版）"""
    print("🚀 オープンアクセスPDF高速並列取得開始（標準ライブラリ版）...")
    start_time = time.time()
    
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_dir = os.path.join(base, "JSON_folder")
    md_dir = os.path.join(base, "md_folder")
    pdf_dir = os.path.join(base, "PDF")
    
    # PDF ディレクトリ作成
    os.makedirs(pdf_dir, exist_ok=True)
    
    # 全JSONファイルを取得
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    print(f"📊 Processing {len(json_files)} files with parallel threads...")
    
    # 並列処理実行（最大同時スレッド数）
    max_workers = min(8, len(json_files))  # CPU数に応じて調整
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 全ファイルをタスクとして提出
        future_to_file = {}
        for json_file in json_files:
            json_path = os.path.join(json_dir, json_file)
            future = executor.submit(process_json_for_pdf, json_path, pdf_dir, md_dir)
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
                    print(f"✅ [{completed}/{len(json_files)}] {message}")
                else:
                    print(f"ℹ️  [{completed}/{len(json_files)}] {message}")
            except Exception as e:
                print(f"❌ [{completed}/{len(json_files)}] Error with {json_file}: {e}")
            
            # 進行状況表示
            if completed % 5 == 0 or completed == len(json_files):
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"⏳ Progress: {completed}/{len(json_files)} files | {elapsed:.1f}s | {rate:.1f} files/sec")
    
    # 結果集計
    total_pdfs = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"\n🎉 PDF取得完了!")
    print(f"📈 処理時間: {elapsed:.1f}秒")
    print(f"📊 新規PDF取得: {success_count}件")
    print(f"📁 総PDF数: {total_pdfs}件")
    print(f"📂 PDFフォルダ: {pdf_dir}")
    print(f"⚡ 処理速度: {len(json_files)/elapsed:.1f} files/sec")
    print(f"🧵 並列度: {max_workers} threads")

if __name__ == "__main__":
    main()