"""Protocol validation: replay only read frames in an authorized PCAPNG."""
import argparse
import socket
import struct


def pcap_payload(path: str) -> bytes:
    data = open(path, "rb").read(); offset = 0; payload = b""
    while offset + 12 <= len(data):
        block_type, length = struct.unpack_from("<II", data, offset)
        if length < 12 or offset + length > len(data): break
        if block_type == 6 and length >= 32:
            captured = struct.unpack_from("<I", data, offset + 20)[0]
            packet = data[offset + 28:offset + 28 + captured]
            if len(packet) >= 34 and struct.unpack_from(">H", packet, 12)[0] == 0x0800 and packet[23] == 6:
                tcp = 14 + ((packet[14] & 15) * 4)
                source_port, destination_port = struct.unpack_from(">HH", packet, tcp)
                tcp_payload = packet[tcp + ((packet[tcp + 12] >> 4 & 15) * 4):]
                if source_port >= 49152 and destination_port == 9100:
                    payload += tcp_payload
        offset += length
    return payload


def frames(stream: bytes) -> list[bytes]:
    result = []; offset = 0
    while offset + 4 <= len(stream):
        length = struct.unpack(">I", stream[offset:offset + 4])[0]
        if length < 8 or offset + 4 + length > len(stream): break
        result.append(stream[offset:offset + 4 + length]); offset += 4 + length
    return result


def read_frame(conn: socket.socket) -> bytes:
    response = b""
    while len(response) < 4:
        part = conn.recv(4096)
        if not part: return response
        response += part
    target = 4 + struct.unpack(">I", response[:4])[0]
    while len(response) < target:
        part = conn.recv(min(65536, target - len(response)))
        if not part: break
        response += part
    return response


def method_name(frame: bytes) -> str:
    return frame[12:76].split(b"\x00")[0].decode(errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay authorized Ems read frames only")
    parser.add_argument("pcap")
    parser.add_argument("--host", default="giada-erp.redstone.com.cn")
    parser.add_argument("--port", type=int, default=9100)
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args(); requests = frames(pcap_payload(args.pcap))
    print(f"readonly_frames={len(requests)} send={args.send}")
    if not args.send: return
    with socket.create_connection((args.host, args.port), timeout=15) as conn:
        conn.settimeout(15)
        for index, request in enumerate(requests, 1):
            conn.sendall(request); response = read_frame(conn); method = method_name(request)
            print(f"{index} request_bytes={len(request)} response_bytes={len(response)} method={method}")
            if method == "querySaleDetailList":
                with open("ems_sale_detail_response.bin", "wb") as file: file.write(response)


if __name__ == "__main__":
    main()
