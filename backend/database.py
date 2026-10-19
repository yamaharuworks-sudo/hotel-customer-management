import os
import psycopg
from dotenv import load_dotenv
from pathlib import Path

#backend/.envを読み込む
load_dotenv(Path(__file__).resolve().parent / ".env")


#PostgreSQLへの接続を作成する関数
def get_connection():

    # 環境変数から接続情報を取得
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URLが設定されていません")


    return psycopg.connect(database_url)