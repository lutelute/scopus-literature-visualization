# Scopus文献可視化システム

Scopus論文データベースから取得した文献情報を可視化するパイプラインシステム。DOIを基にCrossref APIから完全な文献メタデータを取得し、Markdown形式で構造化された文献データベースを生成します。

## 🎯 主要機能

### ✅ 完成済み機能
- **CSVファイル結合**: 複数のScopusCSVファイルを統合
- **DOI完全情報取得**: Crossref APIから20+フィールドの詳細メタデータ取得
- **Markdown生成**: YAMLフロントマター + 参考文献相互リンク機能
- **キーワード自動分析**: 3カテゴリ（Crossref/内容/関連研究）での分類
- **オープンアクセスPDF取得**: Unpaywall API + 直接アクセス
- **メール完了通知**: 処理完了時の自動メール通知（オプション）
- **学術データベース品質**: Obsidian、Zotero等で活用可能

### 処理フロー
1. **CSV結合** → 複数Scopus CSVファイルを統合
2. **DOI解決** → 完全メタデータ取得（著者、出版社、雑誌等）
3. **Markdown生成** → YAMLフロントマター付き構造化文献ファイル
4. **キーワード拡張** → 自動キーワード分析・分類
5. **PDF取得** → オープンアクセス論文の自動ダウンロード
6. **メール通知** → 処理完了時の自動通知（オプション）
7. **最終統合** → 学術データベース品質の文献システム完成

## 📁 使用方法

### 典型的なワークフロー
```
📁 my_research_project/           # ユーザーが作成する作業フォルダ
├── scopus_export_1.csv          # Scopus CSVファイル（複数可）
├── scopus_export_2.csv
└── 📁 scopus-literature-visualization/  # クローンしたツール
    ├── 📁 core/                  # メイン機能
    ├── 📁 pdf_tools/             # PDF取得機能
    ├── 📁 utils/                 # ユーティリティ
    ├── combine_scopus_csv.py     # CSV結合
    ├── scopus_doi_to_json.py     # DOI→JSON変換
    ├── json2tag_ref_scopus_async.py # JSON→Markdown変換
    └── 他のファイル...

実行後:
├── scopus_combined.csv          # 結合されたCSV
├── 📁 JSON_folder/              # 生成JSONファイル
├── 📁 md_folder/                # 生成Markdownファイル
├── 📁 PDF/                      # 取得PDFファイル
└── doi_title_cache.json         # DOI解決キャッシュ
```

## 🚀 使用方法

### 🎯 ワンコマンド全自動実行（推奨）

**🔧 初回セットアップ（1回だけ）**
```bash
# 1. セットアップ実行（仮想環境作成＋パッケージインストール）
python3 setup.py

# 2. 仮想環境アクティベート＋全自動実行
source .venv/bin/activate && python3 全自動実行.py
```

**⚡ 2回目以降（簡単）**
```bash
# 仮想環境アクティベート + 全自動実行
source .venv/bin/activate && python3 全自動実行.py
```

**🤖 さらに簡単（自動セットアップ）**
```bash
# setup.py を先に実行せずに全自動実行（推奨）
python3 全自動実行.py
# → 仮想環境がなければ自動でsetup.pyを実行
```

**処理内容**:
1. 仮想環境チェック・自動作成
2. 環境チェック・依存関係確認
3. CSVファイル結合
4. DOI完全情報取得
5. Markdown生成・参考文献解決
6. キーワード分析・抽出
7. YAMLメタデータ追加
8. メール完了通知設定（オプション）

**実行例**:
```
🚀 Scopus文献可視化システム - 全自動実行
============================================================
✅ 仮想環境がアクティブです
✅ 必須パッケージは全てインストール済み
✅ 1個のCSVファイルを発見: scopus_export.csv
✅ 2️⃣  CSVファイル結合 完了 (0.6秒)
✅ 3️⃣  DOI完全情報取得 完了 (7.4秒)
✅ 4️⃣  Markdown生成・参考文献解決 完了 (0.3秒)
✅ 5️⃣  キーワード分析・抽出 完了 (1.6秒)
✅ 6️⃣  YAMLメタデータ追加 完了 (0.0秒)

🎯 完全成功! 学術文献データベースが完成しました
📂 md_folder/ で Markdown ファイルを確認してください
```

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

3. **メール通知設定（オプション）**
```bash
python3 メール設定.py
```
利用可能な操作：
- `1. メール設定セットアップ`: Gmail/Outlook対応
- `2. 設定状況確認`: 現在の設定確認
- `3. テストメール送信`: 接続テスト
- `4. 設定削除`: メール設定削除

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

## 📋 要件・セットアップ

### クイックスタート（推奨）
```bash
# 1. 作業フォルダを作成してCSVファイルを配置
mkdir my_research_project
cd my_research_project
# ここにScopus CSVファイルをコピー

# 2. ツールをクローン
git clone https://github.com/lutelute/scopus-literature-visualization.git
cd scopus-literature-visualization

# 3. 全自動実行（仮想環境も自動作成）
python3 全自動実行.py
# → 初回は仮想環境作成から自動実行

# 4. 2回目以降は仮想環境アクティベート＋実行
source .venv/bin/activate && python3 全自動実行.py
```

### 手動セットアップ（上級者向け）
```bash
# 依存関係手動インストール
python3 setup.py

# 仮想環境アクティベート（.venvが存在する場合）
source .venv/bin/activate

# メインスクリプト実行
python3 core/scopus解析.py
```

### 必須要件
- **Python 3.7+**
- **インターネット接続**（Crossref API, Unpaywall API使用）

### 自動インストールされる依存関係
- `pandas`: CSVデータ処理
- `requests`: API通信
- `requests_cache`: API結果キャッシュ
- `tqdm`: 進行状況表示

### オプションライブラリ（自動検出・推奨）
- `aiohttp`: 高速並列処理
- `nltk`: キーワード分析

### 入力ファイル
- **作業フォルダ内の*.csv**: Scopus エクスポートCSVファイル（複数可）

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
1. **CSVファイルが見つからない**: 作業フォルダにScopus CSVファイルがあるか確認
2. **NLTKエラー**: キーワード分析をスキップするか `pip install nltk` でインストール
3. **PDF取得失敗**: オープンアクセス論文が少ないため正常（数件程度は一般的）
4. **権限エラー**: 作業フォルダの書き込み権限確認
5. **メール送信失敗**: Gmailアプリパスワード設定、SMTP接続確認

### セキュリティ情報
- **メール設定**: ローカルファイル（.email_config.json）に平文保存
- **推奨設定**: Gmailアプリパスワード使用（通常パスワード非推奨）
- **設定ファイル**: .gitignoreに追加済み（リポジトリに含まれません）

## 📄 ライセンス

学術研究用途での使用を想定しています。APIの利用規約を遵守してください。

---

**🎉 プロジェクト完成**: 100%機能実装済み・本番運用可能

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>