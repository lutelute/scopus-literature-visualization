#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF tools runner for Scopus Literature Visualization
"""

import os
import subprocess
import sys
from pathlib import Path


def run_pdf_tools(auto_mode=False):
    """PDF取得ツール実行"""
    
    print("[FILE] PDF取得ツール開始")
    print("=" * 30)
    
    # PDF取得スクリプトのパス
    pdf_script = Path("pdf_tools/PDF取得.py")
    
    if not pdf_script.exists():
        print("[WARN] PDF取得スクリプトが見つかりません")
        return
    
    try:
        if auto_mode:
            # 自動モードでは全ての方法を順次実行
            print("🤖 自動モード: 全PDF取得方法を順次実行")
            # '0'を標準入力に送信して全方法実行を選択
            result = subprocess.run(
                [sys.executable, str(pdf_script)],
                input="0\n",
                text=True,
                capture_output=True
            )
        else:
            # インタラクティブモード
            result = subprocess.run(
                [sys.executable, str(pdf_script)],
                check=True
            )
        
        if result.returncode == 0:
            print("[OK] PDF取得完了")
        else:
            print("[WARN] PDF取得で一部エラーが発生しました")
            
    except subprocess.CalledProcessError as e:
        print(f"[NG] PDF取得でエラーが発生しました: {e}")
    except Exception as e:
        print(f"[NG] 予期しないエラー: {e}")


def main():
    """PDF取得ツール単体実行用メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scopus Literature PDF Tools')
    parser.add_argument('--auto', action='store_true', help='自動実行モード')
    args = parser.parse_args()
    
    run_pdf_tools(auto_mode=args.auto)


if __name__ == "__main__":
    main()