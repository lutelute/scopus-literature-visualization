#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scopus_combined.csv から DOI / Abstract を md_folder の Markdown へ追記
"""
import os, unicodedata, pandas as pd

CSV_IN="scopus_combined.csv"; MD_DIR="md_folder"
SAFE_CHARS="-_.() "+''.join(chr(c) for c in range(0x30,0x3A))+''.join(chr(c) for c in range(0x41,0x5B))+''.join(chr(c) for c in range(0x61,0x7B))

def safe_filename(t:str,maxlen:int=120)->str:
    t=unicodedata.normalize('NFKC',t); return ''.join(ch if ch in SAFE_CHARS else '_' for ch in t)[:maxlen] or 'untitled'

def main():
    base=os.path.dirname(os.path.abspath(__file__))
    df=pd.read_csv(os.path.join(base,CSV_IN),dtype=str).fillna("")
    for _, r in df.iterrows():
        ttl=r.get('Title', r.get('タイトル','')).strip()
        if not ttl: continue
        md_p=os.path.join(base,MD_DIR, safe_filename(ttl)+'.md')
        if not os.path.exists(md_p): continue
        txt=open(md_p,encoding='utf-8').read()
        if '## DOI' in txt and '## Abstract' in txt: continue
        with open(md_p,'a',encoding='utf-8') as f:
            f.write("\n\n## DOI\n"+r.get('DOI','Unknown'))
            f.write("\n\n## Abstract\n"+r.get('Abstract', r.get('抄録','')))
    print("Abstract 追記完了")

if __name__=='__main__':
    main()
