import getpass

from database import get_connection
from auth import hash_password


def create_admin():
    email = input("管理者メールアドレス: ").strip().lower()
    password = getpass.getpass("管理者パスワード: ")
    confirm_password = getpass.getpass("パスワード確認: ")

    if not email:
        print("メールアドレスを入力してください")
        return

    if len(password) < 12:
        print("パスワードは12文字以上にしてください")
        return

    if password != confirm_password:
        print("パスワードが一致しません")
        return

    password_hash = hash_password(password)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM admin_users LIMIT 1"
            )

            if cursor.fetchone() is not None:
                print("管理者アカウントはすでに存在します")
                return

            cursor.execute(
                """
                INSERT INTO admin_users (email, password_hash)
                VALUES (%s, %s)
                """,
                (email, password_hash)
            )

    print("管理者アカウントを作成しました")


if __name__ == "__main__":
    create_admin()