import requests
import time

def send_requests(ip, port, interval, count):
    url = f"http://{ip}:{port}"
    
    for i in range(count):
        try:
            response = requests.get(url)
            print(f"Request {i + 1}: Status Code: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Request {i + 1} failed: {e}")
        
        time.sleep(interval)

if __name__ == "__main__":
    target_ip = "10.0.0.1"  # Replace with the target IP
    target_port = 8080        # Replace with the target port
    request_interval = 5      # Interval in seconds
    request_count = 10        # Number of requests to send

    send_requests(target_ip, target_port, request_interval, request_count)
