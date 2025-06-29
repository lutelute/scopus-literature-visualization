#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scopus解析.py - Scopus文献データ解析メインスクリプト
"""

import os
import subprocess
import sys
import time

def スクリプト実行(スクリプト名: str, 説明: str, 基準ディレクトリ: str) -> bool:
    """スクリプトを実行して結果を返す"""
    print(f"\n🚀 {説明}を開始...")
    print(f"📄 実行ファイル: {スクリプト名}")
    
    try:
        開始時間 = time.time()
        結果 = subprocess.run([sys.executable, スクリプト名], 
                              capture_output=True, 
                              text=True, 
                              cwd=基準ディレクトリ)
        
        実行時間 = time.time() - 開始時間
        
        if 結果.returncode == 0:
            print(f"✅ {説明} 完了 ({実行時間:.1f}秒)")
            if 結果.stdout:
                出力行 = 結果.stdout.split('\n')
                重要行 = [行 for 行 in 出力行 if any(マーク in 行 for マーク in ['✅', '📊', '📁', '完了', '成功'])]
                for 行 in 重要行[-5:]:  # 最後の5つの重要メッセージ
                    if 行.strip():
                        print(f"  {行}")
            return True
        else:
            print(f"❌ {説明} でエラーが発生しました (コード: {結果.returncode})")
            if 結果.stderr:
                print("⚠️ エラー詳細:")
                print(結果.stderr[-500:])
            return False
            
    except Exception as e:
        print(f"❌ スクリプト実行エラー: {e}")
        return False

def ファイル数確認(ディレクトリ: str, 拡張子: str) -> int:
    """指定ディレクトリ内の指定拡張子ファイル数を取得"""
    if os.path.exists(ディレクトリ):
        return len([f for f in os.listdir(ディレクトリ) if f.endswith(拡張子)])
    return 0

def main():
    """メイン処理"""
    print("🎯 Scopus文献可視化システム")
    print("=" * 50)
    
    基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(基準ディレクトリ)
    
    # 現在の状況確認
    json数 = ファイル数確認(os.path.join(基準ディレクトリ, "JSON_folder"), '.json')
    md数 = ファイル数確認(os.path.join(基準ディレクトリ, "md_folder"), '.md')
    pdf数 = ファイル数確認(os.path.join(基準ディレクトリ, "PDF"), '.pdf')
    
    print(f"📊 現在のファイル数:")
    print(f"   📁 JSONファイル: {json数}件")
    print(f"   📝 Markdownファイル: {md数}件")
    print(f"   📄 PDFファイル: {pdf数}件")
    
    # メニュー表示
    print("\n📋 実行オプション:")
    print("   1. 完全実行（CSV結合→DOI取得→Markdown生成→キーワード→YAML）")
    print("   2. DOI情報のみ更新")
    print("   3. Markdownのみ再生成")
    print("   4. キーワード分析のみ")
    print("   5. YAML メタデータのみ")
    print("   0. 終了")
    
    while True:
        選択 = input("\n選択してください (0-5): ").strip()
        
        if 選択 == '0':
            print("👋 終了します。")
            return
        
        elif 選択 == '1':
            print("\n🚀 完全実行を開始します...")
            全開始時間 = time.time()
            
            パイプライン = [
                ("combine_scopus_csv.py", "CSVファイル結合"),
                ("scopus_doi_to_json.py", "DOI情報完全取得"),
                ("json2tag_ref_scopus_async.py", "Markdown生成・参考文献解決"),
                ("enhance_keywords.py", "キーワード分析・抽出"),
                ("update_markdown_keywords.py", "Markdownキーワード更新"),
                ("add_yaml_metadata.py", "YAMLメタデータ追加"),
            ]
            
            成功数 = 0
            for スクリプト, 説明 in パイプライン:
                if スクリプト実行(スクリプト, 説明, 基準ディレクトリ):
                    成功数 += 1
                else:
                    継続 = input(f"⚠️ エラーが発生しました。続行しますか？ (y/n): ").lower()
                    if 継続 != 'y':
                        break
                print("-" * 30)
            
            全実行時間 = time.time() - 全開始時間
            
            # 最終結果
            最終json数 = ファイル数確認(os.path.join(基準ディレクトリ, "JSON_folder"), '.json')
            最終md数 = ファイル数確認(os.path.join(基準ディレクトリ, "md_folder"), '.md')
            
            print(f"\n🎉 完全実行完了!")
            print(f"📊 実行成功: {成功数}/{len(パイプライン)} ステップ")
            print(f"⏱️ 総実行時間: {全実行時間:.1f}秒")
            print(f"📁 生成ファイル数: JSON {最終json数}件, Markdown {最終md数}件")
            print(f"\n📋 次は PDF取得コマンド で論文PDFを取得できます")
            break
        
        elif 選択 == '2':
            スクリプト実行("scopus_doi_to_json.py", "DOI情報完全取得", 基準ディレクトリ)
            break
        
        elif 選択 == '3':
            スクリプト実行("json2tag_ref_scopus_async.py", "Markdown生成・参考文献解決", 基準ディレクトリ)
            break
        
        elif 選択 == '4':
            if スクリプト実行("enhance_keywords.py", "キーワード分析・抽出", 基準ディレクトリ):
                スクリプト実行("update_markdown_keywords.py", "Markdownキーワード更新", 基準ディレクトリ)
            break
        
        elif 選択 == '5':
            スクリプト実行("add_yaml_metadata.py", "YAMLメタデータ追加", 基準ディレクトリ)
            break
        
        else:
            print("❌ 無効な選択です。0-5を入力してください。")

if __name__ == "__main__":
    main()