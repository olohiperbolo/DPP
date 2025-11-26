import sqlite3

# Łączymy się z bazą danych
conn = sqlite3.connect('app/database.db')
cursor = conn.cursor()

# Ustawiamy rolę ROLE_ADMIN dla użytkownika o nazwie 'admin'
username_to_promote = "admin"

cursor.execute("UPDATE users SET role = 'ROLE_ADMIN' WHERE username = ?", (username_to_promote,))
conn.commit()

if cursor.rowcount > 0:
    print(f"Sukces! Użytkownik '{username_to_promote}' jest teraz administratorem.")
else:
    print(f"Nie znaleziono użytkownika '{username_to_promote}'. Najpierw go zarejestruj!")

conn.close()