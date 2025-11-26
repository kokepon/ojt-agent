---

【結論】
あなたのやりたい「OJTしながら知識をためて、後でgeminiが使えるようにする」仕組みは、
**JSONL で知識を蓄積 → 承認済みに昇格 → ベクトル化 → RAGサーバー → MCPサーバー**
という5層構造に分解することで、既存ライブラリの組み合わせで現実的に構築できる。

---

【全体像】
構造はこの3段階。

1. **知識をためる層（JSONL）**

   * glossary.jsonl
   * datasets.jsonl
   * rules.jsonl
   * analyses.jsonl
   * 生データは `raw/` に、レビュー後は `approved/` に移動。

2. **RAG層（ベクトル化・検索API）**

   * approved の JSONL を embedding
   * Chroma か PostgreSQL+pgvector に格納
   * LlamaIndex か LangChain で検索用APIを構築
   * `/query` で関連知識を返す FastAPI サーバーを立てる

3. **MCP層（gemini から叩けるAPI）**

   * Python の MCP SDK を使って MCP サーバーを実装
   * gemini はこの MCP サーバー経由で “search_knowledge” ツールを利用
   * 実態は ② の RAG サーバーを叩いているだけ

---

【① JSONL層：やること】

* `ai_knowledge/raw/` に解析中にどんどん追記
* `ai_knowledge/approved/` に、人間レビュー後の確定知識を移動
* スキーマを pydantic で固定
* CLI コマンド：

  * `validate-knowledge`（raw をバリデーション）
  * `promote-knowledge`（approved へ移動）

必要ライブラリ：pydantic（これだけで十分）

---

【② RAG層：やること】

目的は「approved の JSONL を全部 embed → ベクトルDB → /query API」。
これは次のセットが最強で最も簡単：

* **ベクトルDB：Chroma**（pipだけで入るので最速）
  あるいは Postgres + pgvector（社内環境が整ってるなら強力）

* **ラッパー：LlamaIndex**
  JSON レコードをそのまま扱いやすい。構造化データ向け。

* **API：FastAPI**
  `/query` で質問を受けて、上位K件の知識レコードを返す。

CLI コマンド：

* `build-rag-index`（approved → embedding → DB）
* `serve-rag`（FastAPI 起動）

---

【③ MCP層：やること】

* MCP サーバーを Python 公式 SDK で作る
* “search_knowledge” という MCP ツールを定義
* 内部で ② の RAG API `/query` を叩くだけ
* gemini は MCP 経由でこのツールを呼ぶ
  → あたかも「会社専用の知識がgeminiに統合されてる」状態になる

CLI：

* `serve-mcp`（MCP サーバー起動）

---

【推奨ライブラリまとめ】

（必須）

* **pydantic**（JSONLスキーマ）
* **Chroma**（ベクトルDB）
* **LlamaIndex**（RAG）
* **FastAPI / Uvicorn**（APIサーバー）
* **modelcontextprotocol（MCP SDK）**

（オプション）

* PostgreSQL + pgvector

---

【やる順番（ここが一番重要）】

あなたが失敗するパターンを排除して、順序を固定する。

1. **JSONL スキーマと raw/approved 運用を確立**
   これができない限り何をしても破綻する。

2. **RAG インデックス＋検索APIを作る**
   ここまでで「Pythonからドメイン知識を検索して解析を補助」できる。

3. **MCPサーバーを実装し、gemini に接続**
   これは UX 向上フェーズ。最後でいい。

---

【端的な結論】
あなたの OJT エージェント構想は、
**知識の構造化、承認フロー、ベクトル化、RAG、MCP**
の5フェーズに分ければ完全に実現できる。
全て既存ライブラリで戻り道なしに組める。
