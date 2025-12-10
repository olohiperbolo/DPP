import requests
import time
import getpass  # Biblioteka do bezpiecznego wprowadzania hasła

# Konfiguracja
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
TASK_URL = f"{BASE_URL}/analyze_img_async"

IMAGE_URL = "https://thumbs.dreamstime.com/b/grupa-ludzi-60885454.jpg"

# --- INTERAKTYWNE LOGOWANIE ---
print("--- Konfiguracja Autoryzacji ---")
# Input pozwala wpisać login, "or 'admin'" ustawi 'admin' jeśli wciśniesz tylko Enter
USERNAME = input("Podaj login: ") or "admin"
# Getpass ukrywa wpisywane znaki
PASSWORD = getpass.getpass("Podaj hasło: ")

def get_auth_token():
    """Loguje się i zwraca token Bearer"""
    print(f"\nPróba logowania jako: {USERNAME}...")
    try:
        # Swagger używa formularza, więc wysyłamy 'data', a nie 'json'
        response = requests.post(LOGIN_URL, data={"username": USERNAME, "password": PASSWORD})
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("Zalogowano pomyślnie!")
            return token
        else:
            print(f"Błąd logowania: {response.status_code}")
            print(f"Treść błędu: {response.text}")
            exit()
    except Exception as e:
        print(f"Błąd połączenia z API: {e}")
        exit()

def spam_queue(count=100):
    # Pobieramy token (teraz używając wpisanego hasła)
    token = get_auth_token()
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"url": IMAGE_URL}

    print(f"\nRozpoczynam wysyłanie {count} zadań do kolejki...")
    start_time = time.time()

    for i in range(count):
        try:
            res = requests.post(TASK_URL, json=payload, headers=headers)
            if res.status_code == 202:
                print(f"[{i+1}/{count}] Wysłano zadanie (202 Accepted)")
            else:
                print(f"[{i+1}/{count}] Błąd: {res.status_code}")
        except Exception as e:
            print(f"Błąd: {e}")

    duration = time.time() - start_time
    print(f"\nZakończono! Wysłano {count} zadań w {duration:.2f} sekundy.")

if __name__ == "__main__":
    # Możesz zmienić liczbę zadań tutaj
    spam_queue(100)