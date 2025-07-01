#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_improved.py - Scopus文献可視化システム 改良版自動セットアップスクリプト
仮想環境作成からパッケージインストールまでを一回で完了
"""

import os
import sys
import subprocess
import importlib.util
import venv
import platform
import time

def CI環境チェック() -> bool:
    """CI環境かどうかをチェック"""
    ci_環境変数 = ['CI', 'GITHUB_ACTIONS', 'TRAVIS', 'CIRCLECI', 'JENKINS_URL']
    return any(os.getenv(var) for var in ci_環境変数)

def 安全なinput(プロンプト: str, デフォルト: str = "y", CI環境: bool = False) -> str:
    """CI環境対応の安全なinput関数"""
    if CI環境:
        print(f"{プロンプト}（CI環境のため自動選択: {デフォルト}）")
        return デフォルト
    try:
        return input(プロンプト).lower().strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n入力が検出されませんでした。デフォルト値を使用: {デフォルト}")
        return デフォルト

def パッケージ確認(パッケージ名: str) -> bool:
    """パッケージがインストールされているかチェック"""
    spec = importlib.util.find_spec(パッケージ名)
    return spec is not None

def 仮想環境Python実行ファイル取得(仮想環境パス: str) -> str:
    """OS別の仮想環境内Python実行ファイルパスを取得"""
    if platform.system() == "Windows":
        return os.path.join(仮想環境パス, "Scripts", "python.exe")
    else:
        return os.path.join(仮想環境パス, "bin", "python")

def 仮想環境pip実行ファイル取得(仮想環境パス: str) -> str:
    """OS別の仮想環境内pip実行ファイルパスを取得"""
    if platform.system() == "Windows":
        return os.path.join(仮想環境パス, "Scripts", "pip.exe")
    else:
        return os.path.join(仮想環境パス, "bin", "pip")

def 仮想環境アクティベーションコマンド取得(仮想環境パス: str) -> str:
    """OS別の仮想環境アクティベーションコマンドを取得"""
    if platform.system() == "Windows":
        return f"{仮想環境パス}\\Scripts\\activate"
    else:
        return f"source {仮想環境パス}/bin/activate"

def 仮想環境実行コマンド生成(仮想環境パス: str, コマンド: str) -> str:
    """OS別の仮想環境実行コマンドを生成"""
    if platform.system() == "Windows":
        return f"{仮想環境パス}\\Scripts\\activate && {コマンド}"
    else:
        return f"source {仮想環境パス}/bin/activate && {コマンド}"

def 仮想環境作成および設定(仮想環境パス: str = ".venv", 自動実行: bool = False) -> bool:
    """仮想環境の作成と必須パッケージの自動インストール"""
    
    print("[INFO] 仮想環境をチェック中...")
    
    # 仮想環境の存在チェック
    if os.path.exists(仮想環境パス):
        print("[OK] 仮想環境が既に存在します")
        venv_python = 仮想環境Python実行ファイル取得(仮想環境パス)
        
        if os.path.exists(venv_python):
            print(f"[OK] 仮想環境のPython実行ファイル確認: {venv_python}")
        else:
            print(f"[NG] 仮想環境が破損している可能性があります。再作成します...")
            return 仮想環境再作成(仮想環境パス)
    else:
        print("[PKG] 仮想環境が見つかりません。作成しますか？")
        print("   (推奨: パッケージの依存関係競合を避けるため)")
        
        # CI環境チェック
        ci環境 = CI環境チェック()
        if ci環境:
            print("🤖 CI環境を検出 - 自動実行モードで動作します")
            自動実行 = True
        
        if 自動実行:
            print("自動実行モード: 仮想環境を作成します")
            return 仮想環境新規作成(仮想環境パス)
        
        回答 = 安全なinput("仮想環境を作成しますか？ (y/n): ", "y", ci環境)
        if 回答 in ['y', 'yes']:
            return 仮想環境新規作成(仮想環境パス)
        else:
            print("⏭️  システム環境で実行します（非推奨）")
            return システム環境パッケージインストール()
    
    # 既存仮想環境のパッケージチェックとインストール
    return 仮想環境パッケージ管理(仮想環境パス)

def 仮想環境新規作成(仮想環境パス: str) -> bool:
    """新規仮想環境作成とセットアップ"""
    print(f"\n[SETUP] 仮想環境を作成中...")
    
    try:
        # 仮想環境作成
        venv.create(仮想環境パス, with_pip=True)
        print(f"[OK] 仮想環境作成完了: {仮想環境パス}")
        
        # 少し待機（仮想環境初期化のため）
        time.sleep(1)
        
        # 仮想環境内でパッケージインストール
        return 仮想環境パッケージ管理(仮想環境パス)
        
    except Exception as e:
        print(f"[NG] 仮想環境作成失敗: {e}")
        print(f"[HINT] 手動で作成してください:")
        if platform.system() == "Windows":
            print(f"python -m venv {仮想環境パス}")
            print(f"{仮想環境アクティベーションコマンド取得(仮想環境パス)}")
        else:
            print(f"python3 -m venv {仮想環境パス}")
            print(f"{仮想環境アクティベーションコマンド取得(仮想環境パス)}")
        return False

def 仮想環境再作成(仮想環境パス: str) -> bool:
    """破損した仮想環境の再作成"""
    import shutil
    print(f"🗑️  既存の仮想環境を削除中...")
    
    try:
        shutil.rmtree(仮想環境パス)
        print(f"[OK] 削除完了")
        return 仮想環境新規作成(仮想環境パス)
    except Exception as e:
        print(f"[NG] 削除失敗: {e}")
        return False

def 仮想環境パッケージ管理(仮想環境パス: str) -> bool:
    """仮想環境内でのパッケージ管理"""
    print(f"\n[PKG] 仮想環境内パッケージをチェック中...")
    
    # 仮想環境のPython実行ファイルパス取得
    venv_python = 仮想環境Python実行ファイル取得(仮想環境パス)
    
    if not os.path.exists(venv_python):
        print(f"[NG] 仮想環境のPython実行ファイルが見つかりません: {venv_python}")
        return False
    
    print(f"[OK] 仮想環境Python: {venv_python}")
    
    # 必須パッケージ定義
    必須パッケージ = ['pandas', 'requests', 'requests_cache', 'tqdm']
    オプションパッケージ = ['aiohttp', 'nltk']
    
    # 仮想環境内でパッケージチェック
    インストール必要 = []
    for パッケージ in 必須パッケージ:
        try:
            # 仮想環境内でパッケージ確認
            結果 = subprocess.run([
                venv_python, "-c", f"import {パッケージ}"
            ], capture_output=True, text=True)
            
            if 結果.returncode == 0:
                print(f"  [OK] {パッケージ} - インストール済み")
            else:
                print(f"  [NG] {パッケージ} - 未インストール")
                インストール必要.append(パッケージ)
        except Exception:
            print(f"  [NG] {パッケージ} - 未インストール")
            インストール必要.append(パッケージ)
    
    # 必要に応じてパッケージインストール
    if インストール必要:
        print(f"\n[PKG] {len(インストール必要)}個のパッケージを仮想環境にインストールします...")
        
        try:
            # pipアップグレード
            print("[PKG] pipを最新版にアップグレード中...")
            subprocess.run([
                venv_python, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # 必須パッケージインストール
            print(f"[PKG] 必須パッケージインストール中: {', '.join(インストール必要)}")
            subprocess.run([
                venv_python, "-m", "pip", "install"
            ] + インストール必要, check=True, capture_output=True)
            
            print("[OK] 必須パッケージのインストール完了")
            
        except subprocess.CalledProcessError as e:
            print("[NG] パッケージインストールに失敗しました")
            print(f"エラー詳細: {e}")
            return False
    else:
        print("[OK] 必須パッケージは全てインストール済みです")
    
    # オプションパッケージの提案
    オプション未インストール = []
    for パッケージ in オプションパッケージ:
        try:
            結果 = subprocess.run([
                venv_python, "-c", f"import {パッケージ}"
            ], capture_output=True, text=True)
            
            if 結果.returncode == 0:
                print(f"  [OK] {パッケージ} - インストール済み（高速化機能が利用可能）")
            else:
                オプション未インストール.append(パッケージ)
        except Exception:
            オプション未インストール.append(パッケージ)
    
    if オプション未インストール:
        print(f"\n[HINT] 高速化のため、オプションパッケージのインストールを推奨します:")
        for パッケージ in オプション未インストール:
            if パッケージ == 'aiohttp':
                print(f"  - {パッケージ}: DOI解決が8倍高速化（並列処理）")
            elif パッケージ == 'nltk':
                print(f"  - {パッケージ}: キーワード分析が高精度化（品詞解析）")
        
        try:
            ci環境 = CI環境チェック()
            回答 = 安全なinput("\nオプションパッケージをインストールしますか？ (y/n): ", "y", ci環境)
            if 回答 in ['y', 'yes']:
                print(f"[PKG] オプションパッケージインストール中...")
                subprocess.run([
                    venv_python, "-m", "pip", "install"
                ] + オプション未インストール, check=True, capture_output=True)
                print("[OK] オプションパッケージのインストール完了")
                
                # NLTKリソースのダウンロード
                if 'nltk' in オプション未インストール:
                    print("📚 NLTK追加リソースをダウンロード中...")
                    try:
                        subprocess.run([
                            venv_python, "-c", 
                            "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger_eng', quiet=True); nltk.download('wordnet', quiet=True)"
                        ], check=True, capture_output=True)
                        print("[OK] NLTK追加リソース完了")
                    except Exception as e:
                        print(f"[WARN]  NLTK追加リソースの一部でエラー: {e}")
            else:
                print("⏭️  オプションパッケージをスキップしました")
        except (KeyboardInterrupt, EOFError):
            print("\n🤖 自動実行モード: オプションパッケージをスキップしました")
    
    return True

def システム環境パッケージインストール() -> bool:
    """システム環境でのパッケージインストール（非推奨）"""
    print("\n[WARN]  システム環境でパッケージをインストールします（非推奨）")
    必須パッケージ = ['pandas', 'requests', 'requests_cache', 'tqdm']
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--user'
        ] + 必須パッケージ)
        print("[OK] システム環境でのインストール完了")
        return True
    except subprocess.CalledProcessError as e:
        print("[NG] システム環境でのインストール失敗")
        print("[HINT] 手動でインストールしてください:")
        print(f"pip install --user {' '.join(必須パッケージ)}")
        return False

def ディレクトリ作成():
    """必要なディレクトリを作成"""
    必要ディレクトリ = ['JSON_folder', 'md_folder', 'PDF']
    
    print(f"\n[DIR] 出力ディレクトリを作成中...")
    for ディレクトリ in 必要ディレクトリ:
        if not os.path.exists(ディレクトリ):
            os.makedirs(ディレクトリ)
            print(f"  [DIR] {ディレクトリ}/ を作成")
        else:
            print(f"  [OK] {ディレクトリ}/ 既存")

def 入力ファイル確認():
    """入力CSVファイルの存在確認"""
    print(f"\n[FILE] 入力ファイルをチェック中...")
    
    work_dir = os.getcwd()
    csv_files = [f for f in os.listdir(work_dir) 
                 if f.endswith('.csv') and f != 'scopus_combined.csv']
    
    if csv_files:
        print(f"  [OK] {len(csv_files)}件のCSVファイルを発見:")
        for csv_file in csv_files[:3]:
            print(f"    - {csv_file}")
        if len(csv_files) > 3:
            print(f"    - ... 他{len(csv_files)-3}件")
        return True
    else:
        print(f"  [NG] CSVファイルが見つかりません")
        print(f"  📝 使用方法:")
        print(f"    1. 作業フォルダを作成")
        print(f"    2. Scopus CSVファイルを配置")
        print(f"    3. python setup_improved.py を実行")
        return False

def 実行例表示():
    """実行例を表示"""
    print(f"\n[START] セットアップ完了！以下のコマンドで実行してください:")
    print(f"")
    
    仮想環境パス = ".venv"
    
    if os.path.exists(仮想環境パス):
        print(f"# [OK] 仮想環境セットアップ完了")
        
        アクティベーションコマンド = 仮想環境アクティベーションコマンド取得(仮想環境パス)
        
        print(f"# 📍 ワンコマンド全自動実行（推奨）")
        実行コマンド = 仮想環境実行コマンド生成(仮想環境パス, "python 全自動実行.py" if platform.system() == "Windows" else "python3 全自動実行.py")
        print(f"{実行コマンド}")
        print(f"")
        
        print(f"# 📍 ステップバイステップ実行")
        if platform.system() == "Windows":
            ステップ実行コマンド = 仮想環境実行コマンド生成(仮想環境パス, "python core\\scopus解析.py")
        else:
            ステップ実行コマンド = 仮想環境実行コマンド生成(仮想環境パス, "python3 core/scopus解析.py")
        print(f"{ステップ実行コマンド}")
        print(f"")
        
        print(f"# 📍 PDF取得")
        if platform.system() == "Windows":
            PDF実行コマンド = 仮想環境実行コマンド生成(仮想環境パス, "python pdf_tools\\PDF取得.py")
        else:
            PDF実行コマンド = 仮想環境実行コマンド生成(仮想環境パス, "python3 pdf_tools/PDF取得.py")
        print(f"{PDF実行コマンド}")
        
        print(f"\n[HINT] 次回からは以下のコマンドで簡単実行:")
        print(f"{実行コマンド}")
    else:
        print(f"# [WARN]  システム環境で実行")
        if platform.system() == "Windows":
            print(f"python 全自動実行.py")
            print(f"python core\\scopus解析.py")
            print(f"python pdf_tools\\PDF取得.py")
        else:
            print(f"python3 全自動実行.py")
            print(f"python3 core/scopus解析.py")
            print(f"python3 pdf_tools/PDF取得.py")

def main():
    """メイン処理"""
    print("[TARGET] Scopus文献可視化システム - 改良版自動セットアップ")
    print("=" * 60)
    print("✨ 機能: 仮想環境作成→パッケージインストール→ディレクトリ作成を一回で完了")
    print("=" * 60)
    
    # コマンドライン引数チェック
    自動実行 = len(sys.argv) > 1 and sys.argv[1] == "--auto"
    
    # Python バージョンチェック
    if sys.version_info < (3, 8):
        print("[NG] Python 3.8以上が必要です")
        print(f"現在のバージョン: {sys.version}")
        print("[HINT] Python 3.7は2023年6月でサポート終了しました")
        sys.exit(1)
    else:
        print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor} 対応")
    
    # OS確認
    print(f"[OK] OS: {platform.system()}")
    
    # 仮想環境作成とパッケージインストール（一回で完了）
    if not 仮想環境作成および設定(自動実行=自動実行):
        print("[NG] 仮想環境セットアップに失敗しました")
        sys.exit(1)
    
    # ディレクトリ作成
    ディレクトリ作成()
    
    # 入力ファイル確認
    入力ファイル確認()
    
    # 実行例表示
    実行例表示()
    
    print(f"\n[DONE] 改良版セットアップ完了！")
    print(f"[HINT] 仮想環境作成からパッケージインストールまで一回で完了しました")

if __name__ == "__main__":
    main()
