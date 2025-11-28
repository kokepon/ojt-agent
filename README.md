# OJT Agent

## 概要
OJTエージェントシステムの実装プロジェクトです。
このシステムは、知識の蓄積 (JSONL)、検索 (RAG/Qdrant)、および Gemini からの利用 (MCP) を実現します。

## セットアップ
1. **依存関係のインストール**:
   ```bash
   uv sync
   ```
2. **環境変数の設定**:
   `.env` ファイルを作成し、必要な環境変数を設定してください（現在はGoogle API Keyは不要ですが、将来的な拡張のために残しておく場合があります）。
3. **Qdrantの起動**:
   ```bash
   docker-compose up -d
   ```

## 使い方

### 1. 知識の蓄積 (CLI)
AIエージェントやユーザーが知識を追加する場合、以下のコマンドを使用します。
```bash
uv run python -m src.cli add '{"term": "...", "definition": "..."}' --type glossary
```

**指定可能な `--type`**:
- `glossary`: 用語集 (必須フィールド: `term`, `definition`)
- `dataset`: データセット (必須フィールド: `name`, `description`)
- `rule`: ルール (必須フィールド: `title`, `rule_content`)
- `analysis`: 分析結果 (必須フィールド: `title`, `summary`, `findings`)

### 2. 知識のバリデーション
**単一ファイルのチェック**:
```bash
uv run python -m src.cli validate ai_knowledge/raw/glossary.jsonl --type glossary
```

**一括チェック** (ai_knowledge/raw 内の全ファイルを検証):
```bash
uv run python -m src.cli validate
```

### 3. 知識の承認（手動）
`ai_knowledge/raw/` から `ai_knowledge/approved/` にファイルを移動します。

### 4. インデックス作成
```bash
uv run python -m src.cli build-index
```

### 5. インデックスのリセット
埋め込みモデルを変更した場合や、インデックスを初期化したい場合に使用します。
```bash
uv run python -m src.cli reset-index
```

### 6. 検索（テスト）
```bash
uv run python -m src.cli search "RAGとは？"
```

### 7. MCPサーバー起動
Gemini から利用するためにサーバーを起動します。
```bash
uv run python -m src.cli serve-mcp
```

### 8. Gemini CLIへの登録 (MCPサーバー設定)
Gemini CLI (または他のMCPクライアント) の設定ファイル (例: `~/.gemini/config.json` やクライアント固有の設定) に、以下のサーバー設定を追加してください。

```json
{
  "mcpServers": {
    "ojt-agent": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "src.cli",
        "serve-mcp"
      ],
      "cwd": "c:/Users/fadec/Desktop/dsenv/ai-ojt"
    }
  }
}
```
> **注意**: `cwd` はプロジェクトの絶対パスを指定してください。

## ファイル構成
- `src/schemas.py`: 知識データのスキーマ定義
- `src/knowledge_manager.py`: バリデーションロジック
- `src/rag_engine.py`: RAGエンジン (LlamaIndex + Qdrant + HuggingFace Embeddings + Retriever Mode)
- `src/mcp_server.py`: MCPサーバー実装
- `src/cli.py`: コマンドラインツール
- `.gemini/commands/`: Gemini CLI用カスタムコマンド (TOML)

## 埋め込みモデルについて
プライバシー保護のため、埋め込みモデルにはローカルで動作する `intfloat/multilingual-e5-large` (HuggingFace) を使用しています。
初回実行時（`build-index` または `search`）にモデルのダウンロード（約2GB）が行われます。
