import socket
import select
import sys


# Helper function for formatting
def display():
    you = "\33[33m\33[1m" + " You: " + "\33[0m"
    sys.stdout.write(you)
    sys.stdout.flush()


def main():

    if len(sys.argv) < 2:
        host = input("Enter host ip address: ")
    else:
        host = sys.argv[1]

    port = 5001

    # Ask for username
    name = input(
        "\33[34m\33[1m"
        " CREATING NEW ID:\n"
        " Enter username: "
        "\33[0m"
    )

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    s.settimeout(2)

    # Connect to host
    try:
        s.connect((host, port))

    except:
        print(
            "\33[31m\33[1m "
            "Can't connect to the server "
            "\33[0m"
        )
        sys.exit()

    # Send username to server
    s.send(name.encode('utf-8'))

    display()

    while True:

        socket_list = [sys.stdin, s]

        # Get sockets which are ready to be read
        rList, wList, error_list = select.select(
            socket_list,
            [],
            []
        )

        for sock in rList:

            # Incoming message from server
            if sock == s:

                data = sock.recv(4096)

                if not data:

                    print(
                        "\33[31m\33[1m"
                        "\rDISCONNECTED FROM SERVER!!\n"
                        "\33[0m"
                    )

                    s.close()
                    sys.exit()

                else:

                    sys.stdout.write(
                        data.decode('utf-8')
                    )

                    display()

            # User entered a message
            else:

                msg = sys.stdin.readline().strip()

                # Exit command
                if msg.lower() == "exit":

                    s.send(
                        "exit".encode('utf-8')
                    )

                    print(
                        "\n\33[31m\33[1m"
                        "Disconnected from server."
                        "\33[0m"
                    )

                    s.close()
                    sys.exit()

                # Send normal message
                s.send(
                    msg.encode('utf-8')
                )

                display()


if __name__ == "__main__":
    main()