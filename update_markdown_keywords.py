#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_markdown_keywords.py - Markdownファイルにキーワード情報を追加
"""

import os
import json
import re
import unicodedata

def safe_filename(title: str, maxlen: int = 120) -> str:
    """安全なファイル名生成"""
    SAFE_CHARS = "-_.() " + "".join(chr(c) for c in range(0x30, 0x7B) if chr(c).isalnum())
    norm = unicodedata.normalize("NFKC", title)
    s = "".join(ch for ch in norm if ch in SAFE_CHARS)
    s = re.sub(r"\s+", "_", s).strip("_")
    s = re.sub(r"_+", "_", s)[:maxlen]
    return s or "untitled"

def format_keywords_section(keywords_data: dict) -> str:
    """キーワード情報をMarkdown形式で整形"""
    sections = []
    
    # 統合キーワード
    combined = keywords_data.get('combined_keywords', [])
    if combined:
        sections.append("### 主要キーワード")
        keyword_tags = " ".join([f"#{kw.replace(' ', '_').replace('-', '_')}" for kw in combined[:10]])
        sections.append(keyword_tags)
    
    # Crossrefキーワード
    crossref_kw = keywords_data.get('crossref_keywords', [])
    if crossref_kw:
        sections.append("\n### Crossref分野キーワード")
        sections.append(", ".join(crossref_kw))
    
    # コンテンツキーワード
    content_kw = keywords_data.get('content_keywords', [])
    if content_kw:
        sections.append("\n### 内容分析キーワード")
        sections.append(", ".join(content_kw))
    
    # 参考文献キーワード
    ref_kw = keywords_data.get('reference_keywords', [])
    if ref_kw:
        sections.append("\n### 関連研究キーワード")
        sections.append(", ".join(ref_kw))
    
    return "\n".join(sections)

def update_markdown_with_keywords(json_path: str, md_dir: str) -> None:
    """JSONのキーワード情報をMarkdownファイルに反映"""
    # JSONデータ読み込み
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    title = data.get('title', 'untitled')
    keywords_data = data.get('keywords', {})
    
    if not keywords_data:
        return
    
    # 対応するMarkdownファイルパス
    md_filename = safe_filename(title) + ".md"
    md_path = os.path.join(md_dir, md_filename)
    
    if not os.path.exists(md_path):
        return
    
    # 既存のMarkdownファイル読み込み
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # キーワードセクションが既に存在するかチェック
    if "## キーワード分析" in content:
        return  # 既に追加済み
    
    # キーワードセクションを生成
    keywords_section = format_keywords_section(keywords_data)
    
    # Markdownに挿入（Abstractの後、参考文献の前）
    if "## 参考文献" in content:
        # 参考文献の前に挿入
        content = content.replace(
            "## 参考文献",
            f"## キーワード分析\n\n{keywords_section}\n\n## 参考文献"
        )
    elif "## DOI" in content:
        # DOIの前に挿入
        content = content.replace(
            "## DOI",
            f"## キーワード分析\n\n{keywords_section}\n\n## DOI"
        )
    else:
        # ファイル末尾に追加
        content += f"\n\n## キーワード分析\n\n{keywords_section}"
    
    # ファイル保存
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    combined_count = len(keywords_data.get('combined_keywords', []))
    print(f"Updated: {md_filename} - {combined_count} keywords added")

def main():
    """メイン処理"""
    print("Markdownキーワード更新開始...")
    
    base = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(base, "JSON_folder")
    md_dir = os.path.join(base, "md_folder")
    
    # 全JSONファイルを処理
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    updated_count = 0
    
    for json_file in json_files:
        json_path = os.path.join(json_dir, json_file)
        try:
            update_markdown_with_keywords(json_path, md_dir)
            updated_count += 1
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    print(f"Markdown更新完了: {updated_count} ファイル処理")

if __name__ == "__main__":
    main()