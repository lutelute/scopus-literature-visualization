#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_yaml_metadata.py - MarkdownファイルにYAMLメタデータを追加
"""

import os
import json
import re
import unicodedata
from datetime import datetime

def safe_filename(title: str, maxlen: int = 120) -> str:
    """安全なファイル名生成"""
    SAFE_CHARS = "-_.() " + "".join(chr(c) for c in range(0x30, 0x7B) if chr(c).isalnum())
    norm = unicodedata.normalize("NFKC", title)
    s = "".join(ch for ch in norm if ch in SAFE_CHARS)
    s = re.sub(r"\s+", "_", s).strip("_")
    s = re.sub(r"_+", "_", s)[:maxlen]
    return s or "untitled"

def extract_main_keywords(json_data: dict) -> list:
    """メイン論文のキーワードを抽出"""
    keywords = []
    
    # CrossrefのsubjectフィールドからKeywords
    crossref_full = json_data.get('_crossref_full', {})
    subjects = crossref_full.get('subject', [])
    if subjects:
        keywords.extend(subjects)
    
    # タイトルから重要キーワード抽出
    title = json_data.get('title', '')
    if title:
        # 基本的なキーワード抽出（簡易版）
        title_words = re.findall(r'\b[A-Za-z]{3,}\b', title.lower())
        title_keywords = [w for w in title_words if w not in ['the', 'and', 'for', 'with', 'from']][:5]
        keywords.extend(title_keywords)
    
    return list(set(keywords))  # 重複削除

def create_yaml_frontmatter(json_data: dict) -> str:
    """YAMLフロントマターを生成"""
    title = json_data.get('title', 'Untitled')
    doi = json_data.get('doi', '')
    year = json_data.get('year', '')
    authors = json_data.get('authors', [])
    journal = json_data.get('journal', '')
    publisher = json_data.get('publisher', '')
    abstract = json_data.get('abstract', '')[:200] + "..." if len(json_data.get('abstract', '')) > 200 else json_data.get('abstract', '')
    
    # 著者名リスト生成
    author_names = []
    for author in authors[:3]:  # 最初の3人まで
        if isinstance(author, dict):
            name = author.get('name', 'Unknown')
            author_names.append(name)
    
    # メインキーワード抽出
    main_keywords = extract_main_keywords(json_data)
    
    # キーワード分析結果
    keywords_data = json_data.get('keywords', {})
    content_keywords = keywords_data.get('content_keywords', [])[:5]
    
    yaml_content = f"""---
title: "{title}"
doi: "{doi}"
year: {year}
authors:"""

    for author in author_names:
        yaml_content += f'\n  - "{author}"'
    
    yaml_content += f"""
journal: "{journal}"
publisher: "{publisher}"
keywords:"""
    
    for keyword in main_keywords[:8]:
        yaml_content += f'\n  - "{keyword}"'
    
    yaml_content += f"""
content_keywords:"""
    
    for keyword in content_keywords:
        yaml_content += f'\n  - "{keyword}"'
    
    yaml_content += f"""
abstract: "{abstract}"
created: "{datetime.now().strftime('%Y-%m-%d')}"
type: "research_paper"
---

"""
    
    return yaml_content

def add_main_paper_doi_section(json_data: dict) -> str:
    """メイン論文のDOI情報セクションを生成"""
    doi = json_data.get('doi', '')
    year = json_data.get('year', '')
    journal = json_data.get('journal', '')
    volume = json_data.get('volume', '')
    issue = json_data.get('issue', '')
    pages = json_data.get('pages', '')
    
    doi_section = f"""

## 論文情報

**DOI**: {doi}  
**発行年**: {year}  
**雑誌**: {journal}"""
    
    if volume:
        doi_section += f"  \n**巻**: {volume}"
    if issue:
        doi_section += f"  \n**号**: {issue}"
    if pages:
        doi_section += f"  \n**ページ**: {pages}"
    
    return doi_section

def update_markdown_with_yaml(json_path: str, md_dir: str) -> None:
    """MarkdownファイルにYAMLメタデータと論文情報を追加"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    title = data.get('title', 'untitled')
    md_filename = safe_filename(title) + ".md"
    md_path = os.path.join(md_dir, md_filename)
    
    if not os.path.exists(md_path):
        return
    
    # 既存のMarkdownファイル読み込み
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 既にYAMLフロントマターがあるかチェック
    if content.startswith('---'):
        return  # 既に追加済み
    
    # YAMLフロントマター生成
    yaml_frontmatter = create_yaml_frontmatter(data)
    
    # メイン論文のDOI情報セクション生成
    doi_section = add_main_paper_doi_section(data)
    
    # コンテンツを更新
    # タグ行を削除（YAMLのkeywordsで代替）
    content_lines = content.split('\n')
    if content_lines[0].startswith('#'):
        content_lines = content_lines[1:]  # タグ行を削除
    
    # 論文情報セクションを適切な位置に挿入
    updated_content = '\n'.join(content_lines)
    if "## 参考文献" in updated_content:
        updated_content = updated_content.replace("## 参考文献", doi_section + "\n\n## 参考文献")
    else:
        updated_content += doi_section
    
    # YAMLフロントマター + 更新されたコンテンツ
    final_content = yaml_frontmatter + updated_content
    
    # ファイル保存
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Updated: {md_filename} - YAML frontmatter and DOI info added")

def main():
    """メイン処理"""
    print("YAML メタデータ追加開始...")
    
    base = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(base, "JSON_folder")
    md_dir = os.path.join(base, "md_folder")
    
    # 全JSONファイルを処理
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    updated_count = 0
    
    for json_file in json_files:
        json_path = os.path.join(json_dir, json_file)
        try:
            update_markdown_with_yaml(json_path, md_dir)
            updated_count += 1
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    print(f"YAML メタデータ追加完了: {updated_count} ファイル処理")

if __name__ == "__main__":
    main()