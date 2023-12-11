import socket
import threading

# Configuration:
LOCAL_HOST = '0.0.0.0'  # Listen on all network interfaces
LOCAL_PORT = 6002       # Port for users to connect to the service
SERVICE_PORT = 6003     # Port to connect to the frpc (forwarding client)

def handle_local_forwarding(local_conn, service_conn):
    while True:
        data = local_conn.recv(4096)
        if not data:
            break
        service_conn.sendall(data)

def handle_service_forwarding(service_conn, local_conn):
    while True:
        data = service_conn.recv(4096)
        if not data:
            break
        local_conn.sendall(data)

def main():
    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    local_server.bind((LOCAL_HOST, LOCAL_PORT))
    local_server.listen(20)
    
    service_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    service_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    service_server.bind((LOCAL_HOST, SERVICE_PORT))
    service_server.listen(1)
    
    print(f'FRPS is running, waiting for connections on port {LOCAL_PORT} (users) and {SERVICE_PORT} (frpc).')

    while True:
        local_conn, local_addr = local_server.accept()
        print(f'User connected from {local_addr}')
        
        service_conn, service_addr = service_server.accept()
        print(f'FRPC connected from {service_addr}')
        
        threading.Thread(target=handle_local_forwarding, args=(local_conn, service_conn)).start()
        threading.Thread(target=handle_service_forwarding, args=(service_conn, local_conn)).start()

if __name__ == '__main__':
    main()