import socket
import threading
import pyaudio

# Server configuration
HOST = '192.168.56.1'
PORT = 12345

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

# Start the server
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
