import pika
import json
import requests
import cv2
import numpy as np
from ultralytics import YOLO

# Ładujemy model raz, przy starcie skryptu (wersja 'n' - nano, najszybsza)
print(" [Worker] Ładowanie modelu AI (YOLOv8)...")
model = YOLO('yolov8n.pt') 

def detect_people(image_url: str) -> int:
    print(f" [Worker] Pobieram: {image_url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        resp = requests.get(image_url, stream=True, timeout=10, headers=headers)
        
        if resp.status_code != 200:
            print(f" [Worker] Błąd HTTP: {resp.status_code}")
            return 0
            
        # Konwersja do formatu dla OpenCV
        image_array = np.asarray(bytearray(resp.content), dtype="uint8")
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None: return 0
        
        # --- ANALIZA YOLOv8 ---
        # conf=0.4 oznacza, że bierzemy tylko te, gdzie AI jest pewna na >40%
        results = model.predict(image, classes=[0], conf=0.4, verbose=False) 
        
        # Klasa '0' w YOLO to 'person' (osoba). Liczymy ile ich wykryto.
        person_count = len(results[0].boxes)
        
        return person_count
        
    except Exception as e:
        print(f" [Worker] Błąd: {e}")
        return 0

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        url = message.get('url')
        user_id = message.get('user_id')
        
        print(f" [x] Zadanie dla UserID: {user_id} | URL: {url[-30:]}...") # Wyświetlamy końcówkę URL
        
        if url:
            count = detect_people(url)
            print(f" [x] >>> WYNIK: Znaleziono {count} osób. <<<")
        else:
            print(" [!] Błąd: Pusty URL")
            
    except Exception as e:
        print(f" [!] Błąd w workerze: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='image_analysis', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='image_analysis', on_message_callback=callback)
        print(' [*] Worker (YOLOv8) gotowy! Czekam na zadania.')
        channel.start_consuming()
    except Exception as e:
        print(f" [!] Błąd połączenia z RabbitMQ: {e}")

if __name__ == "__main__":
    start_worker()