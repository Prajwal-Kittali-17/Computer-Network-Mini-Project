import argparse
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

import pyaudio


# Audio settings (must match sender)
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


LogFn = Callable[[str], None]


@dataclass
class ReceiverServer:
    host: str = "0.0.0.0"
    port: int = 9999
    log: LogFn = print
    chunk_size: int = CHUNK_SIZE
    rate: int = RATE
    channels: int = CHANNELS
    audio_format: int = FORMAT

    _stop_event: threading.Event = field(default_factory=threading.Event, init=False)
    _accept_thread: threading.Thread | None = field(default=None, init=False)
    _server_sock: socket.socket | None = field(default=None, init=False)
    _client_threads: list[threading.Thread] = field(default_factory=list, init=False)
    _client_conns: set[socket.socket] = field(default_factory=set, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def start(self) -> None:
        if self._accept_thread and self._accept_thread.is_alive():
            return

        self._stop_event.clear()

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        server.settimeout(0.5)
        self._server_sock = server

        self.log("Receiver is running.")
        self.log(f"Listening on {self.host}:{self.port}")

        t = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread = t
        t.start()

    def stop(self) -> None:
        self._stop_event.set()

        server = self._server_sock
        self._server_sock = None
        if server is not None:
            try:
                server.close()
            except OSError:
                pass

        with self._lock:
            conns = list(self._client_conns)
            self._client_conns.clear()

        for conn in conns:
            try:
                conn.close()
            except OSError:
                pass

        if self._accept_thread is not None:
            self._accept_thread.join(timeout=2)

        for ct in list(self._client_threads):
            ct.join(timeout=2)

        self.log("Receiver stopped.")

    def is_running(self) -> bool:
        return bool(self._accept_thread and self._accept_thread.is_alive())

    def _accept_loop(self) -> None:
        server = self._server_sock
        if server is None:
            return

        while not self._stop_event.is_set():
            try:
                conn, addr = server.accept()
            except TimeoutError:
                continue
            except OSError:
                break

            with self._lock:
                self._client_conns.add(conn)

            ct = threading.Thread(
                target=self._handle_client,
                args=(conn, addr),
                daemon=True,
            )
            self._client_threads.append(ct)
            ct.start()

        self.log("Receiver shutting down...")

    def _handle_client(self, conn: socket.socket, addr) -> None:
        self.log(f"Connected: {addr}")
        conn.settimeout(0.5)

        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk_size,
        )

        try:
            while not self._stop_event.is_set():
                try:
                    data = conn.recv(self.chunk_size)
                except TimeoutError:
                    continue
                if not data:
                    break
                stream.write(data)
        except Exception as exc:
            self.log(f"Connection error from {addr}: {exc}")
        finally:
            with self._lock:
                self._client_conns.discard(conn)
            try:
                conn.close()
            finally:
                stream.stop_stream()
                stream.close()
                audio.terminate()
            self.log(f"Disconnected: {addr}")


def start_receiver(host: str, port: int) -> None:
    server = ReceiverServer(host=host, port=port)
    server.start()

    try:
        while server.is_running():
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nStopping receiver...")
    finally:
        server.stop()


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
