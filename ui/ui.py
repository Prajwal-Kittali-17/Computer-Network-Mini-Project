import socket
import tkinter as tk
from dataclasses import dataclass
from queue import Empty, Queue
from tkinter import ttk

from app.receiver import ReceiverServer
from app.sender import SenderClient


def _get_local_ip_guess() -> str:
    """Best-effort local IP (no external requests)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't send packets; used to pick the outbound interface.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        return ip
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class LogBox(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self._q: Queue[str] = Queue()

        self._text = tk.Text(
            self,
            height=10,
            wrap="word",
            state="disabled",
        )
        self._scroll = ttk.Scrollbar(self, orient="vertical", command=self._text.yview)
        self._text.configure(yscrollcommand=self._scroll.set)

        self._text.grid(row=0, column=0, sticky="nsew")
        self._scroll.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.after(75, self._pump)

    def log(self, msg: str) -> None:
        self._q.put(msg)

    def _pump(self) -> None:
        drained = False
        try:
            while True:
                msg = self._q.get_nowait()
                drained = True
                self._append(msg)
        except Empty:
            pass
        finally:
            self.after(75 if drained else 150, self._pump)

    def _append(self, msg: str) -> None:
        self._text.configure(state="normal")
        self._text.insert("end", msg.rstrip() + "\n")
        self._text.see("end")
        self._text.configure(state="disabled")


@dataclass
class _Status:
    text_var: tk.StringVar

    def set(self, text: str) -> None:
        self.text_var.set(text)


class ReceiverTab(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=12)

        self._server: ReceiverServer | None = None

        self._host_var = tk.StringVar(value="0.0.0.0")
        self._port_var = tk.StringVar(value="9999")
        self._local_ip_var = tk.StringVar(value=_get_local_ip_guess())
        self._status = _Status(tk.StringVar(value="Stopped"))

        header = ttk.Label(self, text="Receiver (plays audio)", font=("Segoe UI", 12, "bold"))
        header.grid(row=0, column=0, columnspan=4, sticky="w")

        ttk.Label(self, text="Tip: run Receiver first.").grid(row=1, column=0, columnspan=4, sticky="w", pady=(2, 10))

        ttk.Label(self, text="Listen host").grid(row=2, column=0, sticky="w")
        ttk.Entry(self, textvariable=self._host_var, width=18).grid(row=2, column=1, sticky="w", padx=(8, 16))

        ttk.Label(self, text="Port").grid(row=2, column=2, sticky="w")
        ttk.Entry(self, textvariable=self._port_var, width=10).grid(row=2, column=3, sticky="w", padx=(8, 0))

        ttk.Label(self, text="Receiver IP (share with sender)").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(self, textvariable=self._local_ip_var, width=30, state="readonly").grid(
            row=3, column=1, columnspan=3, sticky="w", padx=(8, 0), pady=(10, 0)
        )

        btn_row = ttk.Frame(self)
        btn_row.grid(row=4, column=0, columnspan=4, sticky="w", pady=(12, 0))

        self._start_btn = ttk.Button(btn_row, text="Start", command=self._start)
        self._stop_btn = ttk.Button(btn_row, text="Stop", command=self._stop, state="disabled")
        self._start_btn.grid(row=0, column=0, sticky="w")
        self._stop_btn.grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Label(btn_row, text="Status:").grid(row=0, column=2, sticky="w", padx=(16, 4))
        ttk.Label(btn_row, textvariable=self._status.text_var).grid(row=0, column=3, sticky="w")

        ttk.Separator(self).grid(row=5, column=0, columnspan=4, sticky="ew", pady=(12, 8))

        self._logs = LogBox(self)
        self._logs.grid(row=6, column=0, columnspan=4, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(6, weight=1)

    def _start(self) -> None:
        if self._server is not None and self._server.is_running():
            return

        host = self._host_var.get().strip() or "0.0.0.0"
        try:
            port = int(self._port_var.get().strip() or "9999")
        except ValueError:
            self._logs.log("Port must be a number.")
            return

        self._local_ip_var.set(_get_local_ip_guess())

        self._server = ReceiverServer(host=host, port=port, log=self._logs.log)
        try:
            self._server.start()
        except Exception as exc:
            self._logs.log(f"Receiver failed to start: {exc}")
            self._server = None
            self._status.set("Stopped")
            return

        self._status.set("Running")
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")

    def _stop(self) -> None:
        if self._server is None:
            return
        try:
            self._server.stop()
        finally:
            self._server = None
            self._status.set("Stopped")
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")


class SenderTab(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=12)

        self._client: SenderClient | None = None

        self._host_var = tk.StringVar(value="127.0.0.1")
        self._port_var = tk.StringVar(value="9999")
        self._status = _Status(tk.StringVar(value="Stopped"))

        header = ttk.Label(self, text="Sender (records microphone)", font=("Segoe UI", 12, "bold"))
        header.grid(row=0, column=0, columnspan=4, sticky="w")

        ttk.Label(self, text="Enter the Receiver IP and press Start.").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(2, 10)
        )

        ttk.Label(self, text="Receiver host").grid(row=2, column=0, sticky="w")
        ttk.Entry(self, textvariable=self._host_var, width=18).grid(row=2, column=1, sticky="w", padx=(8, 16))

        ttk.Label(self, text="Port").grid(row=2, column=2, sticky="w")
        ttk.Entry(self, textvariable=self._port_var, width=10).grid(row=2, column=3, sticky="w", padx=(8, 0))

        btn_row = ttk.Frame(self)
        btn_row.grid(row=3, column=0, columnspan=4, sticky="w", pady=(12, 0))

        self._start_btn = ttk.Button(btn_row, text="Start", command=self._start)
        self._stop_btn = ttk.Button(btn_row, text="Stop", command=self._stop, state="disabled")
        self._start_btn.grid(row=0, column=0, sticky="w")
        self._stop_btn.grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Label(btn_row, text="Status:").grid(row=0, column=2, sticky="w", padx=(16, 4))
        ttk.Label(btn_row, textvariable=self._status.text_var).grid(row=0, column=3, sticky="w")

        ttk.Separator(self).grid(row=4, column=0, columnspan=4, sticky="ew", pady=(12, 8))

        self._logs = LogBox(self)
        self._logs.grid(row=5, column=0, columnspan=4, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

    def _start(self) -> None:
        if self._client is not None and self._client.is_running():
            return

        host = self._host_var.get().strip() or "127.0.0.1"
        try:
            port = int(self._port_var.get().strip() or "9999")
        except ValueError:
            self._logs.log("Port must be a number.")
            return

        self._client = SenderClient(host=host, port=port, log=self._logs.log)
        self._client.start()

        self.after(250, self._sync_status)

        self._status.set("Running")
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")

    def _sync_status(self) -> None:
        if self._client is None:
            return
        if not self._client.is_running():
            self._status.set("Stopped")
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")

    def _stop(self) -> None:
        if self._client is None:
            return
        try:
            self._client.stop()
        finally:
            self._client = None
            self._status.set("Stopped")
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")


class App(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        self.pack(fill="both", expand=True)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        notebook.add(ReceiverTab(notebook), text="Receiver")
        notebook.add(SenderTab(notebook), text="Sender")


def main() -> None:
    root = tk.Tk()
    root.title("Audio Walkie-Talkie")
    root.minsize(760, 520)

    try:
        style = ttk.Style(root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except tk.TclError:
        pass

    App(root)

    def on_close() -> None:
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
