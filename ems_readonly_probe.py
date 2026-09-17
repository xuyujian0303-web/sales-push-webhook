"""Read-only authentication probe for the authorized Ems service."""
import argparse
import getpass
import hashlib
import json
import re
import socket
import struct


def read_frame(sock: socket.socket) -> bytes:
    """Read exactly one length-prefixed Ems TCP frame."""
    data = b""
    while len(data) < 4:
        chunk = sock.recv(4096)
        if not chunk:
            return data
        data += chunk
    target = 4 + struct.unpack(">I", data[:4])[0]
    while len(data) < target:
        chunk = sock.recv(min(65536, target - len(data)))
        if not chunk:
            break
        data += chunk
    return data


def field_string(index: int, value: str) -> bytes:
    raw = value.encode("utf-8")
    return b"\x0b" + struct.pack(">H", index) + struct.pack(">I", len(raw)) + raw


def login_frame(username: str, password: str) -> bytes:
    digest = hashlib.md5(password.encode("utf-8")).hexdigest().upper().encode("ascii")
    body = (
        b"\x80\x01\x00\x01"
        + struct.pack(">I", len(b"userLogin")) + b"userLogin"
        + struct.pack(">I", 1)
        + field_string(1, username)
        + b"\x0b\x00\x02" + struct.pack(">I", len(digest)) + digest
        + b"\x00"
    )
    return struct.pack(">I", len(body)) + body


def load_config(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only Ems userLogin probe")
    parser.add_argument("--config", default="ems_config.json")
    parser.add_argument("--send", action="store_true", help="send the read-only userLogin request")
    args = parser.parse_args()
    config = load_config(args.config)
    username = config.get("username") or input("Ems username: ").strip()
    password = config.get("password") or getpass.getpass("Ems password: ")
    host = config.get("auth_host", "giada-erp.redstone.com.cn")
    port = int(config.get("auth_port", 9999))
    frame = login_frame(username, password)
    print(f"frame_bytes={len(frame)} md5=uppercase request=userLogin")
    if not args.send:
        print("dry-run: no network request sent")
        return
    with socket.create_connection((host, port), timeout=15) as conn:
        conn.settimeout(15)
        conn.sendall(frame)
        response = read_frame(conn)
    print(f"response_bytes={len(response)}")
    print(f"response_prefix={response[:64].hex()}")
    text = response.decode("utf-8", errors="ignore")
    status = list(dict.fromkeys(re.findall(r"[\u4e00-\u9fff]{2,}", text)))
    if status:
        print("status_text=" + " | ".join(status))


if __name__ == "__main__":
    main()
