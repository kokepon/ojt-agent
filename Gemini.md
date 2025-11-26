# コミットメッセージ ガイドライン（Conventional Commits）

## フォーマット

```
<type>[scope][!]: <subject>

[body]

[footer]
```

## Type（必須・英語）

- `feat`: 新機能追加
- `fix`: バグ修正
- `docs`: ドキュメントのみ
- `style`: フォーマット等（挙動に影響なし）
- `refactor`: 挙動を変えない構造変更
- `perf`: パフォーマンス改善
- `test`: テスト関連
- `build`: ビルドや依存関係の変更
- `ci`: CI 設定変更
- `chore`: その他雑務
- `revert`: コミット取り消し

## ルール

- **Subject**: 日本語、50文字以内、過去形禁止、句読点なし
- **Body**: 任意、「なぜ」「どのように」を説明
- **Footer**: `BREAKING CHANGE:`, `Closes: #123`, `Refs: #456` など
- **破壊的変更**: `type!:` または `BREAKING CHANGE:` で明示

## 例

```
feat: ログイン機能を追加

fix: 交差検証時のデータリークを修正

refactor: モデル学習処理を関数に抽出

build: 依存パッケージを更新

feat(auth)!: リフレッシュトークンの形式を変更

BREAKING CHANGE: 既存トークンは無効になり再ログインが必要

Closes: #99
```

