#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自動実行.py - Scopus文献可視化システム 完全自動化スクリプト
ワンコマンドで全処理を実行します
"""

import os
import subprocess
import sys
import time
import importlib.util

def banner():
    """バナー表示"""
    print("🚀 Scopus文献可視化システム - 全自動実行")
    print("=" * 60)
    print("📋 実行内容:")
    print("   1️⃣  環境チェック・依存関係確認")
    print("   2️⃣  CSVファイル結合")
    print("   3️⃣  DOI完全情報取得")
    print("   4️⃣  Markdown生成・参考文献解決")
    print("   5️⃣  キーワード分析・抽出")
    print("   6️⃣  YAMLメタデータ追加")
    print("   💡 PDF取得は別途実行: python3 pdf_tools/PDF取得.py")
    print("=" * 60)

def 依存関係チェック():
    """必須パッケージの確認"""
    print("\n📦 依存関係をチェック中...")
    必須パッケージ = ['pandas', 'requests', 'requests_cache', 'tqdm']
    未インストール = []
    
    for パッケージ名 in 必須パッケージ:
        spec = importlib.util.find_spec(パッケージ名)
        if spec is None:
            未インストール.append(パッケージ名)
    
    if 未インストール:
        print(f"❌ 必須パッケージが不足: {', '.join(未インストール)}")
        print("🔧 解決方法:")
        print("   仮想環境を使用: source .venv/bin/activate")
        print("   または手動インストール: pip install pandas requests requests_cache tqdm")
        return False
    else:
        print("✅ 必須パッケージは全てインストール済み")
        return True

def オプションライブラリチェック():
    """オプションライブラリの確認と自動インストール提案"""
    print("\n🔍 拡張機能チェック中...")
    
    オプションパッケージ = {
        'aiohttp': {
            'name': 'aiohttp + async_timeout',
            'description': '高速並列処理機能（DOI解決が3倍高速化）',
            'packages': ['aiohttp', 'async_timeout']
        },
        'nltk': {
            'name': 'NLTK',
            'description': '高度なキーワード分析機能（より精密な分析）',
            'packages': ['nltk']
        }
    }
    
    未インストール拡張 = {}
    for key, info in オプションパッケージ.items():
        for pkg in info['packages']:
            spec = importlib.util.find_spec(pkg)
            if spec is None:
                if key not in 未インストール拡張:
                    未インストール拡張[key] = info
                break
    
    if not 未インストール拡張:
        print("✅ 全ての拡張機能が利用可能です")
        return True
    
    print(f"💡 利用可能な拡張機能:")
    for key, info in 未インストール拡張.items():
        print(f"   🚀 {info['name']}: {info['description']}")
    
    print(f"\n⚙️  これらの拡張機能を仮想環境にインストールしますか？")
    print(f"   (処理速度と分析品質が大幅に向上します)")
    
    try:
        回答 = input("拡張機能をインストールしますか？ (y/n): ").lower().strip()
        if 回答 in ['y', 'yes']:
            return 拡張機能インストール(未インストール拡張)
        else:
            print("⏭️  基本機能のみで実行します")
            return True
    except KeyboardInterrupt:
        print("\n⏹️  中断されました")
        return False

def 拡張機能インストール(未インストール拡張):
    """拡張機能の自動インストール"""
    print(f"\n🔧 拡張機能をインストール中...")
    
    インストール成功 = True
    for key, info in 未インストール拡張.items():
        print(f"\n📦 {info['name']} をインストール中...")
        
        try:
            インストールパッケージ = ' '.join(info['packages'])
            結果 = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '--quiet', '--disable-pip-version-check'
            ] + info['packages'], 
            capture_output=True, text=True, check=True)
            
            print(f"✅ {info['name']} インストール完了")
            
            # NLTKの場合、追加リソースも自動ダウンロード
            if key == 'nltk':
                print("📚 NLTK追加リソースをダウンロード中...")
                try:
                    import nltk
                    nltk.download('punkt', quiet=True)
                    nltk.download('averaged_perceptron_tagger_eng', quiet=True)
                    nltk.download('wordnet', quiet=True)
                    print("✅ NLTK追加リソース完了")
                except Exception as e:
                    print(f"⚠️  NLTK追加リソースの一部でエラー: {e}")
        
        except subprocess.CalledProcessError as e:
            print(f"❌ {info['name']} インストール失敗: {e}")
            インストール成功 = False
        except Exception as e:
            print(f"❌ {info['name']} インストールエラー: {e}")
            インストール成功 = False
    
    if インストール成功:
        print(f"\n🎉 全拡張機能のインストールが完了しました！")
        print(f"⚡ 処理速度と分析品質が向上します")
    else:
        print(f"\n⚠️  一部の拡張機能でエラーが発生しました")
        print(f"💡 基本機能で処理を続行します")
    
    return True

def CSV確認():
    """CSVファイルの存在確認"""
    print("\n📄 CSVファイルをチェック中...")
    現在ディレクトリ = os.getcwd()
    csv_files = [f for f in os.listdir(現在ディレクトリ) if f.endswith('.csv') and 'scopus' in f.lower()]
    
    if not csv_files:
        print("❌ Scopus CSVファイルが見つかりません")
        print("🔧 解決方法:")
        print("   1. ScopusからエクスポートしたCSVファイルを作業フォルダに配置")
        print("   2. ファイル名に'scopus'を含める（例: scopus_export.csv）")
        return False
    else:
        print(f"✅ {len(csv_files)}個のCSVファイルを発見:")
        for f in csv_files:
            print(f"   📄 {f}")
        return True

def スクリプト実行(スクリプト名, 説明):
    """スクリプトを実行"""
    print(f"\n🔄 {説明}を実行中...")
    print(f"📄 {スクリプト名}")
    
    try:
        開始時間 = time.time()
        結果 = subprocess.run([sys.executable, スクリプト名], check=True)
        実行時間 = time.time() - 開始時間
        print(f"✅ {説明} 完了 ({実行時間:.1f}秒)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {説明} でエラー発生 (コード: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ {説明} で予期しないエラー: {e}")
        return False

def main():
    """メイン処理"""
    banner()
    
    全開始時間 = time.time()
    成功ステップ = 0
    総ステップ = 6
    
    # 1. 環境チェック
    print(f"\n{'='*20} 1️⃣  環境チェック {'='*20}")
    if not 依存関係チェック():
        print("\n❌ 必須パッケージが不足しています。上記の解決方法を試してください。")
        return
    
    if not オプションライブラリチェック():
        print("\n❌ 拡張機能チェックで問題が発生しました。")
        return
    
    if not CSV確認():
        print("\n❌ CSVファイルチェックに失敗しました。上記の解決方法を試してください。")
        return
    
    成功ステップ += 1
    
    # パイプライン実行
    パイプライン = [
        ("combine_scopus_csv.py", "2️⃣  CSVファイル結合"),
        ("scopus_doi_to_json.py", "3️⃣  DOI完全情報取得"),
        ("json2tag_ref_scopus_async.py", "4️⃣  Markdown生成・参考文献解決"),
        ("enhance_keywords.py", "5️⃣  キーワード分析・抽出"),
        ("add_yaml_metadata.py", "6️⃣  YAMLメタデータ追加"),
    ]
    
    for スクリプト, 説明 in パイプライン:
        print(f"\n{'='*50}")
        if スクリプト実行(スクリプト, 説明):
            成功ステップ += 1
        else:
            print(f"\n❌ {説明} でエラーが発生しましたが処理を続行します")
            time.sleep(1)
    
    # 最終結果
    全実行時間 = time.time() - 全開始時間
    print(f"\n{'='*60}")
    print("🎉 全自動実行完了!")
    print(f"📊 成功ステップ: {成功ステップ}/{総ステップ}")
    print(f"⏱️  総実行時間: {全実行時間/60:.1f}分")
    
    # 生成ファイル確認
    json_count = len([f for f in os.listdir("JSON_folder") if f.endswith(".json")]) if os.path.exists("JSON_folder") else 0
    md_count = len([f for f in os.listdir("md_folder") if f.endswith(".md")]) if os.path.exists("md_folder") else 0
    pdf_count = len([f for f in os.listdir("PDF") if f.endswith(".pdf")]) if os.path.exists("PDF") else 0
    
    print(f"\n📁 生成ファイル数:")
    print(f"   📄 JSONファイル: {json_count}件")
    print(f"   📝 Markdownファイル: {md_count}件")
    print(f"   📋 PDFファイル: {pdf_count}件")
    
    if 成功ステップ == 総ステップ:
        print(f"\n🎯 完全成功! 学術文献データベースが完成しました")
        print(f"📂 md_folder/ で Markdown ファイルを確認してください")
        print(f"\n📋 次のステップ:")
        print(f"   💾 PDF取得: python3 pdf_tools/PDF取得.py")
        print(f"   📖 Markdownファイルを確認: md_folder/")
        print(f"   🔍 JSONデータを確認: JSON_folder/")
    else:
        print(f"\n⚠️  一部ステップでエラーが発生しました")
        print(f"📋 個別実行で問題を解決してください: python3 core/scopus解析.py")

if __name__ == "__main__":
    main()