#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_crossplatform.py - クロスプラットフォーム対応テストスクリプト
Windows/Mac/Linux での動作確認用
"""

import os
import sys
import platform
import subprocess
import importlib.util

def OS情報表示():
    """現在のOS情報を表示"""
    print("[システム情報]")
    print(f"   OS: {platform.system()}")
    print(f"   バージョン: {platform.version()}")
    print(f"   アーキテクチャ: {platform.machine()}")
    print(f"   Python: {sys.version}")
    print(f"   実行可能ファイル: {sys.executable}")

def 仮想環境アクティベーションコマンド取得(仮想環境パス: str) -> str:
    """OS別の仮想環境アクティベーションコマンドを取得"""
    if platform.system() == "Windows":
        return f"{仮想環境パス}\\Scripts\\activate"
    else:
        return f"source {仮想環境パス}/bin/activate"

def 仮想環境Python実行ファイル取得(仮想環境パス: str) -> str:
    """OS別の仮想環境内Python実行ファイルパス"""
    if platform.system() == "Windows":
        return f"{仮想環境パス}\\Scripts\\python.exe"
    else:
        return f"{仮想環境パス}/bin/python"

def 仮想環境pip実行ファイル取得(仮想環境パス: str) -> str:
    """OS別の仮想環境内pip実行ファイルパス"""
    if platform.system() == "Windows":
        return f"{仮想環境パス}\\Scripts\\pip.exe"
    else:
        return f"{仮想環境パス}/bin/pip"

def 仮想環境実行コマンド生成(仮想環境パス: str, コマンド: str) -> str:
    """OS別の仮想環境実行コマンドを生成"""
    if platform.system() == "Windows":
        return f"{仮想環境パス}\\Scripts\\activate && {コマンド}"
    else:
        return f"source {仮想環境パス}/bin/activate && {コマンド}"

def パス表示テスト():
    """パス処理のテスト"""
    print("\\n[パス処理テスト]")
    
    # 基本パス処理
    基準ディレクトリ = os.path.dirname(os.path.abspath(__file__))
    print(f"   基準ディレクトリ: {基準ディレクトリ}")
    
    # 各種ディレクトリパス
    テストパス = {
        "仮想環境": ".venv",
        "JSON_folder": "JSON_folder",
        "md_folder": "md_folder", 
        "PDF": "PDF",
        "core": "core",
        "pdf_tools": "pdf_tools",
        "utils": "utils"
    }
    
    for 名前, パス in テストパス.items():
        絶対パス = os.path.join(基準ディレクトリ, パス)
        存在 = "[OK]" if os.path.exists(絶対パス) else "[NG]"
        print(f"   {存在} {名前}: {絶対パス}")

def 仮想環境テスト():
    """仮想環境関連のテスト"""
    print("\\n[仮想環境テスト]")
    
    仮想環境パス = ".venv"
    
    # 仮想環境の存在確認
    if os.path.exists(仮想環境パス):
        print(f"   [OK] 仮想環境ディレクトリ存在: {仮想環境パス}")
        
        # OS別実行ファイルの確認
        python実行ファイル = 仮想環境Python実行ファイル取得(仮想環境パス)
        pip実行ファイル = 仮想環境pip実行ファイル取得(仮想環境パス)
        
        python存在 = "[OK]" if os.path.exists(python実行ファイル) else "[NG]"
        pip存在 = "[OK]" if os.path.exists(pip実行ファイル) else "[NG]"
        
        print(f"   {python存在} Python実行ファイル: {python実行ファイル}")
        print(f"   {pip存在} pip実行ファイル: {pip実行ファイル}")
        
        # アクティベーションコマンド表示
        アクティベーションコマンド = 仮想環境アクティベーションコマンド取得(仮想環境パス)
        print(f"   [CMD] アクティベーションコマンド: {アクティベーションコマンド}")
        
        # 仮想環境がアクティブかチェック
        is_venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        状態 = "アクティブ" if is_venv_active else "非アクティブ"
        print(f"   [INFO] 現在の状態: {状態}")
        
    else:
        print(f"   [NG] 仮想環境が見つかりません: {仮想環境パス}")
        print(f"   [HINT] 作成コマンド:")
        if platform.system() == "Windows":
            print(f"      python -m venv {仮想環境パス}")
        else:
            print(f"      python3 -m venv {仮想環境パス}")

def パッケージテスト():
    """必須パッケージのテスト"""
    print("\\n[パッケージテスト]")
    
    必須パッケージ = ['pandas', 'requests', 'requests_cache', 'tqdm']
    オプションパッケージ = ['aiohttp', 'nltk']
    
    print("   必須パッケージ:")
    for パッケージ名 in 必須パッケージ:
        spec = importlib.util.find_spec(パッケージ名)
        状態 = "[OK] インストール済み" if spec is not None else "[NG] 未インストール"
        print(f"     {状態}: {パッケージ名}")
    
    print("   オプションパッケージ:")
    for パッケージ名 in オプションパッケージ:
        spec = importlib.util.find_spec(パッケージ名)
        状態 = "[OK] インストール済み" if spec is not None else "[WARN] 未インストール"
        print(f"     {状態}: {パッケージ名}")

def コマンド例表示():
    """OS別のコマンド例を表示"""
    print("\\n[OS別実行コマンド例]")
    
    仮想環境パス = ".venv"
    
    if platform.system() == "Windows":
        print("   Windows:")
        print(f"     仮想環境作成: python -m venv {仮想環境パス}")
        print(f"     アクティベート: {仮想環境アクティベーションコマンド取得(仮想環境パス)}")
        print(f"     セットアップ実行: python setup.py")
        print(f"     全自動実行: python 全自動実行.py")
        print(f"     手動実行: python core\\\\scopus解析.py")
    else:
        print("   macOS/Linux:")
        print(f"     仮想環境作成: python3 -m venv {仮想環境パス}")
        print(f"     アクティベート: {仮想環境アクティベーションコマンド取得(仮想環境パス)}")
        print(f"     セットアップ実行: python3 setup.py")
        print(f"     全自動実行: python3 全自動実行.py")
        print(f"     手動実行: python3 core/scopus解析.py")

def main():
    """メイン処理"""
    print("Scopus文献可視化システム - クロスプラットフォーム対応テスト")
    print("=" * 60)
    
    OS情報表示()
    パス表示テスト()
    仮想環境テスト()
    パッケージテスト()
    コマンド例表示()
    
    print("\\n[テスト完了]")
    print("上記の結果を確認して、必要に応じて環境をセットアップしてください。")

if __name__ == "__main__":
    main()