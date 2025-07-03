#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_hashtag_keywords.py - Markdownファイルにハッシュタグキーワードを追加
"""

import os
import json
import re
import unicodedata
from pathlib import Path

def safe_filename(title: str, maxlen: int = 120) -> str:
    """安全なファイル名生成"""
    SAFE_CHARS = "-_.() " + "".join(chr(c) for c in range(0x30, 0x7B) if chr(c).isalnum())
    norm = unicodedata.normalize("NFKC", title)
    s = "".join(ch for ch in norm if ch in SAFE_CHARS)
    s = re.sub(r"\s+", "_", s).strip("_")
    s = re.sub(r"_+", "_", s)[:maxlen]
    return s or "untitled"

def extract_keywords_from_doi_title(json_data: dict) -> list:
    """DOIとタイトルからキーワードを抽出"""
    keywords = set()
    
    # タイトルからキーワード抽出
    title = json_data.get('title', '')
    if title:
        # 英語の重要単語を抽出（3文字以上）
        words = re.findall(r'\b[A-Za-z]{3,}\b', title.lower())
        # ストップワードを除外
        stop_words = {
            'the', 'and', 'for', 'with', 'from', 'are', 'was', 'were', 'been', 
            'have', 'has', 'had', 'will', 'would', 'can', 'could', 'may', 
            'might', 'must', 'shall', 'should', 'this', 'that', 'these', 
            'those', 'what', 'when', 'where', 'who', 'why', 'how', 'all',
            'any', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'only', 'own', 'same', 'than', 'too', 'very', 'one', 'two',
            'three', 'four', 'five', 'also', 'back', 'even', 'here', 'new',
            'now', 'old', 'see', 'way', 'well', 'come', 'get', 'made', 'make',
            'take', 'use', 'work', 'first', 'last', 'long', 'good', 'great',
            'little', 'own', 'right', 'big', 'high', 'different', 'small',
            'large', 'next', 'early', 'young', 'important', 'few', 'public',
            'bad', 'same', 'able'
        }
        title_keywords = [w for w in words if w not in stop_words and len(w) >= 3]
        keywords.update(title_keywords[:8])  # 上位8個
    
    # DOIから学術分野推定
    doi = json_data.get('doi', '')
    if doi:
        # IEEE系はEngineering/Technology関連
        if 'ieee' in doi.lower():
            keywords.update(['engineering', 'technology', 'electrical'])
        # Elsevier系
        elif 'elsevier' in doi.lower() or doi.startswith('10.1016'):
            keywords.add('research')
        # Nature系
        elif 'nature' in doi.lower() or doi.startswith('10.1038'):
            keywords.update(['science', 'nature'])
        # Springer系
        elif 'springer' in doi.lower() or doi.startswith('10.1007'):
            keywords.add('academic')
    
    # 年度情報
    year = json_data.get('year', '')
    if year:
        keywords.add(f'year{year}')
    
    # Journal情報から分野推定
    journal = json_data.get('journal', '').lower()
    if journal:
        if any(term in journal for term in ['power', 'energy', 'electric']):
            keywords.update(['power', 'energy'])
        elif any(term in journal for term in ['computer', 'software', 'algorithm']):
            keywords.update(['computer', 'technology'])
        elif any(term in journal for term in ['medical', 'health', 'clinical']):
            keywords.update(['medical', 'health'])
        elif any(term in journal for term in ['material', 'chemistry']):
            keywords.update(['materials', 'chemistry'])
    
    return list(keywords)

def add_hashtag_keywords_to_markdown(md_path: str, keywords: list) -> bool:
    """Markdownファイルにハッシュタグキーワードを追加"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既にキーワードセクションがある場合はスキップ
        if "## キーワード" in content or "#" in content.split('\n')[0]:
            return False
        
        # ハッシュタグ形式のキーワード作成
        hashtags = []
        for keyword in keywords:
            # 安全なハッシュタグ名に変換
            clean_keyword = re.sub(r'[^a-zA-Z0-9_]', '', keyword.lower())
            if clean_keyword and len(clean_keyword) >= 2:
                hashtags.append(f"#{clean_keyword}")
        
        if not hashtags:
            return False
        
        # YAMLフロントマター後、Abstract前にキーワードセクションを挿入
        keyword_section = f"""
## キーワード

{' '.join(hashtags)}

"""
        
        # Abstractセクションの前に挿入
        if "## Abstract" in content:
            content = content.replace("## Abstract", keyword_section + "## Abstract")
        elif "## 論文情報" in content:
            content = content.replace("## 論文情報", keyword_section + "## 論文情報")
        else:
            # YAMLフロントマター終了後に挿入
            if content.startswith('---'):
                lines = content.split('\n')
                yaml_end = -1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        yaml_end = i
                        break
                
                if yaml_end != -1:
                    lines.insert(yaml_end + 1, keyword_section.strip())
                    content = '\n'.join(lines)
                else:
                    content = keyword_section + content
            else:
                content = keyword_section + content
        
        # ファイル保存
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error processing {md_path}: {e}")
        return False

def main():
    """メイン処理"""
    print("Markdownファイルにハッシュタグキーワード追加開始...")
    
    base = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(base, "JSON_folder")
    md_dir = os.path.join(base, "md_folder")
    
    if not os.path.exists(json_dir):
        print(f"Error: JSONディレクトリが見つかりません: {json_dir}")
        return
    
    if not os.path.exists(md_dir):
        print(f"Error: Markdownディレクトリが見つかりません: {md_dir}")
        return
    
    # JSONファイルを処理
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    processed_count = 0
    
    for json_file in json_files:
        json_path = os.path.join(json_dir, json_file)
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            title = data.get('title', '')
            if not title:
                continue
            
            # 対応するMarkdownファイルを探す
            safe_title = safe_filename(title)
            md_path = os.path.join(md_dir, f"{safe_title}.md")
            
            if not os.path.exists(md_path):
                print(f"Warning: Markdownファイルが見つかりません: {safe_title}.md")
                continue
            
            # キーワード抽出
            keywords = extract_keywords_from_doi_title(data)
            
            if not keywords:
                print(f"Info: キーワードが抽出できませんでした: {title}")
                continue
            
            # ハッシュタグキーワード追加
            if add_hashtag_keywords_to_markdown(md_path, keywords):
                processed_count += 1
                print(f"✅ {safe_title}.md にキーワード追加: {', '.join(keywords[:5])}")
            else:
                print(f"⏭️ {safe_title}.md スキップ（既存またはエラー）")
                
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    print(f"\n完了: {processed_count}個のMarkdownファイルにハッシュタグキーワードを追加しました")

if __name__ == "__main__":
    main()