#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
クリーンアップ.py - 自動生成ファイル削除とフォルダ整理
"""

import os
import shutil
import glob

def ファイル削除確認(ファイルパス: str) -> bool:
    """ファイル削除の確認"""
    if os.path.exists(ファイルパス):
        print(f"  🗑️ {os.path.basename(ファイルパス)}")
        return True
    return False

def フォルダ削除確認(フォルダパス: str) -> int:
    """フォルダ内ファイル数確認"""
    if os.path.exists(フォルダパス):
        ファイル数 = len([f for f in os.listdir(フォルダパス) if os.path.isfile(os.path.join(フォルダパス, f))])
        if ファイル数 > 0:
            print(f"  [DIR] {os.path.basename(フォルダパス)}/ ({ファイル数}件)")
        return ファイル数
    return 0

def main():
    """クリーンアップメイン処理"""
    print("🧹 自動生成ファイル クリーンアップツール")
    print("=" * 45)
    
    基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 削除対象ファイル・フォルダの確認
    削除対象 = {
        "キャッシュファイル": [
            "crossref_cache.sqlite",
            "doi_title_cache.json",
            "error_log.txt"
        ],
        "出力フォルダ": [
            "JSON_folder",
            "md_folder",
            "PDF"
        ],
        "一時ファイル": [
            "scopus_combined.csv"
        ]
    }
    
    print("[INFO] 削除対象ファイルを確認中...")
    
    削除ファイル数 = 0
    削除フォルダ数 = 0
    
    for カテゴリ, ファイル一覧 in 削除対象.items():
        print(f"\n📋 {カテゴリ}:")
        
        for ファイル名 in ファイル一覧:
            パス = os.path.join(基準ディレクトリ, ファイル名)
            
            if os.path.isfile(パス):
                if ファイル削除確認(パス):
                    削除ファイル数 += 1
            elif os.path.isdir(パス):
                内部ファイル数 = フォルダ削除確認(パス)
                if 内部ファイル数 > 0:
                    削除フォルダ数 += 1
                    削除ファイル数 += 内部ファイル数
    
    if 削除ファイル数 == 0:
        print("\n[OK] 削除対象ファイルは見つかりませんでした。")
        return
    
    print(f"\n[DATA] 削除予定:")
    print(f"   [FILE] ファイル数: {削除ファイル数}件")
    print(f"   [DIR] フォルダ数: {削除フォルダ数}件")
    
    # 削除確認
    確認 = input("\n❓ これらのファイルを削除しますか？ (y/n): ").lower()
    
    if 確認 != 'y':
        print("[NG] クリーンアップをキャンセルしました。")
        return
    
    print("\n🧹 クリーンアップを実行中...")
    
    削除成功数 = 0
    削除エラー数 = 0
    
    for カテゴリ, ファイル一覧 in 削除対象.items():
        for ファイル名 in ファイル一覧:
            パス = os.path.join(基準ディレクトリ, ファイル名)
            
            try:
                if os.path.isfile(パス):
                    os.remove(パス)
                    print(f"  [OK] 削除: {ファイル名}")
                    削除成功数 += 1
                elif os.path.isdir(パス):
                    shutil.rmtree(パス)
                    print(f"  [OK] 削除: {ファイル名}/")
                    削除成功数 += 1
            except Exception as e:
                print(f"  [NG] エラー: {ファイル名} ({e})")
                削除エラー数 += 1
    
    print(f"\n[DONE] クリーンアップ完了!")
    print(f"[DATA] 削除成功: {削除成功数}件")
    if 削除エラー数 > 0:
        print(f"[WARN] 削除エラー: {削除エラー数}件")
    
    print(f"\n📋 次の手順:")
    print(f"   1. scopus解析.py を実行してMarkdownファイルを生成")
    print(f"   2. PDF取得.py を実行して論文PDFを取得")

if __name__ == "__main__":
    main()