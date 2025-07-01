#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline runner for Scopus Literature Visualization
"""

import os
import subprocess
import sys
from pathlib import Path


def run_pipeline(auto_mode=False):
    """パイプライン実行"""
    
    # 実行スクリプトリスト
    scripts = [
        "combine_scopus_csv.py",
        "scopus_doi_to_json.py", 
        "json2tag_ref_scopus_async.py",
        "add_abst_scopus.py",
        "enhance_keywords.py",
        "add_yaml_metadata.py"
    ]
    
    print("🚀 Scopus文献可視化パイプライン開始")
    print("=" * 50)
    
    for i, script in enumerate(scripts, 1):
        script_path = Path(script)
        if not script_path.exists():
            print(f"⚠️ スクリプトが見つかりません: {script}")
            continue
            
        print(f"\n{i}️⃣ {script} 実行中...")
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                check=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                print(result.stdout)
            
            print(f"✅ {script} 完了")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {script} でエラーが発生しました")
            print(f"終了コード: {e.returncode}")
            if e.stderr:
                print(f"エラー詳細: {e.stderr}")
            if not auto_mode:
                user_input = input("続行しますか？ (y/n): ").lower()
                if user_input != 'y':
                    break
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            if not auto_mode:
                user_input = input("続行しますか？ (y/n): ").lower()
                if user_input != 'y':
                    break
    
    print("\n✨ パイプライン完了")


def main():
    """パイプライン単体実行用メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scopus Literature Visualization Pipeline')
    parser.add_argument('--auto', action='store_true', help='自動実行モード')
    args = parser.parse_args()
    
    run_pipeline(auto_mode=args.auto)


if __name__ == "__main__":
    main()