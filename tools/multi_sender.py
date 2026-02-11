import argparse
import threading

from app.sender import start_sender


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tool: start multiple senders (useful for stress testing)."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9999)
    parser.add_argument("--clients", type=int, default=3)
    args = parser.parse_args()

    for _ in range(args.clients):
        threading.Thread(
            target=start_sender,
            args=(args.host, args.port),
            daemon=True,
        ).start()

    threading.Event().wait()


if __name__ == "__main__":
    main()
