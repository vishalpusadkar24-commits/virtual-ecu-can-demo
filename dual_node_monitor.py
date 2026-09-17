"""
Connects to both simulated nodes in the two-node virtual CAN network demo
(see virtual_ecu_twonode_demo.resc) at once, and prints their UART output
side by side with a tag showing which node it came from.

This is the same pattern as hardware_simulator.py, applied to two
independent virtual ECUs sharing one CAN bus - useful for watching both
sides of a CAN exchange (e.g. an ECU and a diagnostic tester) without
needing physical hardware or a second serial cable.

Usage:
    python dual_node_monitor.py [duration_seconds]
"""

import socket
import sys
import threading
import time

NODES = [
    ("ECU", "127.0.0.1", 3456),
    ("TESTER", "127.0.0.1", 3457),
]

DURATION_S = float(sys.argv[1]) if len(sys.argv) > 1 else 12.0


def stream_node(label, host, port, deadline):
    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            sock.settimeout(0.5)
            print(f"[{label}] connected to {host}:{port}")
            buffer = ""
            while time.time() < deadline:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk.decode("utf-8", errors="replace")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if line:
                            print(f"[{label}] {line}")
                except socket.timeout:
                    continue
            if buffer.strip():
                print(f"[{label}] {buffer.strip()}")
    except OSError as e:
        print(f"[{label}] connection failed: {e}")


def main():
    deadline = time.time() + DURATION_S
    threads = [
        threading.Thread(target=stream_node, args=(label, host, port, deadline))
        for label, host, port in NODES
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("\n[monitor] done.")


if __name__ == "__main__":
    main()
