"""
External "hardware simulator" for the virtual ECU co-simulation demo.

Connects to the TCP socket that Renode exposes for the simulated Nucleo
H753ZI's UART (see demo_v2_socket_cosim.resc / CreateServerSocketTerminal).
This mirrors, at a small scale, the pattern used in production pre-silicon
validation setups: firmware runs entirely inside a simulator, and an
external process (here, a plain Python script; in the field, anything from
a Python rig to real test equipment) drives or observes it over a socket
instead of a physical wire.

Usage:
    python hardware_simulator.py [host] [port] [duration_seconds]
"""

import socket
import sys
import time

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 3456
DURATION_S = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0


def main():
    print(f"[sim] connecting to virtual ECU UART at {HOST}:{PORT} ...")
    with socket.create_connection((HOST, PORT), timeout=10) as sock:
        sock.settimeout(0.5)
        print("[sim] connected. Streaming UART output from the simulated firmware:\n")

        deadline = time.time() + DURATION_S
        buffer = bytearray()
        while time.time() < deadline:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer.extend(chunk)
                text = chunk.decode("utf-8", errors="replace")
                sys.stdout.write(text)
                sys.stdout.flush()
            except socket.timeout:
                continue

        print("\n\n[sim] done. Received", len(buffer), "bytes total from the virtual ECU.")


if __name__ == "__main__":
    main()
