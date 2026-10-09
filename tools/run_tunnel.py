"""Cloudflare Quick Tunnel Runner for Stick Clash.
Generates a public HTTPS/WSS URL for online multiplayer testing.
"""

import os
import re
import subprocess
import sys
import time

CLOUDFLARED_PATH = r"C:\Users\denzs\.gemini\antigravity-ide\bin\cloudflared.exe"

def start_tunnel(target_url="http://127.0.0.1:5173"):
    if not os.path.exists(CLOUDFLARED_PATH):
        print(f"Error: cloudflared not found at {CLOUDFLARED_PATH}")
        sys.exit(1)

    print(f"[*] Starting Cloudflare Tunnel targeting {target_url}...")
    cmd = [CLOUDFLARED_PATH, "tunnel", "--url", target_url]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    for line in iter(process.stdout.readline, ""):
        print(line, end="")
        match = url_pattern.search(line)
        if match:
            tunnel_url = match.group(0)
            print("\n" + "=" * 60)
            print(f"🎉 CLOUDFLARE PUBLIC MULTIPLAYER URL: {tunnel_url}")
            print(f"Share this link with friends to play online:")
            print(f"  {tunnel_url}")
            print("=" * 60 + "\n")
            with open("tunnel_url.txt", "w") as f:
                f.write(tunnel_url)
            break

    try:
        process.wait()
    except KeyboardInterrupt:
        print("[*] Stopping tunnel...")
        process.terminate()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5173"
    start_tunnel(target)
