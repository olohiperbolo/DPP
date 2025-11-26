import pika
import json
import cv2
import numpy as np
import requests
import time

# Funkcja analizy (taka sama jak w main.py, ale tutaj wykonuje się w tle)
def detect_people(image_url: str) -> int:
    print(f" [Worker] Pobieram: {image_url}")
    try:
        # Dodajemy User-Agent, żeby serwery nas nie blokowały (błąd 403)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        # Pobieramy zdjęcie
        resp = requests.get(image_url, stream=True, timeout=10, headers=headers)
        
        if resp.status_code != 200:
            print(f" [Worker] Błąd pobierania! Kod HTTP: {resp.status_code}")
            return 0
            
        # Konwersja bajtów na obraz OpenCV
        image_array = np.asarray(bytearray(resp.content), dtype="uint8")
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None: 
            print(" [Worker] Nie udało się odczytać obrazu (zły format?)")
            return 0
        
        # Wykrywanie ludzi (HOG + SVM)
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Detekcja
        boxes, _ = hog.detectMultiScale(image, winStride=(8,8), padding=(8,8), scale=1.05)
        return len(boxes)
        
    except Exception as e:
        print(f" [Worker] Wyjątek podczas analizy: {e}")
        return 0

def callback(ch, method, properties, body):
    """Ta funkcja uruchamia się automatycznie, gdy przyjdzie wiadomość z RabbitMQ"""
    try:
        # Odbieramy JSON z kolejki
        message = json.loads(body)
        url = message.get('url')
        user_id = message.get('user_id')
        
        print(f" [x] Odebrano zadanie dla UserID: {user_id}")
        
        if url:
            # Wykonujemy ciężką pracę (analiza)
            count = detect_people(url)
            print(f" [x] Wynik: Znaleziono {count} osób na zdjęciu.")
        else:
            print(" [!] Błąd: Wiadomość nie zawiera URL")
        
    except Exception as e:
        print(f" [!] Błąd przetwarzania wiadomości: {e}")
    finally:
        # Potwierdzenie wykonania zadania (CRITICAL!)
        # Jeśli tego nie zrobisz, RabbitMQ pomyśli, że worker padł i wyśle zadanie komuś innemu
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    # Łączymy się z RabbitMQ (zakładamy, że działa na localhost w Dockerze)
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        
        # Deklarujemy kolejkę (musi być ta sama nazwa co w API!)
        channel.queue_declare(queue='image_analysis', durable=True)
        
        # QoS: Worker bierze tylko 1 zadanie na raz.
        # Nie weźmie kolejnego, dopóki nie potwierdzi (basic_ack) poprzedniego.
        channel.basic_qos(prefetch_count=1)
        
        # Rejestrujemy funkcję callback
        channel.basic_consume(queue='image_analysis', on_message_callback=callback)
        
        print(' [*] Worker gotowy. Czekam na wiadomości. Naciśnij CTRL+C aby wyjść.')
        channel.start_consuming()
        
    except pika.exceptions.AMQPConnectionError:
        print(" [!] BŁĄD: Nie można połączyć się z RabbitMQ.")
        print("     Upewnij się, że kontener Docker działa: sudo docker ps")

if __name__ == "__main__":
    start_worker()