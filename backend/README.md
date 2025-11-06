# Bear Sighting API

クマの出没情報を自動収集・分析・保存するFastAPIバックエンド

## 概要

この API は，NHK ニュースからクマ関連記事を自動収集し，LLM (GPT) で分析・分類，ジオコーディングで位置情報を付与して PostgreSQL に保存する．

### 主な機能

- 📰 **ニュース収集**: NewsAPI を使用して NHK からクマ関連記事を取得（1 日 1 回自動実行）
- 🧠 **LLM分析**: GPT で記事を分析し，具体的な出没情報か一般的な話題かを分類
- 📍 **位置情報付与**: 都道府県・市区町村から緯度経度を自動取得 (Nominatim)
- 💾 **データ保存**: 重複チェック後，PostgreSQL に保存
- 🔄 **スケジューラ**: APScheduler で毎日自動実行

## アーキテクチャ

```
┌─────────────┐
│  NewsAPI    │ (NHK ニュース取得)
└──────┬──────┘
       │
       v
┌─────────────┐
│ LLM (GPT)   │ (記事分析・分類・要約)
└──────┬──────┘
       │
       v
┌─────────────┐
│ Geocoding   │ (緯度経度取得)
└──────┬──────┘
       │
       v
┌─────────────┐
│ PostgreSQL  │ (データ保存)
└─────────────┘
```

## ファイル構成

| ファイル             | 説明                                                               |
| -------------------- | ------------------------------------------------------------------ |
| `main.py`            | FastAPI アプリケーション本体，スケジューラ設定，エンドポイント定義 |
| `models.py`          | SQLAlchemy データベースモデル（BearSighting）                      |
| `schemas.py`         | Pydantic スキーマ（バリデーション，シリアライズ）                  |
| `crud.py`            | データベース操作（作成・読み取り）                                 |
| `database.py`        | データベース接続設定，セッション管理                               |
| `services.py`        | メインビジネスロジック（ニュース取得→分析→保存）                   |
| `llm.py`             | LLM (GPT) による記事分析・分類                                     |
| `geocoding.py`       | 地名から緯度経度を取得（Nominatim + キャッシュ）                   |
| `docker-compose.yml` | PostgreSQL コンテナ設定                                            |
| `pyproject.toml`     | プロジェクト依存関係                                               |

## セットアップ

### 1. 環境変数の設定

`.env` ファイルを作成し，以下を設定：

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bear_sighting
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=bear_sighting
POSTGRES_PORT=5432

# API Keys
NEWS_API_KEY=your_newsapi_key
OPENAI_API_KEY=your_openai_key
```

### 2. 依存関係インストール

```bash
mise backend:setup
```

### 3. データベース起動

```bash
mise backend:start-db
```

### 4. サーバー起動

```bash
mise backend:dev
# または
mise backend:start
```

### 5. リンター・フォーマッター

```bash
mise backend:format
mise backend:lint
mise backend:lint-fix
```

## API エンドポイント

### `GET /`
APIルートエンドポイント（ウェルカムメッセージ）

### `GET /health`
ヘルスチェック

### `GET /sightings`
すべての出没情報を取得

**レスポンス例:**
```json
[
  {
    "id": 1,
    "prefecture": "岩手県",
    "city": "盛岡市",
    "latitude": 39.7036,
    "longitude": 141.1527,
    "summary": "盛岡市の岩手銀行本店の地下駐車場にクマ1頭が侵入し，捕獲された．",
    "source_url": "https://www3.nhk.or.jp/...",
    "image_url": "https://...",
    "published_at": "2025-11-05T10:30:00Z"
  }
]
```

## データフロー

1. **スケジューラ起動**（毎日 1 回）
   - `run_sighting_job()` → `services.process_and_save_articles()`

2. **ニュース取得**
   - NewsAPI から「クマ」関連記事を取得（NHK のみ，過去 1 日分）

3. **記事分析**
   - LLM で記事を分析
   - 具体的な出没情報か判定
   - 都道府県・市区町村・要約を抽出

4. **位置情報取得**
   - Nominatim で緯度経度を取得（キャッシュ機能付き）

5. **重複チェック**
   - URL で既存データをチェック

6. **データ保存**
   - PostgreSQL に保存

## データベーススキーマ

### `bear_sightings` テーブル

| カラム         | 型       | 説明                 |
| -------------- | -------- | -------------------- |
| `id`           | Integer  | 主キー（自動採番）   |
| `prefecture`   | String   | 都道府県             |
| `city`         | String   | 市区町村             |
| `latitude`     | Float    | 緯度                 |
| `longitude`    | Float    | 経度                 |
| `summary`      | String   | 要約                 |
| `source_url`   | String   | 記事 URL（ユニーク） |
| `image_url`    | String   | 画像 URL             |
| `published_at` | DateTime | 公開日時             |

## 技術スタック

- **フレームワーク**: FastAPI, Uvicorn
- **データベース**: PostgreSQL (SQLAlchemy ORM)
- **LLM**: OpenAI GPT
- **ジオコーディング**: Nominatim (Geopy)
- **スケジューラ**: APScheduler
- **HTTP クライアント**: httpx
- **検証**: Pydantic
