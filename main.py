#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py  ―  Scopus パイプライン一括実行ドライバ（改良版）

同じフォルダに置いた 4 つのスクリプトを順番に呼び出します。
    1. combine_scopus_csv.py   : 複数 CSV → scopus_combined.csv
    2. scopus_doi_to_json.py   : DOI → JSON_folder/*.json
    3. json2tag_ref_scopus_async.py  : JSON → md_folder/*.md
    4. add_abst_scopus.py      : DOI / Abstract を Markdown 追記

実行後、成果物は md_folder/ に出力されます。
"""

import os
import subprocess
import sys

SCRIPTS = [
    "combine_scopus_csv.py",
    "scopus_doi_to_json.py",
    "json2tag_ref_scopus_async.py",
    "add_abst_scopus.py",
]

BASE = os.path.dirname(os.path.abspath(__file__))

print("\n=== Setting up virtual environment and installing required packages ===")
try:
    venv_dir = os.path.join(BASE, ".venv")
    if not os.path.isdir(venv_dir):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    # Activate venv (path will differ by shell, here we just call pip inside venv)
    pip_executable = os.path.join(venv_dir, "bin", "pip")
    # Upgrade pip and install packages
    subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)
    subprocess.run([pip_executable, "install", "pandas", "requests", "requests_cache", "tqdm"], check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ Environment setup failed with exit code {e.returncode}")
    print(f"Command: {e.cmd}")
    sys.exit(1)

for script in SCRIPTS:
    path = os.path.join(BASE, script)
    print(f"\n=== running {script} ===")
    try:
        subprocess.run([os.path.join(BASE, ".venv", "bin", "python"), path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ {script} failed with exit code {e.returncode}")
        print(f"Command: {e.cmd}")
        break
    except Exception as e:
        print(f"⚠️ Unexpected error during {script}: {e}")
        break
    else:
        print(f"✅ {script} completed successfully.")

print("\n✔️  Pipeline finished. Check the md_folder for results (if no error occurred).")