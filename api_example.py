import requests


BASE_URL = "http://127.0.0.1:5000"


def main():
    # 1) Просмотр списка новостей (доступно без прав)
    r = requests.get(f"{BASE_URL}/api/news")
    print("news list:", r.status_code, r.json())

    # 2) Чтение одной новости
    article_id = int(input("Введите id новости для просмотра: ").strip() or "1")
    r = requests.get(f"{BASE_URL}/api/news/{article_id}")
    print("news id=1:", r.status_code, r.json())

    # 3) Логин администратора (нужен для добавления/удаления новости)
    admin_session = requests.Session()
    admin_password = input("Введите пароль от admin: ").strip()
    r = admin_session.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": admin_password},
    )
    print("admin login:", r.status_code, r.json())

    # 4) Добавление новости
    title = "API: новая новость"
    intro = "Короткое вступление"
    text = "Полный текст новости"
    r = admin_session.post(
        f"{BASE_URL}/api/news",
        json={"title": title, "intro": intro, "text": text},
    )
    print("create:", r.status_code, r.json())

    # 5) Удаление новости
    delete_id = int(input("Введите id новости для удаления: ").strip())
    r = admin_session.delete(f"{BASE_URL}/api/news/{delete_id}")
    print("delete:", r.status_code, r.json())


if __name__ == "__main__":
    main()

