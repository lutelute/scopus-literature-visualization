#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py - Scopus文献可視化システム スタートアップスクリプト

このスクリプトは：
1. 依存関係の自動チェック・インストール
2. 環境の自動セットアップ
3. メインスクリプトの起動
を行います。
"""

import os
import sys
import subprocess
import importlib.util

def 依存関係チェック・インストール():
    """必須パッケージの確認と自動インストール"""
    必須パッケージ = [
        'pandas',
        'requests', 
        'requests_cache',
        'tqdm'
    ]
    
    print("[INFO] 依存関係をチェック中...")
    未インストール = []
    
    for パッケージ名 in 必須パッケージ:
        spec = importlib.util.find_spec(パッケージ名)
        if spec is None:
            未インストール.append(パッケージ名)
            print(f"  [NG] {パッケージ名} - 未インストール")
        else:
            print(f"  [OK] {パッケージ名} - インストール済み")
    
    if 未インストール:
        print(f"\n[WARN]  {len(未インストール)}個の必須パッケージが不足しています")
        print(f"[PKG] 自動インストールを実行します...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + 未インストール)
            print(f"[OK] インストール完了: {', '.join(未インストール)}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[NG] 自動インストール失敗: {e}")
            print(f"\n[HINT] 手動でインストールしてください:")
            print(f"pip install {' '.join(未インストール)}")
            return False
    else:
        print(f"[OK] 必須パッケージは全てインストール済みです")
        return True

def オプションライブラリチェック():
    """オプションライブラリの確認"""
    オプションパッケージ = ['aiohttp', 'nltk']
    未インストール = []
    
    print(f"\n[INFO] オプションライブラリをチェック中...")
    for パッケージ名 in オプションパッケージ:
        spec = importlib.util.find_spec(パッケージ名)
        if spec is None:
            未インストール.append(パッケージ名)
            print(f"  [WARN]  {パッケージ名} - 未インストール（標準版で動作）")
        else:
            print(f"  [OK] {パッケージ名} - インストール済み（高速化機能利用可能）")
    
    if 未インストール:
        print(f"\n[HINT] 高速化のため、以下のコマンドでオプションライブラリをインストールできます:")
        print(f"pip install {' '.join(未インストール)}")
        print(f"\n📝 機能差:")
        if 'aiohttp' in 未インストール:
            print(f"  - aiohttp: DOI解決が8倍高速化（並列処理）")
        if 'nltk' in 未インストール:
            print(f"  - nltk: キーワード分析が高精度化（品詞解析）")

def 環境セットアップ():
    """必要なディレクトリを作成"""
    必要ディレクトリ = ['JSON_folder', 'md_folder', 'PDF']
    
    print(f"\n[DIR] 出力ディレクトリをセットアップ中...")
    for ディレクトリ in 必要ディレクトリ:
        if not os.path.exists(ディレクトリ):
            os.makedirs(ディレクトリ)
            print(f"  [DIR] {ディレクトリ}/ を作成")
        else:
            print(f"  [OK] {ディレクトリ}/ 既存")

def CSVファイル確認():
    """入力CSVファイルの存在確認"""
    print(f"\n[FILE] 入力ファイルをチェック中...")
    
    # 親ディレクトリ（作業フォルダ）でCSVファイルを検索
    親ディレクトリ = os.path.dirname(os.getcwd())
    csv_files = [f for f in os.listdir(親ディレクトリ) 
                 if f.endswith('.csv') and f != 'scopus_combined.csv']
    
    if csv_files:
        print(f"  [OK] {len(csv_files)}件のCSVファイルを発見:")
        for csv_file in csv_files[:3]:
            print(f"    - {csv_file}")
        if len(csv_files) > 3:
            print(f"    - ... 他{len(csv_files)-3}件")
        return True
    else:
        print(f"  [WARN]  CSVファイルが見つかりません")
        print(f"  📝 使用方法:")
        print(f"    1. 作業フォルダを作成")
        print(f"    2. Scopus CSVファイルを配置")
        print(f"    3. ツールをクローン")
        print(f"    4. python3 run.py を実行")
        return False

def 仮想環境チェック():
    """仮想環境の確認と案内"""
    venv_path = '.venv'
    
    if os.path.exists(venv_path):
        print(f"\n[PKG] 仮想環境を発見: {venv_path}")
        
        # 仮想環境がアクティブかチェック
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print(f"[OK] 仮想環境アクティブ中")
            return True
        else:
            print(f"[WARN]  仮想環境が非アクティブです")
            print(f"[HINT] 以下のコマンドで仮想環境をアクティベートしてください:")
            print(f"source .venv/bin/activate")
            print(f"python3 core/scopus解析.py")
            return False
    else:
        print(f"[PKG] 仮想環境が見つかりません - グローバル環境で実行")
        return True

def メインスクリプト起動():
    """メインスクリプトを起動"""
    print(f"\n[START] メインスクリプトを起動中...")
    core_script = os.path.join('core', 'scopus解析.py')
    
    if os.path.exists(core_script):
        subprocess.run([sys.executable, core_script])
    else:
        print(f"[NG] メインスクリプトが見つかりません: {core_script}")

def main():
    """メイン処理"""
    print("[TARGET] Scopus文献可視化システム - スタートアップ")
    print("=" * 50)
    
    # Python バージョンチェック
    if sys.version_info < (3, 7):
        print("[NG] Python 3.7以上が必要です")
        print(f"現在のバージョン: {sys.version}")
        sys.exit(1)
    else:
        print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor} 対応")
    
    # 依存関係チェック・インストール
    if not 依存関係チェック・インストール():
        print("\n[NG] 依存関係エラーにより終了します")
        sys.exit(1)
    
    # オプションライブラリチェック
    オプションライブラリチェック()
    
    # 仮想環境チェック
    if not 仮想環境チェック():
        print("\n[NG] 仮想環境の問題により終了します")
        sys.exit(1)
    
    # 環境セットアップ
    環境セットアップ()
    
    # CSVファイル確認
    CSVファイル確認()
    
    # メインスクリプト起動
    メインスクリプト起動()

if __name__ == "__main__":
    main()