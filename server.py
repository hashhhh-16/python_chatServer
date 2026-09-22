import socket
import select
from datetime import datetime


def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")


# Function to send message to all connected clients
def send_to_all(sock, message):

    # Message is not forwarded to the server and sender itself
    for client in connected_list[:]:

        if client != server_socket and client != sock:

            try:
                client.send(message.encode('utf-8'))

            except:
                client.close()

                if client in connected_list:
                    connected_list.remove(client)


if __name__ == "__main__":

    # Dictionary to store address corresponding to username
    record = {}

    # List to keep track of socket descriptors
    connected_list = []

    buffer = 4096
    port = 5001

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    connected_list.append(server_socket)

    print("\33[32m\t\t\t\tSERVER WORKING\33[0m")
    print(f"Server listening on 127.0.0.1:{port}")

    while True:

        # Get the list of sockets which are ready to be read
        rList, wList, error_sockets = select.select(
            connected_list,
            [],
            []
        )

        for sock in rList:

            # New connection
            if sock == server_socket:

                sockfd, addr = server_socket.accept()

                # Receive username
                name = sockfd.recv(buffer).decode('utf-8').strip()

                connected_list.append(sockfd)

                # Check if username already exists
                if name in record.values():

                    sockfd.send(
                        "\r\33[31m\33[1m "
                        "Username already taken!\n"
                        "\33[0m".encode('utf-8')
                    )

                    connected_list.remove(sockfd)
                    sockfd.close()

                    continue

                else:

                    # Add name and address
                    record[addr] = name

                    print(
                        f"Client {addr} connected [{name}]"
                    )

                    sockfd.send(
                        "\33[32m\r\33[1m "
                        "Welcome to chat room. "
                        "Enter 'tata' anytime to exit\n"
                        "\33[0m".encode('utf-8')
                    )

                    # Notify other clients
                    send_to_all(
                        sockfd,
                        f"\33[32m\33[1m\r "
                        f"[{get_timestamp()}] "
                        f"{name} joined the conversation\n"
                        f"\33[0m"
                    )

            # Incoming message from an existing client
            else:

                try:

                    data = sock.recv(buffer).decode('utf-8').strip()

                    # Client disconnected
                    if not data:
                        raise ConnectionError

                    # Get address of client sending the message
                    addr = sock.getpeername()

                    # Client wants to exit
                    if data == "tata":

                        msg = (
                            "\r\33[1m\33[31m "
                            f"[{get_timestamp()}] "
                            f"{record[addr]} left the conversation "
                            "\33[0m\n"
                        )

                        send_to_all(sock, msg)

                        print(
                            f"Client {addr} is offline "
                            f"[{record[addr]}]"
                        )

                        del record[addr]

                        connected_list.remove(sock)
                        sock.close()

                        continue

                    else:

                        msg = (
                            "\r\33[1m\33[35m "
                            f"[{get_timestamp()}] "
                            f"{record[addr]}: "
                            "\33[0m"
                            f"{data}\n"
                        )

                        send_to_all(sock, msg)

                # Abrupt user exit
                except:

                    try:
                        addr = sock.getpeername()

                    except:
                        continue

                    if addr in record:

                        send_to_all(
                            sock,
                            "\r\33[31m\33[1m "
                            f"[{get_timestamp()}] "
                            f"{record[addr]} "
                            "left the conversation unexpectedly"
                            "\33[0m\n"
                        )

                        print(
                            f"Client {addr} is offline (error) "
                            f"[{record[addr]}]"
                        )

                        del record[addr]

                    if sock in connected_list:
                        connected_list.remove(sock)

                    sock.close()

    server_socket.close()