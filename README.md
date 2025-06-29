# Scopus文献可視化システム

Scopus論文データベースから取得した文献情報を可視化するパイプラインシステム。DOIを基にCrossref APIから完全な文献メタデータを取得し、Markdown形式で構造化された文献データベースを生成します。

## 🎯 主要機能

### ✅ 完成済み機能
- **CSVファイル結合**: 複数のScopusCSVファイルを統合
- **DOI完全情報取得**: Crossref APIから20+フィールドの詳細メタデータ取得
- **Markdown生成**: YAMLフロントマター + 参考文献相互リンク機能
- **キーワード自動分析**: 3カテゴリ（Crossref/内容/関連研究）での分類
- **オープンアクセスPDF取得**: Unpaywall API + 直接アクセス
- **学術データベース品質**: Obsidian、Zotero等で活用可能

### 処理フロー
1. **CSV結合** → 複数Scopus CSVファイルを統合
2. **DOI解決** → 完全メタデータ取得（著者、出版社、雑誌等）
3. **Markdown生成** → YAMLフロントマター付き構造化文献ファイル
4. **キーワード拡張** → 自動キーワード分析・分類
5. **PDF取得** → オープンアクセス論文の自動ダウンロード
6. **最終統合** → 学術データベース品質の文献システム完成

## 📁 システム構成

```
📦 Scopus文献可視化システム/
├── 📁 core/                    # メイン機能
│   └── scopus解析.py            # 日本語メイン実行スクリプト
├── 📁 pdf_tools/               # PDF取得機能
│   ├── download_open_access_pdfs.py      # オープンアクセス論文取得
│   ├── download_open_access_pdfs_fast_stdlib.py  # 高速版
│   ├── download_researchgate_pdfs.py     # ResearchGate検索
│   └── PDF取得.py              # 日本語PDF取得スクリプト
├── 📁 utils/                   # ユーティリティ
│   └── クリーンアップ.py         # ファイル整理ツール
├── 📁 GFM_rev/                 # 入力データ
│   └── scopus_gfm_rev.csv      # Scopus CSVファイル
├── 📁 JSON_folder/             # 生成JSONファイル (27件)
├── 📁 md_folder/               # 生成Markdownファイル (27件)
├── 📁 PDF/                     # 取得PDFファイル (2件)
├── combine_scopus_csv.py       # CSV結合
├── scopus_doi_to_json.py       # DOI→JSON変換
├── json2tag_ref_scopus_async.py # JSON→Markdown変換
├── enhance_keywords.py         # キーワード分析
├── update_markdown_keywords.py # キーワード更新
├── add_yaml_metadata.py        # YAMLメタデータ追加
└── main.py                     # 英語版メインスクリプト
```

## 🚀 使用方法

### 基本的な使用手順

1. **メイン処理実行**
```bash
python3 core/scopus解析.py
```
選択できるオプション：
- `1. 完全実行`: CSV結合→DOI取得→Markdown生成→キーワード→YAML
- `2. DOI情報のみ更新`: 最新のDOI情報取得
- `3. Markdownのみ再生成`: 既存JSONからMarkdown作成
- `4. キーワード分析のみ`: キーワード抽出・更新
- `5. YAMLメタデータのみ`: フロントマター追加

2. **PDF取得実行**
```bash
python3 pdf_tools/PDF取得.py
```
選択できる方法：
- `1. オープンアクセス論文（高速版）`: 8スレッド並列処理
- `2. ResearchGate検索取得`: 積極的PDF検索
- `3. オープンアクセス論文（標準版）`: 標準速度版
- `0. 全ての方法を順次実行`: 全方法自動実行

### 個別スクリプト実行

```bash
# CSV結合
python3 combine_scopus_csv.py

# DOI情報取得
python3 scopus_doi_to_json.py

# Markdown生成
python3 json2tag_ref_scopus_async.py

# キーワード分析
python3 enhance_keywords.py

# YAMLメタデータ追加
python3 add_yaml_metadata.py
```

## 📋 要件

### 必須要件
- Python 3.7+
- インターネット接続（Crossref API, Unpaywall API使用）

### 推奨ライブラリ
- `aiohttp`: 高速並列処理（オプション）
- `nltk`: キーワード分析（オプション）

### 入力ファイル
- `GFM_rev/scopus_gfm_rev.csv`: Scopus CSVファイル

## 📊 出力

### 生成されるファイル
- **JSON_folder/**: 完全なメタデータ付き文献情報（27件）
- **md_folder/**: YAMLフロントマター付きMarkdownファイル（27件）
- **PDF/**: オープンアクセスPDFファイル（取得可能分）
- **doi_title_cache.json**: DOI解決キャッシュ
- **crossref_cache.sqlite**: Crossref APIキャッシュ

### Markdownファイルの特徴
- **YAMLフロントマター**: タイトル、DOI、著者、雑誌、キーワード等
- **論文情報セクション**: DOI、発行年、雑誌、巻号、ページ
- **キーワード分析**: 自動抽出された20個程度のキーワード
- **参考文献相互リンク**: DOI解決による相互参照
- **PDF埋め込み**: 取得済みPDFの表示・ダウンロードリンク

## 🛠️ システム管理

### ファイル整理
```bash
python3 utils/クリーンアップ.py
```
自動生成ファイルを削除して最初からやり直す場合に使用

### 作業記録
- **requirements.md**: プロジェクト要件定義書
- **work_log.md**: 詳細作業記録
- **CLAUDE.md**: Claude作業引き継ぎガイド

## 🎯 技術的特徴

### API統合
- **Crossref API**: 完全な文献メタデータ取得
- **Unpaywall API**: オープンアクセス論文検出
- **ResearchGate検索**: 積極的PDF検索

### データ品質
- **完全なDOI情報**: 著者、所属、出版社、識別子等20+フィールド
- **キーワード分析**: 3カテゴリでの自動分類・推薦
- **相互リンク機能**: 参考文献間の相互参照
- **学術標準対応**: Obsidian、Zotero等での活用可能

### パフォーマンス
- **非同期処理**: 大量DOI解決の高速化
- **キャッシュ機能**: 重複処理の回避
- **並列処理**: PDF取得の効率化
- **エラーハンドリング**: 堅牢な処理継続

## 📈 処理実績

- **論文数**: 31件 → 27件のJSONファイル生成
- **参考文献**: 2012個のDOI処理（500件ずつ5チャンク）
- **Markdownファイル**: 27件（YAMLメタデータ完備）
- **PDFファイル**: 2件のオープンアクセス論文取得
- **キーワード**: 平均20個/論文の自動抽出

## 🔧 トラブルシューティング

### よくある問題
1. **CSVファイルが見つからない**: `GFM_rev/scopus_gfm_rev.csv`の存在確認
2. **NLTKエラー**: キーワード分析をスキップするか別途インストール
3. **PDF取得失敗**: オープンアクセス論文が少ないため正常
4. **権限エラー**: フォルダの書き込み権限確認

## 📄 ライセンス

学術研究用途での使用を想定しています。APIの利用規約を遵守してください。

---

**🎉 プロジェクト完成**: 100%機能実装済み・本番運用可能

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>