# Scopus文献可視化システム

Scopusの文献データからMarkdownファイルとPDFを自動取得する日本語対応システムです。

## 📋 機能概要

- **📊 文献データ解析**: ScopusCSVからDOI情報を完全取得
- **📝 Markdown生成**: 参考文献リンク付きの構造化文書作成  
- **🔍 キーワード分析**: 自動キーワード抽出・分類
- **📄 PDF取得**: オープンアクセス・ResearchGate対応
- **🏷️ メタデータ**: YAML形式でObsidian/Zotero対応

## 🚀 クイックスタート

### 1. メイン解析実行
```bash
python3 core/scopus解析.py
```

### 2. PDF取得
```bash
python3 pdf_tools/PDF取得.py
```

### 3. クリーンアップ（必要時）
```bash
python3 utils/クリーンアップ.py
```

## 📁 ファイル構成

```
📦 プロジェクト/
├── 📁 core/              # メイン機能
│   └── scopus解析.py      # メイン実行スクリプト
├── 📁 pdf_tools/          # PDF取得機能  
│   └── PDF取得.py         # PDF取得専用ツール
├── 📁 utils/              # ユーティリティ
│   └── クリーンアップ.py   # ファイル整理
├── 📁 GFM_rev/            # 入力データ
├── 📁 JSON_folder/        # 生成されるJSONファイル
├── 📁 md_folder/          # 生成されるMarkdownファイル
├── 📁 PDF/                # 取得されるPDFファイル
└── README_日本語.md       # このファイル
```

## 🎯 使用方法

### Step 1: 文献解析実行

```bash
python3 core/scopus解析.py
```

**実行オプション:**
1. **完全実行** - CSV結合→DOI取得→Markdown生成→キーワード→YAML
2. **DOI情報のみ更新** - 最新のDOI情報取得
3. **Markdownのみ再生成** - 既存JSONからMarkdown作成
4. **キーワード分析のみ** - キーワード抽出・更新
5. **YAMLメタデータのみ** - フロントマター追加

### Step 2: PDF取得

```bash
python3 pdf_tools/PDF取得.py
```

**取得方法:**
1. **オープンアクセス論文（高速版）** - 8スレッド並列処理
2. **ResearchGate検索取得** - 積極的PDF検索
3. **オープンアクセス論文（標準版）** - 標準速度版
0. **全ての方法を順次実行** - 全方法自動実行

### Step 3: クリーンアップ（必要時）

```bash
python3 utils/クリーンアップ.py
```

自動生成ファイルを削除して、クリーンな状態から再実行できます。

## 🔧 技術仕様

### 対応形式
- **入力**: Scopus CSV形式
- **出力**: Markdown (YAML frontmatter付き)、JSON、PDF
- **API**: Crossref、Unpaywall、ResearchGate

### 処理能力
- **並列処理**: 最大8スレッド
- **DOI解決**: 500件/チャンク
- **キーワード**: 自動分類（主要/内容/関連研究）

### 生成ファイル例

**Markdownファイル構成:**
```markdown
---
title: "論文タイトル"
doi: "10.1000/xxxxx"
year: 2023
authors: ["著者1", "著者2"]
keywords: ["keyword1", "keyword2"]
---

## Abstract
論文要約...

## キーワード分析
### 主要キーワード
#keyword1 #keyword2

## 論文情報  
**DOI**: 10.1000/xxxxx
**雑誌**: Journal Name

## PDF
**フルテキストPDF**: [📄 filename.pdf](PDF/filename.pdf)

## 参考文献
- [[Reference1]]
- [[Reference2]]
```

## 🔍 トラブルシューティング

### よくある問題

1. **CSVファイルが見つからない**
   ```
   GFM_rev/scopus_gfm_rev.csv を確認してください
   ```

2. **PDFダウンロードに失敗**
   ```
   オープンアクセス論文のみ取得可能です
   ResearchGateオプションをお試しください
   ```

3. **キーワードが表示されない**
   ```
   キーワード分析を個別実行してください
   ```

### ログファイル
- `error_log.txt` - エラーログ
- `doi_title_cache.json` - DOIキャッシュ
- `crossref_cache.sqlite` - Crossrefキャッシュ

## 📊 パフォーマンス

### 処理速度目安
- **DOI取得**: 100件/分
- **Markdown生成**: 50件/分  
- **PDF取得**: 10件/分（成功分のみ）

### システム要件
- Python 3.7+
- インターネット接続
- 500MB以上の空き容量

## 🎨 カスタマイズ

### キーワード分析調整
`enhance_keywords.py` の設定:
```python
min_freq = 2        # 最小出現頻度
top_n = 20         # 上位N個のキーワード
```

### PDF取得設定
`download_researchgate_pdfs.py` の設定:
```python
max_workers = 3     # 同時実行数
timeout = 30       # タイムアウト秒数
```

## 📞 サポート

システムの使用に関する質問やバグ報告は、プロジェクト管理者までお問い合わせください。

---

**更新日**: 2025-06-29  
**バージョン**: 2.0.0  
**対応言語**: 日本語・英語