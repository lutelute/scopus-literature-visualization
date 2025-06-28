#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
combine_scopus_csv.py
---------------------
同フォルダ内の *.csv（scopus エクスポート）を 1 本に結合。
既に生成済みの scopus_combined.csv は対象外。
重複行は drop_duplicates で除去。
"""

import os, glob, pandas as pd

OUT_NAME = "scopus_combined.csv"

def main() -> None:
    base  = os.path.dirname(os.path.abspath(__file__))
    csvs  = [f for f in glob.glob(os.path.join(base, "*.csv"))
             if os.path.basename(f) != OUT_NAME]

    if not csvs:
        print("結合対象 CSV がありません")
        return

    df = pd.concat([pd.read_csv(f, dtype=str) for f in csvs],
                   ignore_index=True).fillna("")
    df.drop_duplicates(inplace=True)   # 完全一致を削除
    df.to_csv(os.path.join(base, OUT_NAME), index=False)

    print(f"{len(csvs)} ファイル → {len(df)} 行を {OUT_NAME} に保存しました")

if __name__ == "__main__":
    main()