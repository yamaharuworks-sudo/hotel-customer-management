from database import get_connection


def cleanup_expired_sessions():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM admin_sessions
                WHERE expires_at <= NOW()
                """
            )

            deleted_count = cursor.rowcount

    print(f"期限切れセッションを{deleted_count}件削除しました")


if __name__ == "__main__":
    cleanup_expired_sessions()