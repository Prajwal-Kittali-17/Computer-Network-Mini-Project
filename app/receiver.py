import argparse
import socket
import threading

import pyaudio


# Audio settings (must match sender)
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


def handle_client(conn: socket.socket, addr) -> None:
    print(f"Connected: {addr}")

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK_SIZE,
    )

    try:
        while True:
            data = conn.recv(CHUNK_SIZE)
            if not data:
                break
            stream.write(data)
    except Exception as exc:
        print(f"Connection error from {addr}: {exc}")
    finally:
        try:
            conn.close()
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
        print(f"Disconnected: {addr}")


def start_receiver(host: str, port: int) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)

    print("Receiver is running.")
    print(f"Listening on {host}:{port}")
    print("Keep this window open. Press Ctrl+C to stop.")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            ).start()
    except KeyboardInterrupt:
        print("\nStopping receiver...")
    finally:
        server.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Receiver: plays audio coming from a sender "
            "over Wi-Fi/LAN."
        )
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Where to listen (default: 0.0.0.0 = all network adapters)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9999,
        help="Port to listen on (default: 9999)",
    )
    args = parser.parse_args()

    start_receiver(args.host, args.port)


if __name__ == "__main__":
    main()
