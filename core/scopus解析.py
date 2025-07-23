#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scopus解析.py - Scopus文献データ解析メインスクリプト
"""

import os
import subprocess
import sys
import time
import importlib.util

def 依存関係チェック():
    """必須パッケージの確認とインストール"""
    必須パッケージ = ['pandas', 'requests', 'requests_cache', 'tqdm']
    未インストール = []
    
    for パッケージ名 in 必須パッケージ:
        spec = importlib.util.find_spec(パッケージ名)
        if spec is None:
            未インストール.append(パッケージ名)
    
    if 未インストール:
        print(f"[WARN]  必須パッケージが不足しています: {', '.join(未インストール)}")
        print(f"[PKG] 自動インストールを実行しますか？ (y/n): ", end="")
        
        try:
            回答 = input().lower()
            if 回答 in ['y', 'yes']:
                print(f"[PKG] パッケージインストール中...")
                try:
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install'
                    ] + 未インストール)
                    print(f"[OK] インストール完了: {', '.join(未インストール)}")
                    return True
                except subprocess.CalledProcessError:
                    print(f"[NG] 自動インストール失敗")
                    print(f"手動実行してください: pip install {' '.join(未インストール)}")
                    return False
            else:
                print(f"⏭️  パッケージ不足のまま続行します（エラーが発生する可能性があります）")
                return False
        except KeyboardInterrupt:
            print(f"\n⏹️  中断されました")
            return False
    else:
        print(f"[OK] 必須パッケージは全てインストール済みです")
        return True

def スクリプト実行(スクリプト名: str, 説明: str, 基準ディレクトリ: str) -> bool:
    """スクリプトを実行して結果を返す"""
    print(f"\n[START] {説明}を開始...")
    print(f"[FILE] 実行ファイル: {スクリプト名}")
    
    try:
        開始時間 = time.time()
        
        # リアルタイム進捗表示の場合は capture_output=False を使用
        if スクリプト名 in ["json2tag_ref_scopus_async.py", "scopus_doi_to_json.py"]:
            print(f"[DATA] リアルタイム進捗表示モード")
            結果 = subprocess.run([sys.executable, スクリプト名], 
                                  cwd=基準ディレクトリ)
            実行時間 = time.time() - 開始時間
            
            if 結果.returncode == 0:
                print(f"[OK] {説明} 完了 ({実行時間:.1f}秒)")
                return True
            else:
                print(f"[NG] {説明} でエラーが発生しました (コード: {結果.returncode})")
                return False
        else:
            # その他のスクリプトは従来通り
            結果 = subprocess.run([sys.executable, スクリプト名], 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=基準ディレクトリ)
            
            実行時間 = time.time() - 開始時間
            
            if 結果.returncode == 0:
                print(f"[OK] {説明} 完了 ({実行時間:.1f}秒)")
                if 結果.stdout:
                    出力行 = 結果.stdout.split('\n')
                    重要行 = [行 for 行 in 出力行 if any(マーク in 行 for マーク in ['[OK]', '[DATA]', '[DIR]', '完了', '成功'])]
                    for 行 in 重要行[-5:]:  # 最後の5つの重要メッセージ
                        if 行.strip():
                            print(f"  {行}")
                return True
            else:
                print(f"[NG] {説明} でエラーが発生しました (コード: {結果.returncode})")
                if 結果.stderr:
                    print("[WARN] エラー詳細:")
                    print(結果.stderr[-500:])
                return False
            
    except Exception as e:
        print(f"[NG] スクリプト実行エラー: {e}")
        return False

def ファイル数確認(ディレクトリ: str, 拡張子: str) -> int:
    """指定ディレクトリ内の指定拡張子ファイル数を取得"""
    if os.path.exists(ディレクトリ):
        return len([f for f in os.listdir(ディレクトリ) if f.endswith(拡張子)])
    return 0

def main():
    """メイン処理"""
    print("[TARGET] Scopus文献可視化システム")
    print("=" * 50)
    
    基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(基準ディレクトリ)
    
    # 現在の状況確認
    json数 = ファイル数確認(os.path.join(基準ディレクトリ, "JSON_folder"), '.json')
    md数 = ファイル数確認(os.path.join(基準ディレクトリ, "md_folder"), '.md')
    pdf数 = ファイル数確認(os.path.join(基準ディレクトリ, "PDF"), '.pdf')
    
    print(f"[DATA] 現在のファイル数:")
    print(f"   [DIR] JSONファイル: {json数}件")
    print(f"   📝 Markdownファイル: {md数}件")
    print(f"   [FILE] PDFファイル: {pdf数}件")
    
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
            print("\n[START] 完全実行を開始します...")
            
            # 依存関係チェック
            print("\n[PKG] 依存関係をチェック中...")
            if not 依存関係チェック():
                print("[NG] 依存関係エラーにより中断します")
                break
            
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
                    継続 = input(f"[WARN] エラーが発生しました。続行しますか？ (y/n): ").lower()
                    if 継続 != 'y':
                        break
                print("-" * 30)
            
            全実行時間 = time.time() - 全開始時間
            
            # 最終結果
            最終json数 = ファイル数確認(os.path.join(基準ディレクトリ, "JSON_folder"), '.json')
            最終md数 = ファイル数確認(os.path.join(基準ディレクトリ, "md_folder"), '.md')
            
            print(f"\n[DONE] 完全実行完了!")
            print(f"[DATA] 実行成功: {成功数}/{len(パイプライン)} ステップ")
            print(f"⏱️ 総実行時間: {全実行時間:.1f}秒")
            print(f"[DIR] 生成ファイル数: JSON {最終json数}件, Markdown {最終md数}件")
            print(f"\n📋 次は PDF取得コマンド で論文PDFを取得できます")
            break
        
        elif 選択 == '2':
            print("\n[PKG] 依存関係をチェック中...")
            if 依存関係チェック():
                スクリプト実行("scopus_doi_to_json.py", "DOI情報完全取得", 基準ディレクトリ)
            break
        
        elif 選択 == '3':
            print("\n[PKG] 依存関係をチェック中...")
            if 依存関係チェック():
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
            print("[NG] 無効な選択です。0-5を入力してください。")

if __name__ == "__main__":
    main()