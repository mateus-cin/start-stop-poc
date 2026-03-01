import socket
import datetime
import string
import os
import platform

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4444
BUFFER_SIZE = 65535

last_88 = None
last_96 = None


def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def format_hex_ascii(data: bytes, width: int = 16) -> str:
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(
            chr(b) if 32 <= b <= 126 else "."
            for b in chunk
        )
        lines.append(f"{i:04X}  {hex_part:<{width*3}}  {ascii_part}")
    return "\n".join(lines)


def print_packet(title, packet_info):
    if packet_info is None:
        print(f"{title}: No packet received yet\n")
        return

    timestamp, addr, data = packet_info
    print("=" * 80)
    print(f"{title}")
    print("=" * 80)
    print(f"Timestamp : {timestamp}")
    print(f"Source    : {addr[0]}:{addr[1]}")
    print(f"Size      : {len(data)} bytes")
    print("-" * 80)
    print(format_hex_ascii(data))
    print("\n")


def main():
    global last_88, last_96

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))

    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}...")

    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        size = len(data)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if size == 88:
            last_88 = (timestamp, addr, data)
        elif size == 96:
            last_96 = (timestamp, addr, data)
        else:
            continue  # Ignore unexpected sizes

        clear_console()

        print("UDP PACKET VISUALIZER (Tracking 88 & 96 byte packets)\n")

        print_packet("LAST 88 BYTE PACKET", last_88)
        print_packet("LAST 96 BYTE PACKET", last_96)


if __name__ == "__main__":
    main()