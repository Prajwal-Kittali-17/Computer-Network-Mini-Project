# Audio Walkie-Talkie (Computer Networks Mini Project)

This project lets one computer **send live microphone audio** to another computer over the same Wi‑Fi / LAN.

Think of it like a simple walkie‑talkie:

- **Sender** = the computer that talks into the microphone
- **Receiver** = the computer that plays the sound on speakers/headphones

It is meant for learning sockets in Computer Networks.

## What you need (simple checklist)

- Two Windows PCs/laptops on the same Wi‑Fi (or you can test on one PC)
- Python installed
- A microphone on the Sender
- Speakers/headphones on the Receiver

Tip: use headphones on the Receiver to avoid loud echo/feedback.

## How to run (step by step)

### Clean UI (recommended)

You can run a simple interactive window with Start/Stop buttons:

```bash
python -m ui
```

Use the **Receiver** tab first, then the **Sender** tab.

### Step 1 — Download and open the project

Open this folder in VS Code or File Explorer.

### Step 2 — Install the required library

Open PowerShell in this folder and run:

```bash
python -m pip install -r requirements.txt
```

### Step 3 — Start the Receiver (the listening computer)

On the Receiver PC, run:

```bash
python app/receiver.py --host 0.0.0.0 --port 9999
```

Leave this window open.

### Step 4 — Find the Receiver’s IP address

On the Receiver PC:

1. Open **Command Prompt**
2. Type `ipconfig` and press Enter
3. Look for **IPv4 Address** (it looks like `192.168.x.x`)

That number is the Receiver IP.

### Step 5 — Start the Sender (the talking computer)

On the Sender PC, run (replace `RECEIVER_IP`):

```bash
python app/sender.py --host RECEIVER_IP --port 9999
```

Now speak into the Sender microphone — you should hear it on the Receiver.

## Testing on a single computer (optional)

You can test without a second PC:

Terminal 1:

```bash
python app/receiver.py
```

Terminal 2:

```bash
python app/sender.py --host 127.0.0.1
```

## How to stop

In any running window, press **Ctrl + C**.

## Troubleshooting (common issues)

### “No sound”

- Make sure the Receiver volume is not muted
- Try headphones
- Confirm both PCs are on the same Wi‑Fi

### “Connection refused” or it can’t connect

- Receiver must be started first
- Check the IP address is correct
- Windows Firewall might block Python; allow it for Private networks

### Microphone errors

- Windows Settings → Privacy & security → Microphone → allow access
- Close other apps using the microphone (Zoom/Teams, etc.)

## Project structure

- `app/receiver.py` — plays the incoming audio
- `app/sender.py` — records microphone audio and sends it
- `tools/multi_sender.py` — optional testing tool (not needed for normal use)

## Important note

This is a learning demo and does **not** add encryption/authentication.
Only use it on a trusted local network.
