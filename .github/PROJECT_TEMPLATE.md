# 🗂️ GitHub Projects 設定ガイド

## プロジェクト作成手順

### 1. 新しいプロジェクト作成
1. リポジトリページ → 「Projects」タブ
2. 「New project」をクリック
3. 「Table」レイアウトを選択
4. プロジェクト名：「Scopus文献可視化システム - 開発ロードマップ」

### 2. フィールド設定
```
必須フィールド：
- Status (Single select)
- Priority (Single select) 
- Size (Single select)
- Type (Single select)
```

### 3. Status オプション
```
📋 Backlog      - アイデア・要求段階
🎯 Ready        - 実装準備完了
⚡ In Progress  - 開発中
👀 Review       - レビュー・テスト中
✅ Done         - 完了
❌ Cancelled    - キャンセル
```

### 4. Priority オプション
```
🔴 Critical  - 緊急修正必要
🟠 High      - 高優先度
🟡 Medium    - 中優先度  
🟢 Low       - 低優先度
⚪ TBD       - 優先度未定
```

### 5. Size オプション
```
🐭 XS - 1時間以内
🐱 S  - 半日以内
🐶 M  - 1-2日
🐺 L  - 1週間
🐻 XL - 1ヶ月以上
```

### 6. Type オプション
```
🐛 Bug        - バグ修正
✨ Feature    - 新機能
📚 Docs       - ドキュメント
🔧 Maintenance - メンテナンス
🧪 Research   - 調査・研究
```

## 初期タスク例

### v2.1 リリース予定
```markdown
## 🐛 バグ修正 (Priority: High)
- [ ] PDF取得時のタイムアウトエラー修正
- [ ] 大量CSV処理時のメモリリーク対応
- [ ] 日本語文字化け修正

## ✨ 新機能 (Priority: Medium)  
- [ ] PubMed データベース対応
- [ ] 引用ネットワーク可視化
- [ ] 批判的閲覧ツール統合

## 📚 ドキュメント (Priority: Low)
- [ ] チュートリアル動画作成
- [ ] API リファレンス整備
- [ ] 使用事例集作成
```

### v3.0 長期計画
```markdown
## 🌐 Web化 (Priority: TBD)
- [ ] Flask/Django Web UI開発
- [ ] リアルタイム進行状況表示
- [ ] オンライン実行環境

## 🔬 研究機能拡張 (Priority: TBD)
- [ ] 機械学習による関連論文推薦
- [ ] 自動レビュー生成
- [ ] 研究トレンド分析
```

## ビュー設定

### 1. ロードマップビュー
```
グループ化: Status
ソート: Priority (High → Low)
フィルタ: Type != "Maintenance"
```

### 2. スプリントビュー  
```
グループ化: Priority
ソート: Size (XS → XL)
フィルタ: Status = "Ready" OR "In Progress"
```

### 3. 完了レポートビュー
```
グループ化: Type
ソート: 完了日 (新しい順)
フィルタ: Status = "Done"
```

## 自動化設定

### 1. Issue → Project 自動追加
```yaml
# .github/workflows/add-to-project.yml
name: Add to project
on:
  issues:
    types: [opened]
jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v0.4.0
        with:
          project-url: https://github.com/users/USERNAME/projects/PROJECT_NUMBER
          github-token: ${{ secrets.ADD_TO_PROJECT_PAT }}
```

### 2. PR マージ時の自動 Done 移動
```yaml
# Status を自動で Done に変更
```

---

**💡 ヒント**: GitHub Projects (Beta) は従来の Projects より高機能です。新しい方を使用することを強く推奨します。