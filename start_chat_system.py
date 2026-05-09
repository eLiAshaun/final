#!/usr/bin/env python3
import argparse
import platform
import shlex
import socket
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
CHAT_DIR = PROJECT_ROOT / "simple_gui"
CHAT_PORT = 1112


def venv_python():
    if platform.system() == "Windows":
        candidate = PROJECT_ROOT / "icdsproject" / "Scripts" / "python.exe"
    else:
        candidate = PROJECT_ROOT / "icdsproject" / "bin" / "python"
    return candidate if candidate.exists() else Path(sys.executable)


def escape_applescript(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def open_terminal(command):
    if platform.system() == "Darwin":
        script = (
            'tell application "Terminal"\n'
            '  activate\n'
            f'  do script "{escape_applescript(command)}"\n'
            'end tell'
        )
        subprocess.run(["osascript", "-e", script], check=True)
    elif platform.system() == "Windows":
        subprocess.Popen(f'start cmd /k "{command}"', shell=True)
    else:
        subprocess.Popen(["xterm", "-e", command])


def port_is_open(host="127.0.0.1", port=CHAT_PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((host, port)) == 0


def wait_for_server(timeout=6):
    start = time.time()
    while time.time() - start < timeout:
        if port_is_open():
            return True
        time.sleep(0.2)
    return False


def build_command(python_path, script_name, extra_args=None):
    parts = [
        "cd",
        shlex.quote(str(CHAT_DIR)),
        "&&",
        shlex.quote(str(python_path)),
        script_name,
    ]
    if extra_args:
        parts.extend(extra_args)
    return " ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Start the ICDS GUI chat demo.")
    parser.add_argument(
        "--clients",
        type=int,
        default=2,
        help="number of GUI clients to open after the server is ready",
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="open clients only, assuming chat_server.py is already running",
    )
    args = parser.parse_args()
    if args.clients < 1:
        parser.error("--clients must be at least 1")

    python_path = venv_python()
    server_command = build_command(python_path, "chat_server.py")
    client_command = build_command(python_path, "chat_cmdl_client.py", ["-d", "127.0.0.1"])

    if args.no_server or port_is_open():
        print("Using existing chat server on port", CHAT_PORT)
    else:
        print("Starting chat server...")
        open_terminal(server_command)
        if not wait_for_server():
            print("Server did not become ready on port", CHAT_PORT)
            print("Check the server terminal for errors, then run this script again.")
            return 1

    for index in range(args.clients):
        print("Starting chat client", index + 1, "...")
        open_terminal(client_command)
        time.sleep(0.35)

    print("Done. Log in with different names in each client window.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
