#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF取得.py - 論文PDF取得専用ツール
"""

import os
import subprocess
import sys
import time

def pdf取得実行(スクリプト名: str, 説明: str) -> bool:
    """PDF取得スクリプトを実行"""
    print(f"\n🚀 {説明}を開始...")
    print(f"📄 実行ファイル: {スクリプト名}")
    
    try:
        開始時間 = time.time()
        基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        スクリプトパス = os.path.join(基準ディレクトリ, "pdf_tools", スクリプト名)
        結果 = subprocess.run([sys.executable, スクリプトパス], 
                              capture_output=True, 
                              text=True, 
                              cwd=基準ディレクトリ)
        
        実行時間 = time.time() - 開始時間
        
        if 結果.returncode == 0:
            print(f"✅ {説明} 完了 ({実行時間:.1f}秒)")
            if 結果.stdout:
                # 成功メッセージと統計のみ表示
                出力行 = 結果.stdout.split('\n')
                重要行 = [行 for 行 in 出力行 if any(マーク in 行 for マーク in ['✅', '📊', '📁', '📈', '🎉', 'PDF取得完了', '新規PDF', '総PDF'])]
                for 行 in 重要行[-8:]:  # 最後の8個の重要メッセージ
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

def pdf数取得(pdfディレクトリ: str) -> int:
    """PDFディレクトリ内のPDF数を取得"""
    if os.path.exists(pdfディレクトリ):
        return len([f for f in os.listdir(pdfディレクトリ) if f.endswith('.pdf')])
    return 0

def main():
    """PDF取得メイン処理"""
    print("📥 論文PDF取得ツール")
    print("=" * 40)
    
    基準ディレクトリ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdfディレクトリ = os.path.join(基準ディレクトリ, "PDF")
    
    # 現在のPDF数確認
    初期pdf数 = pdf数取得(pdfディレクトリ)
    print(f"📊 現在のPDF数: {初期pdf数}件")
    
    # PDF取得オプション
    pdf取得方法 = [
        ("download_open_access_pdfs_fast_stdlib.py", "オープンアクセス論文（高速版）"),
        ("download_researchgate_pdfs.py", "ResearchGate検索取得"),
        ("download_open_access_pdfs.py", "オープンアクセス論文（標準版）"),
    ]
    
    print("\n📋 利用可能なPDF取得方法:")
    for i, (スクリプト, 説明) in enumerate(pdf取得方法, 1):
        print(f"   {i}. {説明}")
    
    print("   0. 全ての方法を順次実行")
    print("   q. 終了")
    
    while True:
        選択 = input("\n選択してください (0-3, q): ").strip().lower()
        
        if 選択 == 'q':
            print("👋 終了します。")
            return
        
        if 選択 == '0':
            print("\n🚀 全てのPDF取得方法を順次実行します...")
            成功数 = 0
            
            for スクリプト, 説明 in pdf取得方法:
                if pdf取得実行(スクリプト, 説明):
                    成功数 += 1
                    現在pdf数 = pdf数取得(pdfディレクトリ)
                    新規pdf数 = 現在pdf数 - 初期pdf数
                    print(f"📈 累積新規PDF: {新規pdf数}件 (総計: {現在pdf数}件)")
                else:
                    print(f"⚠️ {説明}でエラーが発生しました。")
                
                print("-" * 25)
            
            最終pdf数 = pdf数取得(pdfディレクトリ)
            総新規pdf数 = 最終pdf数 - 初期pdf数
            
            print(f"\n🎉 全PDF取得処理完了!")
            print(f"📊 成功率: {成功数}/{len(pdf取得方法)} 方法")
            print(f"📥 新規PDF取得: {総新規pdf数}件")
            print(f"📁 総PDF数: {最終pdf数}件")
            break
        
        elif 選択.isdigit() and 1 <= int(選択) <= len(pdf取得方法):
            インデックス = int(選択) - 1
            スクリプト, 説明 = pdf取得方法[インデックス]
            
            print(f"\n🚀 {説明}を実行します...")
            if pdf取得実行(スクリプト, 説明):
                最終pdf数 = pdf数取得(pdfディレクトリ)
                新規pdf数 = 最終pdf数 - 初期pdf数
                print(f"\n📈 新規PDF取得: {新規pdf数}件")
                print(f"📁 総PDF数: {最終pdf数}件")
            break
        
        else:
            print("❌ 無効な選択です。0-3またはqを入力してください。")

if __name__ == "__main__":
    main()