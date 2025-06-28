# Scopus Literature Visualization Pipeline

DOIからの完全メタデータ取得と自動キーワード分析による文献可視化システム

## 機能概要

### 主要機能
- **完全なDOI情報取得**: Crossref APIから20+フィールドの詳細メタデータを取得
- **自動キーワード分析**: DOI・参考文献から3分類でキーワードを自動抽出
- **Markdown構造化出力**: 検索可能なタグ付き文献ファイル生成
- **参考文献相互リンク**: 2000+件のDOI参考文献を自動解決してリンク化

### 処理フロー
1. **CSV結合** → 複数Scopus CSVファイルを統合
2. **DOI解決** → 完全メタデータ取得（著者、出版社、雑誌等）
3. **Markdown生成** → タグ付き構造化文献ファイル
4. **キーワード拡張** → 自動キーワード分析・分類
5. **最終統合** → 検索可能な文献データベース完成

## 実行方法

### 基本実行
```bash
python main.py
```

### 個別実行
```bash
# 1. CSV結合
python combine_scopus_csv.py

# 2. DOI→JSON変換（改修版）
python scopus_doi_to_json.py

# 3. JSON→Markdown変換
python json2tag_ref_scopus_async.py

# 4. Abstract追記
python add_abst_scopus.py

# 5. キーワード拡張
python enhance_keywords.py

# 6. Markdownキーワード更新
python update_markdown_keywords.py
```

## 必要なファイル

### 入力データ
- Scopus CSVファイル（複数可）を同じフォルダに配置

### 依存関係
- Python 3.8+
- pandas, requests, requests_cache, tqdm
- aiohttp, async_timeout, nltk

## 出力成果物

### JSONファイル (JSON_folder/)
完全なメタデータ付き文献情報：
- 基本情報（タイトル、年、DOI、アブストラクト）
- 著者情報（名前、所属機関）
- 出版情報（出版社、雑誌、巻号、ページ）
- 識別子（ISSN、ISBN、URL）
- 引用情報（被引用数、参考文献数）
- **キーワード分析結果**

### Markdownファイル (md_folder/)
検索可能な構造化文献：
- タグ付きタイトル
- アブストラクト
- **キーワード分析セクション**
  - 主要キーワード（ハッシュタグ形式）
  - 内容分析キーワード
  - 関連研究キーワード
- 参考文献相互リンク
- DOI情報

## 新機能（改修版）

### DOI完全メタデータ取得
従来の5フィールドから**20+フィールド**に拡張：
- 著者情報、所属機関
- 出版社、雑誌名、巻号
- 被引用数、ライセンス情報
- Crossref完全レスポンス保存

### 自動キーワード分析
- **Crossrefキーワード**: DOIメタデータから分野キーワード
- **内容分析キーワード**: タイトル・アブストラクト分析
- **関連研究キーワード**: 2000+参考文献から推薦

## ファイル構成

```
├── main.py                          # メインパイプライン
├── combine_scopus_csv.py            # CSV結合
├── scopus_doi_to_json.py           # DOI→JSON（改修版）
├── json2tag_ref_scopus_async.py    # JSON→Markdown
├── add_abst_scopus.py              # Abstract追記
├── enhance_keywords.py             # キーワード拡張（新機能）
├── update_markdown_keywords.py     # Markdownキーワード更新（新機能）
├── requirements.md                 # 要件定義書
├── work_log.md                     # 作業記録
└── CLAUDE.md                       # Claude作業引き継ぎガイド
```

## 実行例

31件の論文処理結果：
- **27件のJSONファイル**（完全メタデータ）
- **27件のMarkdownファイル**（キーワード分析付き）
- **2012件のDOI参考文献**を自動解決
- **平均20個のキーワード**を自動分類

## ライセンス

このプロジェクトは教育・研究目的で開発されました。

## 貢献者

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>