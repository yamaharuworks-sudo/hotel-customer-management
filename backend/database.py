import os
import psycopg
from dotenv import load_dotenv
from pathlib import Path

#backend/.envを読み込む
load_dotenv(Path(__file__).resolve().parent / ".env")
# 環境変数から接続情報を取得
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URLが設定されていません")

#PostgreSQLへの接続を作成する関数
def get_connection():
    return psycopg.connect(DATABASE_URL)