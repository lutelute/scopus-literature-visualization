#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup.py - Scopus文献可視化システム 自動セットアップスクリプト
"""

import os
import sys
import subprocess
import importlib.util

def パッケージ確認(パッケージ名: str) -> bool:
    """パッケージがインストールされているかチェック"""
    spec = importlib.util.find_spec(パッケージ名)
    return spec is not None

def 必須パッケージインストール():
    """必須パッケージの自動インストール"""
    必須パッケージ = [
        'pandas',
        'requests', 
        'requests_cache',
        'tqdm'
    ]
    
    オプションパッケージ = [
        'aiohttp',
        'nltk'
    ]
    
    print("🔍 必須パッケージをチェック中...")
    インストール必要 = []
    
    for パッケージ in 必須パッケージ:
        if not パッケージ確認(パッケージ):
            インストール必要.append(パッケージ)
            print(f"  ❌ {パッケージ} - 未インストール")
        else:
            print(f"  ✅ {パッケージ} - インストール済み")
    
    if インストール必要:
        print(f"\n📦 {len(インストール必要)}個のパッケージをインストールします...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + インストール必要)
            print("✅ 必須パッケージのインストール完了")
        except subprocess.CalledProcessError:
            print("❌ パッケージインストールに失敗しました")
            print("手動でインストールしてください:")
            print(f"pip install {' '.join(インストール必要)}")
            return False
    else:
        print("✅ 必須パッケージは全てインストール済みです")
    
    # オプションパッケージのチェック
    print(f"\n🔍 オプションパッケージをチェック中...")
    未インストール = []
    for パッケージ in オプションパッケージ:
        if パッケージ確認(パッケージ):
            print(f"  ✅ {パッケージ} - インストール済み（高速化機能が利用可能）")
        else:
            print(f"  ⚠️  {パッケージ} - 未インストール（標準版で動作）")
            未インストール.append(パッケージ)
    
    if 未インストール:
        print(f"\n💡 高速化のため、以下のコマンドでオプションパッケージをインストールできます:")
        print(f"pip install {' '.join(未インストール)}")
        print(f"")
        print(f"📝 機能説明:")
        print(f"  - aiohttp: DOI解決が8倍高速化（並列処理）")
        print(f"  - nltk: キーワード分析が高精度化（品詞解析）")
    
    return True

def ディレクトリ作成():
    """必要なディレクトリを作成"""
    必要ディレクトリ = [
        'JSON_folder',
        'md_folder', 
        'PDF'
    ]
    
    print(f"\n📁 出力ディレクトリを作成中...")
    for ディレクトリ in 必要ディレクトリ:
        if not os.path.exists(ディレクトリ):
            os.makedirs(ディレクトリ)
            print(f"  📁 {ディレクトリ}/ を作成")
        else:
            print(f"  ✅ {ディレクトリ}/ 既存")

def 入力ファイル確認():
    """入力CSVファイルの存在確認"""
    print(f"\n📄 入力ファイルをチェック中...")
    
    入力パス = os.path.join('GFM_rev', 'scopus_gfm_rev.csv')
    if os.path.exists(入力パス):
        print(f"  ✅ {入力パス} - 発見")
        return True
    else:
        print(f"  ❌ {入力パス} - 見つかりません")
        print(f"  📝 Scopus CSVファイルを GFM_rev/ フォルダに配置してください")
        return False

def 実行例表示():
    """実行例を表示"""
    print(f"\n🚀 セットアップ完了！以下のコマンドで実行してください:")
    print(f"")
    print(f"# 日本語版（推奨）")
    print(f"python3 core/scopus解析.py")
    print(f"")
    print(f"# 英語版")
    print(f"python3 main.py")
    print(f"")
    print(f"# PDF取得")
    print(f"python3 pdf_tools/PDF取得.py")
    print(f"")
    print(f"# 開発・テスト用")
    print(f"python3 dev_tools/進行状況確認.py")

def main():
    """メイン処理"""
    print("🎯 Scopus文献可視化システム - 自動セットアップ")
    print("=" * 50)
    
    # Python バージョンチェック
    if sys.version_info < (3, 7):
        print("❌ Python 3.7以上が必要です")
        print(f"現在のバージョン: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} 対応")
    
    # パッケージインストール
    if not 必須パッケージインストール():
        sys.exit(1)
    
    # ディレクトリ作成
    ディレクトリ作成()
    
    # 入力ファイル確認
    入力ファイル確認()
    
    # 実行例表示
    実行例表示()
    
    print(f"\n🎉 セットアップ完了！")

if __name__ == "__main__":
    main()