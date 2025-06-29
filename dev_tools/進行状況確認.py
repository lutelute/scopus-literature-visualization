#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
進行状況確認.py - プロジェクト作業状況の確認と記録
"""

import os
import json
import time
from datetime import datetime

def ファイル数取得(ディレクトリ: str, 拡張子: str) -> int:
    """指定ディレクトリ内の指定拡張子ファイル数を取得"""
    if os.path.exists(ディレクトリ):
        return len([f for f in os.listdir(ディレクトリ) if f.endswith(拡張子)])
    return 0

def フォルダサイズ取得(ディレクトリ: str) -> float:
    """フォルダサイズをMB単位で取得"""
    if not os.path.exists(ディレクトリ):
        return 0.0
    
    総サイズ = 0
    for dirpath, dirnames, filenames in os.walk(ディレクトリ):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                総サイズ += os.path.getsize(filepath)
    
    return 総サイズ / (1024 * 1024)  # MB変換

def 進行状況記録作成():
    """現在の進行状況を記録"""
    基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # ファイル数確認
    json数 = ファイル数取得(os.path.join(基準ディレクトリ, "JSON_folder"), '.json')
    md数 = ファイル数取得(os.path.join(基準ディレクトリ, "md_folder"), '.md')
    pdf数 = ファイル数取得(os.path.join(基準ディレクトリ, "PDF"), '.pdf')
    
    # フォルダサイズ確認
    jsonサイズ = フォルダサイズ取得(os.path.join(基準ディレクトリ, "JSON_folder"))
    mdサイズ = フォルダサイズ取得(os.path.join(基準ディレクトリ, "md_folder"))
    pdfサイズ = フォルダサイズ取得(os.path.join(基準ディレクトリ, "PDF"))
    
    # キャッシュファイル確認
    キャッシュファイル = {
        "crossref_cache.sqlite": os.path.exists(os.path.join(基準ディレクトリ, "crossref_cache.sqlite")),
        "doi_title_cache.json": os.path.exists(os.path.join(基準ディレクトリ, "doi_title_cache.json")),
        "scopus_combined.csv": os.path.exists(os.path.join(基準ディレクトリ, "scopus_combined.csv"))
    }
    
    # 進行状況データ
    進行状況 = {
        "記録日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ファイル数": {
            "JSON": json数,
            "Markdown": md数,
            "PDF": pdf数
        },
        "フォルダサイズ_MB": {
            "JSON_folder": round(jsonサイズ, 2),
            "md_folder": round(mdサイズ, 2),
            "PDF": round(pdfサイズ, 2)
        },
        "キャッシュファイル": キャッシュファイル,
        "処理段階": {
            "CSV結合": os.path.exists(os.path.join(基準ディレクトリ, "scopus_combined.csv")),
            "DOI取得": json数 > 0,
            "Markdown生成": md数 > 0,
            "キーワード分析": "実行確認が必要",
            "YAML追加": "実行確認が必要",
            "PDF取得": pdf数 > 0
        }
    }
    
    return 進行状況

def 作業再開ガイド表示():
    """作業再開のガイドを表示"""
    print("\n📋 作業再開ガイド")
    print("=" * 40)
    print("1️⃣ 進行状況確認:")
    print("   python3 dev_tools/進行状況確認.py")
    print()
    print("2️⃣ メイン処理:")
    print("   python3 core/scopus解析.py")
    print("   → オプション選択で必要な処理のみ実行")
    print()
    print("3️⃣ PDF取得:")
    print("   python3 pdf_tools/PDF取得.py")
    print("   → 3つの取得方法から選択")
    print()
    print("4️⃣ クリーンアップ（必要時）:")
    print("   python3 utils/クリーンアップ.py")
    print("   → 最初からやり直したい場合")

def 問題診断():
    """よくある問題の診断"""
    基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n🔍 問題診断")
    print("=" * 25)
    
    # 入力ファイル確認
    入力csv = os.path.join(基準ディレクトリ, "GFM_rev", "scopus_gfm_rev.csv")
    if os.path.exists(入力csv):
        print("✅ 入力CSVファイル: 存在")
    else:
        print("❌ 入力CSVファイル: 見つかりません")
        print("   → GFM_rev/scopus_gfm_rev.csv を確認してください")
    
    # 必要モジュール確認
    try:
        import nltk
        print("✅ NLTK: インストール済み")
    except ImportError:
        print("⚠️  NLTK: 未インストール")
        print("   → キーワード分析に必要です")
    
    try:
        import aiohttp
        print("✅ aiohttp: インストール済み")
    except ImportError:
        print("ℹ️  aiohttp: 未インストール（標準版で代替可能）")
    
    # 権限確認
    if os.access(基準ディレクトリ, os.W_OK):
        print("✅ 書き込み権限: OK")
    else:
        print("❌ 書き込み権限: 不足")

def main():
    """メイン処理"""
    print("📊 Scopus文献可視化プロジェクト - 進行状況確認")
    print("=" * 55)
    
    # 現在の進行状況を取得
    進行状況 = 進行状況記録作成()
    
    # 進行状況表示
    print(f"🕒 記録日時: {進行状況['記録日時']}")
    print()
    
    print("📁 ファイル数:")
    for ファイル種類, 数 in 進行状況['ファイル数'].items():
        print(f"   {ファイル種類}: {数}件")
    
    print()
    print("💾 フォルダサイズ:")
    for フォルダ, サイズ in 進行状況['フォルダサイズ_MB'].items():
        print(f"   {フォルダ}: {サイズ} MB")
    
    print()
    print("⚙️ 処理段階:")
    for 段階, 状況 in 進行状況['処理段階'].items():
        if isinstance(状況, bool):
            マーク = "✅" if 状況 else "⏳"
            print(f"   {マーク} {段階}")
        else:
            print(f"   ❓ {段階}: {状況}")
    
    print()
    print("📦 キャッシュファイル:")
    for ファイル, 存在 in 進行状況['キャッシュファイル'].items():
        マーク = "✅" if 存在 else "❌"
        print(f"   {マーク} {ファイル}")
    
    # 進行状況をJSONで保存
    基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    進行状況ファイル = os.path.join(基準ディレクトリ, "dev_tools", "進行状況.json")
    with open(進行状況ファイル, 'w', encoding='utf-8') as f:
        json.dump(進行状況, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 進行状況を保存しました: dev_tools/進行状況.json")
    
    # 問題診断実行
    問題診断()
    
    # 作業再開ガイド表示
    作業再開ガイド表示()
    
    # 推奨次ステップ
    print("\n🎯 推奨次ステップ:")
    if 進行状況['ファイル数']['JSON'] == 0:
        print("   → まずは core/scopus解析.py でDOI取得から始めてください")
    elif 進行状況['ファイル数']['Markdown'] == 0:
        print("   → JSON生成済み。Markdown生成を実行してください")
    elif 進行状況['ファイル数']['PDF'] == 0:
        print("   → Markdown生成済み。PDF取得を実行してください")
    else:
        print("   → 基本処理完了！必要に応じてキーワード分析やクリーンアップを実行")

if __name__ == "__main__":
    main()