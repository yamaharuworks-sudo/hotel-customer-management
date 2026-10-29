# Hotel Customer Management

ホテルの顧客情報と宿泊履歴を管理するWebアプリケーションです。

## 主な機能

- 顧客情報の登録・編集・削除
- 顧客の検索・並び替え
- 宿泊履歴の登録・表示・削除
- 宿泊回数と最終宿泊日の表示
- 管理者ログイン認証

## 技術スタック

| 分類 | 使用技術 |
|---|---|
| Frontend | Vue 3 / Vite / JavaScript |
| Backend | Python / FastAPI |
| Database | PostgreSQL |
| Container | Docker / Docker Compose |
| Deployment | Render |

## 開発環境

Docker Composeを使用して、以下の3つのサービスを起動します。

- `frontend`：Vue 3 + Vite（ポート5173）
- `backend`：FastAPI（ポート8000）
- `db`：PostgreSQL（ポート5432、Dockerネットワーク内）

## セットアップ（開発環境）

### 1. 必要なソフトウェア

- Git
- Docker Desktop（Docker Composeを含む）

### 2. リポジトリを取得

```bash
git clone https://github.com/yamaharuworks-sudo/hotel-customer-management.git
cd hotel-customer-management
```

### 3. 環境変数を設定

プロジェクトのルートディレクトリで、`.env.example` をコピーして `.env` を作成します。

Mac / Linux：

```bash
cp .env.example .env
```

Windows（PowerShell）：

```powershell
Copy-Item .env.example .env
```

作成した `.env` を開き、`POSTGRES_PASSWORD` をローカル開発用のパスワードに変更してください。

```dotenv
POSTGRES_PASSWORD=任意の開発用パスワード
```

パスワードは新しいPostgreSQL環境の初回起動前に設定してください。既存のデータベースでは、`.env` の値を変更するだけではDBユーザーのパスワードは変更されません。

`.env` はGit管理対象外です。実際のパスワードをGitHubにコミットしないでください。

### 4. Dockerコンテナを起動

```bash
docker compose -f compose.dev.yaml up -d --build
```

以下の3つのサービスが起動します。

- frontend（Vue）
- backend（FastAPI）
- db（PostgreSQL）

### 5. アプリにアクセス

- フロントエンド：http://localhost:5173
- FastAPI APIドキュメント：http://localhost:8000/docs
- APIの接続確認：http://localhost:8000/ready

### 6. データベースの初期設定

初回セットアップ時は、FastAPIコンテナ内でデータベースの初期化を行います。

**テーブルを作成**

```bash
docker compose -f compose.dev.yaml exec backend python init_db.py
```

以下のテーブルを作成します。

- `customers`：顧客情報
- `stays`：宿泊履歴
- `admin_users`：管理者アカウント
- `admin_sessions`：ログインセッション

**管理者アカウントを作成**

```bash
docker compose -f compose.dev.yaml exec backend python create_admin.py
```

画面の案内に従って管理者情報を入力してください。

初期設定が完了したら、ブラウザで `http://localhost:5173` を開いてログインします。

### 7. コンテナの停止

```bash
docker compose -f compose.dev.yaml down
```

このコマンドではPostgreSQLの名前付きボリュームは削除されないため、登録済みのデータは保持されます。