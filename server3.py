import socket
import threading
import pyaudio

# Server configuration
HOST = '192.168.9.31'  # Listen on all available interfaces
PORT = 3333
MAX_CONNECTIONS = 5  # Maximum number of simultaneous connections

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# List to store connected clients
connected_clients = []

# Function to handle a single client's audio streaming
def handle_client(client_socket):
    print(f"[*] New connection from {client_socket.getpeername()}")
    connected_clients.append(client_socket)

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK_SIZE)

    try:
        while True:
            data = client_socket.recv(CHUNK_SIZE)
            if not data:
                break

            # Broadcast received audio data to all connected clients
            for client in connected_clients:
                try:
                    client.sendall(data)
                except Exception as e:
                    print(f"Error sending audio to {client.getpeername()}: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print(f"[*] Connection from {client_socket.getpeername()} closed.")
        connected_clients.remove(client_socket)
        stream.stop_stream()
        stream.close()
        p.terminate()
        client_socket.close()

# Function to start the server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CONNECTIONS)
    print(f"[*] Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if _name_ == "_main_":
    start_server()