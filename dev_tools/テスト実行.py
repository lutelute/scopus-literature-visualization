#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト実行.py - 整理後システムの動作テスト
"""

import os
import subprocess
import sys

def main():
    print("[TEST] システム動作テスト")
    print("=" * 30)
    
    基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 既存ファイル確認
    重要ファイル = [
        "combine_scopus_csv.py",
        "scopus_doi_to_json.py", 
        "json2tag_ref_scopus_async.py",
        "enhance_keywords.py",
        "update_markdown_keywords.py",
        "add_yaml_metadata.py"
    ]
    
    print("📋 必要ファイル確認:")
    for ファイル in 重要ファイル:
        パス = os.path.join(基準ディレクトリ, ファイル)
        if os.path.exists(パス):
            print(f"  [OK] {ファイル}")
        else:
            print(f"  [NG] {ファイル} - 見つかりません")
    
    # フォルダ確認
    print(f"\n[DIR] フォルダ構成:")
    for フォルダ in ["core", "pdf_tools", "utils"]:
        パス = os.path.join(基準ディレクトリ, フォルダ)
        if os.path.exists(パス):
            ファイル数 = len(os.listdir(パス))
            print(f"  [OK] {フォルダ}/ ({ファイル数}件)")
        else:
            print(f"  [NG] {フォルダ}/ - 見つかりません")
    
    # 出力フォルダ確認
    出力フォルダ = ["JSON_folder", "md_folder", "PDF"]
    print(f"\n[DATA] 出力フォルダ:")
    for フォルダ in 出力フォルダ:
        パス = os.path.join(基準ディレクトリ, フォルダ)
        if os.path.exists(パス):
            ファイル数 = len(os.listdir(パス))
            print(f"  [DIR] {フォルダ}/ ({ファイル数}件)")
        else:
            print(f"  [DIR] {フォルダ}/ (未作成)")
    
    print(f"\n[TARGET] テスト完了!")
    print(f"次の手順で実行してください:")
    print(f"1. python3 core/scopus解析.py")
    print(f"2. python3 pdf_tools/PDF取得.py")

if __name__ == "__main__":
    main()