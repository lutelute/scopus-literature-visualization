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
import venv

# メール通知機能のインポート（オプション）
try:
    from utils.email_notification import (
        メール設定状況確認, メール設定セットアップ, 処理完了通知送信
    )
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

def CI環境チェック() -> bool:
    """CI環境かどうかをチェック"""
    ci_環境変数 = ['CI', 'GITHUB_ACTIONS', 'TRAVIS', 'CIRCLECI', 'JENKINS_URL']
    return any(os.getenv(var) for var in ci_環境変数)

def 安全なinput(プロンプト: str, デフォルト: str = "n", CI環境: bool = False) -> str:
    """CI環境対応の安全なinput関数"""
    if CI環境:
        print(f"{プロンプト}（CI環境のため自動選択: {デフォルト}）")
        return デフォルト
    try:
        return input(プロンプト).lower().strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n入力が検出されませんでした。デフォルト値を使用: {デフォルト}")
        return デフォルト

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
    print("   7️⃣  オープンアクセスPDF取得（オプション）")
    print("=" * 60)

def 仮想環境チェック():
    """仮想環境の状況を確認"""
    print("\n🔍 実行環境をチェック中...")
    
    # 仮想環境がアクティブかチェック
    is_venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if os.path.exists(".venv"):
        if is_venv_active:
            print("✅ 仮想環境がアクティブです")
            return True
        else:
            print("❌ 仮想環境が存在しますが、アクティブではありません")
            print("🔧 解決方法:")
            print("   source .venv/bin/activate && python3 全自動実行.py")
            print("   または setup.py を先に実行してください")
            return False
    else:
        print("⚠️  仮想環境が見つかりません")
        print("🔧 自動で setup.py を実行して仮想環境を作成します...")
        
        try:
            print("\n🔧 setup.py を実行中...")
            結果 = subprocess.run([sys.executable, "setup.py"], check=True)
            print("✅ setup.py 実行完了")
            print("⚠️  仮想環境をアクティベートしてから再実行してください:")
            print("source .venv/bin/activate && python3 全自動実行.py")
            print("\n💡 次回からは以下のコマンドで簡単実行:")
            print("   source .venv/bin/activate && python3 全自動実行.py")
            return False
        except subprocess.CalledProcessError:
            print("❌ setup.py 実行失敗")
            print("🔧 手動で実行してください: python3 setup.py")
            print("⚠️  それでも続行しますか？（仮想環境なし・非推奨）")
            try:
                ci環境 = CI環境チェック()
                回答 = 安全なinput("仮想環境なしで続行しますか？ (y/n): ", "n", ci環境)
                if 回答 in ['y', 'yes']:
                    print("⏭️  仮想環境なしで実行します（非推奨）")
                    return True
                else:
                    print("⏹️  処理を中断します")
                    return False
            except KeyboardInterrupt:
                print("\n⏹️  中断されました")
                return False
        except KeyboardInterrupt:
            print("\n⏹️  中断されました")
            return False

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
        ci環境 = CI環境チェック()
        回答 = 安全なinput("拡張機能をインストールしますか？ (y/n): ", "y", ci環境)
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

def PDF取得実行():
    """PDF取得を実行（オプション）"""
    print(f"\n🔄 オープンアクセスPDF取得を実行中...")
    print(f"📄 download_open_access_pdfs_fast_stdlib.py")
    
    try:
        開始時間 = time.time()
        スクリプトパス = os.path.join("pdf_tools", "download_open_access_pdfs_fast_stdlib.py")
        結果 = subprocess.run([sys.executable, スクリプトパス], check=True)
        実行時間 = time.time() - 開始時間
        print(f"✅ オープンアクセスPDF取得 完了 ({実行時間:.1f}秒)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PDF取得でエラー発生 (コード: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ PDF取得で予期しないエラー: {e}")
        return False

def PDF数確認(pdf_dir="PDF"):
    """PDFファイル数を確認"""
    if os.path.exists(pdf_dir):
        return len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    return 0

def メール通知オプション確認():
    """メール通知オプションの確認と設定"""
    if not EMAIL_AVAILABLE:
        return False
    
    print(f"\n💡 オプション: 処理完了時のメール通知")
    
    # 現在の設定状況確認
    設定済み, 状況 = メール設定状況確認()
    print(f"📧 メール設定: {状況}")
    
    ci環境 = CI環境チェック()
    
    if 設定済み:
        try:
            回答 = 安全なinput("完了時にメール通知を送信しますか？ (y/n): ", "n", ci環境)
            return 回答 in ['y', 'yes']
        except KeyboardInterrupt:
            return False
    else:
        print("📋 メール通知を有効にするには設定が必要です")
        if ci環境:
            print("CI環境のためメール設定をスキップします")
            return False
        try:
            回答 = 安全なinput("メール設定をセットアップしますか？ (y/n): ", "n", ci環境)
            if 回答 in ['y', 'yes']:
                if メール設定セットアップ():
                    print("✅ メール設定完了！完了時に通知を送信します")
                    return True
                else:
                    print("❌ メール設定に失敗しました")
            return False
        except KeyboardInterrupt:
            return False

def main():
    """メイン処理"""
    banner()
    
    # CI環境チェック
    ci環境 = CI環境チェック()
    if ci環境:
        print("🤖 CI環境を検出 - 自動モードで実行します")
    
    全開始時間 = time.time()
    成功ステップ = 0
    総ステップ = 6
    
    # 1. 環境チェック
    print(f"\n{'='*20} 1️⃣  環境チェック {'='*20}")
    
    # 仮想環境チェック
    if not 仮想環境チェック():
        print("\n❌ 実行環境のセットアップが必要です。")
        return
    
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
    
    # メール通知オプション確認
    メール通知有効 = メール通知オプション確認()
    
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
    print("🎉 メイン処理完了!")
    print(f"📊 成功ステップ: {成功ステップ}/{総ステップ}")
    print(f"⏱️  総実行時間: {全実行時間/60:.1f}分")
    
    # 生成ファイル確認
    json_count = len([f for f in os.listdir("JSON_folder") if f.endswith(".json")]) if os.path.exists("JSON_folder") else 0
    md_count = len([f for f in os.listdir("md_folder") if f.endswith(".md")]) if os.path.exists("md_folder") else 0
    初期pdf_count = PDF数確認()
    
    print(f"\n📁 生成ファイル数:")
    print(f"   📄 JSONファイル: {json_count}件")
    print(f"   📝 Markdownファイル: {md_count}件")
    print(f"   📋 PDFファイル: {初期pdf_count}件")
    
    if 成功ステップ == 総ステップ:
        print(f"\n🎯 メイン処理完了! 学術文献データベースが完成しました")
        print(f"📂 md_folder/ で Markdown ファイルを確認してください")
        
        # PDF取得オプション
        print(f"\n💡 オプション: オープンアクセス論文のPDF取得")
        print(f"   (高速並列処理 - 最大8スレッド)")
        
        try:
            回答 = 安全なinput("\nPDF取得を実行しますか？ (y/n): ", "n", ci環境)
            if 回答 in ['y', 'yes']:
                print(f"\n{'='*50}")
                print("🔄 7️⃣  オープンアクセスPDF取得")
                print("=" * 50)
                
                pdf_結果 = PDF取得実行()
                if pdf_結果:
                    最終pdf_count = PDF数確認()
                    新規pdf_count = 最終pdf_count - 初期pdf_count
                    print(f"\n📈 PDF取得結果:")
                    print(f"   📥 新規PDF取得: {新規pdf_count}件")
                    print(f"   📁 総PDF数: {最終pdf_count}件")
                    
                    print(f"\n🎉 全処理完了! 完全な学術文献データベースが完成しました")
                    print(f"📂 PDF付きMarkdownファイル: md_folder/")
                    print(f"📄 PDFファイル: PDF/")
                else:
                    print(f"\n⚠️  PDF取得でエラーが発生しましたが、メイン処理は完了しています")
                    最終pdf_count = 初期pdf_count
                    新規pdf_count = 0
            else:
                print(f"\n⏭️  PDF取得をスキップしました")
                print(f"💡 後でPDF取得する場合: python3 pdf_tools/PDF取得.py")
                pdf_結果 = False
                最終pdf_count = 初期pdf_count
                新規pdf_count = 0
        except KeyboardInterrupt:
            print(f"\n⏹️  中断されました")
            pdf_結果 = False
            最終pdf_count = 初期pdf_count
            新規pdf_count = 0
        
        print(f"\n📋 最終結果:")
        print(f"   📖 Markdownファイル確認: md_folder/")
        print(f"   🔍 JSONデータ確認: JSON_folder/")
        print(f"   📄 PDFファイル確認: PDF/")
        
        # メール通知送信
        if メール通知有効:
            print(f"\n📧 完了通知メールを送信中...")
            生成ファイル数 = {
                'json': json_count,
                'md': md_count,
                'pdf': 最終pdf_count if 'pdf_結果' in locals() and pdf_結果 else 初期pdf_count
            }
            
            pdf取得結果 = None
            if 'pdf_結果' in locals() and pdf_結果:
                pdf取得結果 = {
                    '新規': 新規pdf_count,
                    '総数': 最終pdf_count,
                    '速度': 0  # 速度情報は取得が複雑なため省略
                }
            
            if 処理完了通知送信(成功ステップ, 総ステップ, 全実行時間, 生成ファイル数, pdf取得結果):
                print("✅ 完了通知メール送信完了")
            else:
                print("⚠️  メール送信に失敗しました（処理は正常完了）")
    else:
        print(f"\n⚠️  一部ステップでエラーが発生しました")
        print(f"📋 個別実行で問題を解決してください: python3 core/scopus解析.py")
        
        # エラー時もメール通知送信
        if メール通知有効:
            print(f"\n📧 エラー通知メールを送信中...")
            生成ファイル数 = {
                'json': json_count,
                'md': md_count,
                'pdf': 初期pdf_count
            }
            
            if 処理完了通知送信(成功ステップ, 総ステップ, 全実行時間, 生成ファイル数):
                print("✅ エラー通知メール送信完了")
            else:
                print("⚠️  メール送信に失敗しました")

if __name__ == "__main__":
    main()