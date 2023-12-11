import socket
import threading

# Configuration:
REMOTE_HOST = 'santongding.com'   # IP address of frps
REMOTE_PORT =  6003         # The port on frps for service connection
SERVICE_HOST = '127.0.0.1'  # The service to forward requests to
SERVICE_PORT = 5001          # The service port to forward requests to

def handle_remote_forwarding(remote_conn, service_conn):
    while True:
        data = remote_conn.recv(4096)
        if not data:
            break
        service_conn.sendall(data)

def handle_service_forwarding(service_conn, remote_conn):
    while True:
        data = service_conn.recv(4096)
        if not data:
            break
        remote_conn.sendall(data)

def main():
    while True:
        remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_conn.connect((REMOTE_HOST, REMOTE_PORT))

        service_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        service_conn.connect((SERVICE_HOST, SERVICE_PORT))

        print(f'Connected to FRPS at {REMOTE_HOST}:{REMOTE_PORT} and to local service at {SERVICE_HOST}:{SERVICE_PORT}.')

        threads = [threading.Thread(target=handle_remote_forwarding, args=(remote_conn, service_conn)),
        threading.Thread(target=handle_service_forwarding, args=(service_conn, remote_conn))]

        for t in threads:
            t.start()

if __name__ == '__main__':
    main()