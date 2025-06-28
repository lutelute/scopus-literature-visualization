#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhance_keywords.py - DOIからキーワード取得と関連参考文献からの推薦キーワード抽出
"""

import os
import json
import re
import unicodedata
from collections import Counter
from typing import Dict, List, Set
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def ensure_nltk_data():
    """必要なNLTKデータをダウンロード"""
    required_data = [
        ('tokenizers/punkt', 'punkt'),
        ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet')
    ]
    
    for path, name in required_data:
        try:
            nltk.data.find(path)
        except LookupError:
            print(f"Downloading {name}...")
            nltk.download(name)

def extract_crossref_keywords(crossref_data: dict) -> List[str]:
    """CrossrefデータからキーワードとSubjectを抽出"""
    keywords = []
    
    # Subjectフィールドから取得
    subjects = crossref_data.get('subject', [])
    if subjects:
        keywords.extend(subjects)
    
    # その他のキーワード関連フィールド
    if 'keyword' in crossref_data:
        keywords.extend(crossref_data['keyword'])
    
    return [kw.lower().strip() for kw in keywords if kw]

def extract_text_keywords(text: str, min_freq: int = 2, top_n: int = 20) -> List[str]:
    """テキストからキーワードを抽出"""
    if not text:
        return []
    
    # 前処理
    text = re.sub(r'<.*?>', '', text)  # HTMLタグ除去
    text = re.sub(r'\s+', ' ', text)   # 空白正規化
    
    # トークン化
    tokens = word_tokenize(text.lower())
    
    # ストップワードとlemmatizer
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
    # フィルタリング
    filtered_tokens = []
    for token in tokens:
        if (len(token) >= 3 and 
            token.isalpha() and 
            token not in stop_words and
            not token.isdigit()):
            filtered_tokens.append(lemmatizer.lemmatize(token))
    
    # 頻度カウント
    freq_counter = Counter(filtered_tokens)
    
    # 最小頻度以上のキーワードを抽出
    keywords = [word for word, freq in freq_counter.most_common(top_n) 
                if freq >= min_freq]
    
    return keywords

def analyze_references_keywords(references: List[dict], doi_cache: Dict[str, str]) -> List[str]:
    """参考文献から共通キーワードを分析"""
    all_text = []
    
    for ref in references:
        if isinstance(ref, dict):
            # タイトル情報
            title = ref.get('article-title', '')
            if title:
                all_text.append(title)
            
            # DOIからタイトル取得
            doi = ref.get('DOI', '').lower()
            if doi and doi in doi_cache:
                all_text.append(doi_cache[doi])
            
            # その他のテキスト情報
            unstructured = ref.get('unstructured', '')
            if unstructured:
                all_text.append(unstructured)
    
    # 全テキストを結合してキーワード抽出
    combined_text = ' '.join(all_text)
    return extract_text_keywords(combined_text, min_freq=2, top_n=15)

def enhance_json_with_keywords(json_path: str, doi_cache: Dict[str, str]) -> None:
    """JSONファイルにキーワード情報を追加"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 既存のキーワード情報
    existing_keywords = set()
    
    # 1. CrossrefデータからキーワードDecoding
    crossref_full = data.get('_crossref_full', {})
    crossref_keywords = extract_crossref_keywords(crossref_full)
    existing_keywords.update(crossref_keywords)
    
    # 2. タイトル・アブストラクトからキーワード抽出
    title_abstract = f"{data.get('title', '')} {data.get('abstract', '')}"
    content_keywords = extract_text_keywords(title_abstract, min_freq=1, top_n=10)
    
    # 3. 参考文献からキーワード推薦
    references = data.get('references', [])
    ref_keywords = analyze_references_keywords(references, doi_cache)
    
    # 4. 全キーワードを統合
    all_keywords = {
        'crossref_keywords': crossref_keywords,
        'content_keywords': content_keywords,
        'reference_keywords': ref_keywords,
        'combined_keywords': list(set(crossref_keywords + content_keywords + ref_keywords))
    }
    
    # JSONに追加
    data['keywords'] = all_keywords
    
    # ファイル保存
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Enhanced: {os.path.basename(json_path)} - {len(all_keywords['combined_keywords'])} keywords")

def main():
    """メイン処理"""
    print("キーワード拡張処理開始...")
    ensure_nltk_data()
    
    base = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(base, "JSON_folder")
    
    # DOIキャッシュを読み込み
    doi_cache_path = os.path.join(base, "doi_title_cache.json")
    doi_cache = {}
    if os.path.exists(doi_cache_path):
        with open(doi_cache_path, 'r', encoding='utf-8') as f:
            doi_cache = json.load(f)
    
    # 全JSONファイルを処理
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    for json_file in json_files:
        json_path = os.path.join(json_dir, json_file)
        try:
            enhance_json_with_keywords(json_path, doi_cache)
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    print(f"キーワード拡張完了: {len(json_files)} ファイル処理")

if __name__ == "__main__":
    main()