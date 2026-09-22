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


# Function to display active users
def get_active_users():
    message = (
        "\n\33[36m\33[1m"
        "╔══════════════════════════════╗\n"
        "║        ACTIVE USERS          ║\n"
        "╠══════════════════════════════╣\n"
        "\33[0m"
    )

    if record:
        for index, username in enumerate(record.values(), start=1):
            message += (
                f"\33[36m║ {index}. {username:<25}║\n"
            )
    else:
        message += "\33[36m║ No active users             ║\n"

    message += (
        "\33[36m\33[1m"
        "╚══════════════════════════════╝\n"
        "\33[0m"
    )

    return message


# Function to display network information
def get_network_info(sock):

    client_ip, client_port = sock.getpeername()

    message = (
        "\n\33[33m\33[1m"
        "╔══════════════════════════════╗\n"
        "║        NETWORK INFO          ║\n"
        "╠══════════════════════════════╣\n"
        f"║ Protocol  : TCP              ║\n"
        f"║ Server IP : 127.0.0.1        ║\n"
        f"║ Server Port: {port:<15}║\n"
        f"║ Your IP   : {client_ip:<15}║\n"
        f"║ Your Port : {client_port:<15}║\n"
        f"║ Active Users: {len(record):<13}║\n"
        "╚══════════════════════════════╝\n"
        "\33[0m"
    )

    return message


if __name__ == "__main__":

    # Dictionary to store address corresponding to username
    record = {}

    # List to keep track of socket descriptors
    connected_list = []

    buffer = 4096
    port = 5001

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

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

                    # Show active users
                    if data == "/users":

                        users_message = get_active_users()

                        sock.send(
                            users_message.encode('utf-8')
                        )

                        continue

                    # Show network information
                    if data == "/info":

                        info_message = get_network_info(sock)

                        sock.send(
                            info_message.encode('utf-8')
                        )

                        continue

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

                    # Normal chat message
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