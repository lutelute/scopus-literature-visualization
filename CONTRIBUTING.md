# 🤝 コントリビューションガイド

Scopus文献可視化システムへの貢献をありがとうございます！

## 📋 貢献方法

### 1. Issues
- **バグ報告**: [Bug Report テンプレート](.github/ISSUE_TEMPLATE/bug_report.md)を使用
- **機能提案**: [Feature Request テンプレート](.github/ISSUE_TEMPLATE/feature_request.md)を使用
- **質問・議論**: [Discussions](https://github.com/lutelute/scopus-literature-visualization/discussions)を活用

### 2. Pull Requests
1. リポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を作成

## 🛠️ 開発環境セットアップ

```bash
# リポジトリクローン
git clone https://github.com/lutelute/scopus-literature-visualization.git
cd scopus-literature-visualization

# 開発環境セットアップ
python3 setup.py

# 開発ツール実行
python3 dev_tools/テスト実行.py
```

## 📝 コーディング規約

### Python スタイル
- **PEP 8** に準拠
- **日本語変数名・関数名** 推奨（学術ツールとして理解しやすさ優先）
- **型ヒント** 可能な限り使用
- **docstring** 日本語で記述

### コミットメッセージ
```
[TYPE] 簡潔な変更内容

詳細な説明（必要に応じて）

## 変更内容
- 具体的な変更1
- 具体的な変更2

## テスト
- 実行したテスト内容

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

**TYPE例**: FEAT, FIX, DOCS, STYLE, REFACTOR, TEST

## 🧪 テスト

### 必須テスト
```bash
# システム構成テスト
python3 dev_tools/テスト実行.py

# 進行状況確認テスト
python3 dev_tools/進行状況確認.py
```

### 機能テスト（CSV必要）
```bash
# メイン機能テスト
python3 core/scopus解析.py

# PDF取得テスト
python3 pdf_tools/PDF取得.py
```

## 📚 ドキュメント

### 更新が必要なファイル
- **README.md**: 新機能追加時
- **requirements.txt**: 依存関係変更時
- **dev_tools/README.md**: 開発ツール変更時
- **work_log.md**: 重要な変更・修正時

## 🎯 重点分野

### 歓迎する貢献
1. **新しい学術データベース対応**
   - PubMed, arXiv, IEEE Xplore等
   
2. **PDF取得精度向上**
   - 新しいオープンアクセス検出方法
   - 学術出版社の直接アクセス
   
3. **多言語対応**
   - 非英語論文のキーワード分析
   - 出力の多言語化
   
4. **可視化機能**
   - 引用ネットワーク図
   - キーワード関係図
   
5. **Web UI**
   - ブラウザベースインターフェース
   - リアルタイム進行状況表示

### 技術的優先度
- **高**: API効率化、エラーハンドリング改善
- **中**: 新機能追加、UI改善
- **低**: リファクタリング、コメント追加

## 🏷️ ラベル

### Issue ラベル
- `bug`: バグ報告
- `enhancement`: 新機能・改善
- `documentation`: ドキュメント関連
- `good first issue`: 初心者向け
- `help wanted`: 支援募集
- `priority-high`: 高優先度
- `research`: 研究・調査が必要

### Pull Request ラベル
- `ready for review`: レビュー準備完了
- `work in progress`: 作業中
- `breaking change`: 破壊的変更

## 🤔 質問・サポート

- **技術的質問**: [GitHub Discussions](https://github.com/lutelute/scopus-literature-visualization/discussions)
- **バグ報告**: [Issues](https://github.com/lutelute/scopus-literature-visualization/issues)
- **機能提案**: [Issues](https://github.com/lutelute/scopus-literature-visualization/issues)

## 📜 ライセンス

このプロジェクトに貢献することで、あなたの貢献が同じライセンスの下で利用されることに同意したものとみなされます。

---

**🎉 あなたの貢献をお待ちしています！**