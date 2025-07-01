#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI interface for Scopus Literature Visualization
"""

import argparse
import os
import sys
from pathlib import Path
from .pipeline import run_pipeline
from .pdf_tools import run_pdf_tools


def main():
    """メインCLI関数"""
    parser = argparse.ArgumentParser(
        description='Scopus Literature Visualization Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  scopus-lit-viz --auto                # 全自動実行
  scopus-lit-viz --dir /path/to/data   # 特定ディレクトリで実行
  scopus-lit-viz --pipeline-only       # パイプラインのみ実行
  scopus-lit-viz --pdf-only            # PDF取得のみ実行
        """
    )
    
    parser.add_argument(
        '--dir', '-d',
        type=str,
        default=os.getcwd(),
        help='作業ディレクトリ (デフォルト: 現在のディレクトリ)'
    )
    
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='全自動実行モード'
    )
    
    parser.add_argument(
        '--pipeline-only',
        action='store_true',
        help='パイプライン処理のみ実行'
    )
    
    parser.add_argument(
        '--pdf-only',
        action='store_true',
        help='PDF取得のみ実行'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # 作業ディレクトリ設定
    work_dir = Path(args.dir).resolve()
    if not work_dir.exists():
        print(f"❌ 指定されたディレクトリが見つかりません: {work_dir}")
        sys.exit(1)
    
    os.chdir(work_dir)
    print(f"📁 作業ディレクトリ: {work_dir}")
    
    # CSVファイルの存在確認
    csv_files = list(work_dir.glob("*.csv"))
    if not csv_files:
        print("❌ CSVファイルが見つかりません")
        print("📝 Scopus CSVファイルを作業ディレクトリに配置してください")
        sys.exit(1)
    
    print(f"✅ {len(csv_files)}個のCSVファイルを発見")
    
    try:
        if args.pdf_only:
            print("🎯 PDF取得のみ実行")
            run_pdf_tools(auto_mode=args.auto)
        elif args.pipeline_only:
            print("🎯 パイプライン処理のみ実行")
            run_pipeline(auto_mode=args.auto)
        else:
            print("🎯 完全実行モード")
            run_pipeline(auto_mode=args.auto)
            run_pdf_tools(auto_mode=args.auto)
        
        print("\n🎉 処理完了！")
        print("📂 結果を確認してください:")
        print("  - JSON_folder/: 文献メタデータ")
        print("  - md_folder/: Markdownファイル")
        print("  - PDF/: PDFファイル")
        
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()