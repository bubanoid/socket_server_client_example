import sys
import socket
import struct


def recvall(sock: socket.socket, n: int) -> bytes | None:
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def read_massage(sock: socket.socket) -> str | None:
    # Read the 4-byte length
    message_length_encoded = recvall(sock, 4)
    if not message_length_encoded:
        print("Socket closed")
        sys.exit(0)

    message_length = struct.unpack('>I', message_length_encoded)[0]
    return recvall(sock, message_length).decode()


so = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
)

so.connect(("localhost", 8000))  # Blocking
print("Connected")

try:
    message = "Hello, give me a weather, please".encode()

    # Pack the length of the message into 4 bytes (big-endian)
    message_length = struct.pack('>I', len(message))
    sent = so.send(message_length + message)  # Blocking
    print(f"Sent {sent} bytes")

    while True:
        msg = read_massage(so)
        print(msg)

except KeyboardInterrupt:
    so.close()
    print("Socket closed")
    sys.exit(0)
