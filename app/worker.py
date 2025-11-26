import pika
import json
import cv2
import numpy as np
import requests
import time

# Funkcja analizy
def detect_people(image_url: str) -> int:
    print(f" [Worker] Pobieram: {image_url}")
    try:
        resp = requests.get(image_url, stream=True, timeout=10)
        if resp.status_code != 200:
            return 0
        image_array = np.asarray(bytearray(resp.content), dtype="uint8")
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None: return 0
        
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        boxes, _ = hog.detectMultiScale(image, winStride=(8,8), padding=(8,8), scale=1.05)
        return len(boxes)
    except Exception as e:
        print(f" [Worker] Błąd: {e}")
        return 0

def callback(ch, method, properties, body):
    """To się wykonuje, gdy przyjdzie wiadomość z kolejki"""
    message = json.loads(body)
    url = message['url']
    user_id = message['user_id']
    
    print(f" [x] Odebrano zadanie dla UserID: {user_id}")
    
    # Symulacja długiej pracy (opcjonalne)
    # time.sleep(2)
    
    count = detect_people(url)
    print(f" [x] Wynik: Znaleziono {count} osób.")
    
    # Tutaj normalnie zapisalibyśmy wynik do bazy danych (UPDATE analysis_results SET count=...)
    
    # Potwierdzenie wykonania zadania (żeby RabbitMQ usunął je z kolejki)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='image_analysis', durable=True)
    
    # QoS: Worker bierze tylko 1 zadanie na raz
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue='image_analysis', on_message_callback=callback)
    
    print(' [*] Czekam na wiadomości. Naciśnij CTRL+C aby wyjść.')
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()