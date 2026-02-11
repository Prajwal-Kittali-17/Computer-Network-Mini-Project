import argparse
import socket

import pyaudio


# Audio settings (must match receiver)
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


def start_sender(host: str, port: int) -> None:
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )

    sock: socket.socket | None = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"Connected to receiver at {host}:{port}")
        print("Sending microphone audio... Press Ctrl+C to stop.")

        while True:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            sock.sendall(data)
    except KeyboardInterrupt:
        print("\nStopping sender...")
    except Exception as exc:
        print(f"Sender error: {exc}")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        if sock is not None:
            sock.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Sender: sends microphone audio to a receiver "
            "over Wi-Fi/LAN."
        )
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Receiver IP/host (default: 127.0.0.1 for same PC test)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9999,
        help="Receiver port (default: 9999)",
    )
    args = parser.parse_args()

    start_sender(args.host, args.port)


if __name__ == "__main__":
    main()
