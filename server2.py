import socket
import pyaudio
import threading

# Server configuration
HOST = '192.168.9.63'
PORT = 9999

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Function to handle each client connection
def handle_client(conn, addr):
    print(f"[*] Accepted connection from {addr}")

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK_SIZE)

    try:
        while True:
            data = conn.recv(CHUNK_SIZE)
            if not data:
                break
            stream.write(data)
    except Exception as e:
        print(f"Error: {e}")

    print(f"[*] Connection from {addr} closed.")
    conn.close()

# Function to accept incoming connections and start a thread for each
def accept_connections():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[*] Server shutting down.")
        server.close()

# Start accepting connections
accept_connections()
