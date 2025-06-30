#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup.py - Scopus文献可視化システム 自動セットアップスクリプト
"""

import os
import sys
import subprocess
import importlib.util
import venv
import shutil

def パッケージ確認(パッケージ名: str) -> bool:
    """パッケージがインストールされているかチェック"""
    spec = importlib.util.find_spec(パッケージ名)
    return spec is not None

def 仮想環境チェック作成():
    """仮想環境の存在チェックと自動作成"""
    仮想環境パス = ".venv"
    
    print("🔍 仮想環境をチェック中...")
    
    if os.path.exists(仮想環境パス):
        print("✅ 仮想環境が既に存在します")
        return True
    
    print("📦 仮想環境が見つかりません。作成しますか？")
    print("   (推奨: パッケージの依存関係競合を避けるため)")
    
    try:
        回答 = input("仮想環境を作成しますか？ (y/n): ").lower().strip()
        if 回答 in ['y', 'yes']:
            print(f"\n🔧 仮想環境を作成中...")
            try:
                venv.create(仮想環境パス, with_pip=True)
                print(f"✅ 仮想環境作成完了: {仮想環境パス}")
                print(f"\n💡 次回から以下のコマンドで実行してください:")
                print(f"source {仮想環境パス}/bin/activate && python3 setup.py")
                return True
            except Exception as e:
                print(f"❌ 仮想環境作成失敗: {e}")
                print(f"💡 手動で作成してください:")
                print(f"python3 -m venv {仮想環境パス}")
                print(f"source {仮想環境パス}/bin/activate")
                return False
        else:
            print("⏭️  システム環境で実行します（非推奨）")
            return True
    except KeyboardInterrupt:
        print("\n⏹️  中断されました")
        return False

def 仮想環境アクティベーション確認():
    """仮想環境がアクティブかチェック"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 仮想環境がアクティブです")
        return True
    else:
        if os.path.exists(".venv"):
            print("⚠️  仮想環境が存在しますが、アクティブではありません")
            print(f"💡 以下のコマンドでアクティベートしてください:")
            print(f"source .venv/bin/activate")
            print(f"python3 setup.py")
        else:
            print("⚠️  仮想環境を使用していません（システム環境で実行）")
        return False

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
        
        # 仮想環境アクティベーション状況をチェック
        is_venv_active = 仮想環境アクティベーション確認()
        
        try:
            # 仮想環境がある場合はアクティベーションを促す
            if os.path.exists(".venv") and not is_venv_active:
                print("⚠️  仮想環境をアクティベートしてから再実行してください")
                print("以下のコマンドを実行してください:")
                print("source .venv/bin/activate && python3 setup.py")
                return False
            
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '--quiet', '--disable-pip-version-check'
            ] + インストール必要)
            print("✅ 必須パッケージのインストール完了")
        except subprocess.CalledProcessError as e:
            print("❌ パッケージインストールに失敗しました")
            
            # エラーがexternally-managed-environmentの場合は特別な案内
            if "externally-managed-environment" in str(e):
                print("💡 システム環境での直接インストールが制限されています")
                print("🔧 解決方法:")
                print("1. 仮想環境を作成してアクティベート:")
                print("   python3 -m venv .venv")
                print("   source .venv/bin/activate")
                print("   python3 setup.py")
                print("2. または --break-system-packages を使用:")
                print(f"   pip install --break-system-packages {' '.join(インストール必要)}")
            else:
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
    
    # 現在のディレクトリでCSVファイルを検索
    work_dir = os.getcwd()
    csv_files = [f for f in os.listdir(work_dir) 
                 if f.endswith('.csv') and f != 'scopus_combined.csv']
    
    if csv_files:
        print(f"  ✅ {len(csv_files)}件のCSVファイルを発見:")
        for csv_file in csv_files[:3]:  # 最初の3件を表示
            print(f"    - {csv_file}")
        if len(csv_files) > 3:
            print(f"    - ... 他{len(csv_files)-3}件")
        return True
    else:
        print(f"  ❌ CSVファイルが見つかりません")
        print(f"  📝 使用方法:")
        print(f"    1. 作業フォルダを作成")
        print(f"    2. Scopus CSVファイルを配置")
        print(f"    3. git clone でこのツールをクローン")
        print(f"    4. python3 setup.py を実行")
        return False

def 実行例表示():
    """実行例を表示"""
    print(f"\n🚀 セットアップ完了！以下のコマンドで実行してください:")
    print(f"")
    
    # 仮想環境の状況に応じて表示を分ける
    if os.path.exists(".venv"):
        is_venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if is_venv_active:
            print(f"# ✅ 仮想環境アクティブ - そのまま実行可能")
        else:
            print(f"# 🔧 仮想環境をアクティベートしてから実行")
            print(f"source .venv/bin/activate")
            print(f"")
        
        print(f"# 📍 ワンコマンド全自動実行（推奨）")
        if is_venv_active:
            print(f"python3 全自動実行.py")
        else:
            print(f"source .venv/bin/activate && python3 全自動実行.py")
        print(f"")
        
        print(f"# 📍 ステップバイステップ実行")
        if is_venv_active:
            print(f"python3 core/scopus解析.py")
        else:
            print(f"source .venv/bin/activate && python3 core/scopus解析.py")
        print(f"")
        
        print(f"# 📍 PDF取得")
        if is_venv_active:
            print(f"python3 pdf_tools/PDF取得.py")
        else:
            print(f"source .venv/bin/activate && python3 pdf_tools/PDF取得.py")
    else:
        print(f"# ⚠️  システム環境で実行")
        print(f"python3 全自動実行.py")
        print(f"python3 core/scopus解析.py")
        print(f"python3 pdf_tools/PDF取得.py")

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
    
    # 仮想環境チェック・作成
    if not 仮想環境チェック作成():
        print("❌ 仮想環境セットアップに失敗しました")
        sys.exit(1)
    
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