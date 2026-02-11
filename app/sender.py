import argparse
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

import pyaudio


# Audio settings (must match receiver)
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


LogFn = Callable[[str], None]


@dataclass
class SenderClient:
    host: str = "127.0.0.1"
    port: int = 9999
    log: LogFn = print
    chunk_size: int = CHUNK_SIZE
    rate: int = RATE
    channels: int = CHANNELS
    audio_format: int = FORMAT

    _stop_event: threading.Event = field(default_factory=threading.Event, init=False)
    _thread: threading.Thread | None = field(default=None, init=False)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        t = threading.Thread(target=self._run, daemon=True)
        self._thread = t
        t.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self.log("Sender stopped.")

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def _run(self) -> None:
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )

        sock: socket.socket | None = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            self.log(f"Connected to receiver at {self.host}:{self.port}")
            self.log("Sending microphone audio...")

            while not self._stop_event.is_set():
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                sock.sendall(data)
        except Exception as exc:
            self.log(f"Sender error: {exc}")
        finally:
            try:
                if sock is not None:
                    sock.close()
            finally:
                stream.stop_stream()
                stream.close()
                audio.terminate()


def start_sender(host: str, port: int) -> None:
    client = SenderClient(host=host, port=port)
    client.start()

    try:
        while client.is_running():
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nStopping sender...")
    finally:
        client.stop()


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
