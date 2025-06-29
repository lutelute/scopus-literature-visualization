#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
combine_scopus_csv.py
---------------------
実行ディレクトリ内の *.csv（Scopus エクスポート）を 1 本に結合。
既に生成済みの scopus_combined.csv は対象外。
重複行は drop_duplicates で除去。

使用方法:
1. 作業フォルダを作成
2. そのフォルダ内にScopus CSVファイルを配置
3. このツールをクローン/実行
"""

import os, glob, pandas as pd

OUT_NAME = "scopus_combined.csv"

def main() -> None:
    # 実行ディレクトリ（ユーザーの作業フォルダ）でCSVファイルを検索
    work_dir = os.getcwd()
    print(f"📁 作業ディレクトリ: {work_dir}")
    
    csvs = [f for f in glob.glob(os.path.join(work_dir, "*.csv"))
            if os.path.basename(f) != OUT_NAME]
    
    print(f"🔍 検出されたCSVファイル: {len(csvs)}件")
    for csv_file in csvs:
        print(f"  - {os.path.basename(csv_file)}")

    if not csvs:
        print("❌ 結合対象のCSVファイルが見つかりません")
        print("💡 使用方法:")
        print("  1. 作業フォルダにScopus CSVファイルを配置")
        print("  2. その作業フォルダ内でこのツールを実行")
        return

    print(f"📊 CSVファイルを結合中...")
    df = pd.concat([pd.read_csv(f, dtype=str) for f in csvs],
                   ignore_index=True).fillna("")
    
    original_count = len(df)
    df.drop_duplicates(inplace=True)   # 完全一致を削除
    deduplicated_count = len(df)
    
    output_path = os.path.join(work_dir, OUT_NAME)
    df.to_csv(output_path, index=False)

    print(f"✅ 結合完了:")
    print(f"  📁 入力: {len(csvs)}ファイル")
    print(f"  📊 元データ: {original_count:,}行")
    print(f"  🔄 重複除去後: {deduplicated_count:,}行")
    print(f"  💾 出力: {OUT_NAME}")
    
    if original_count != deduplicated_count:
        print(f"  ⚠️  {original_count - deduplicated_count:,}行の重複を除去")

if __name__ == "__main__":
    main()