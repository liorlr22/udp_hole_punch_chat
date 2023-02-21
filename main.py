import threading
import socket

# Constants
HOST = socket.gethostbyname(socket.gethostname())
TCP_PORT = 0
UDP_PORT = 0
BUFFER_SIZE = 1024

# Global variables
client_sockets = []


# Thread for handling user input
def handle_user_input():
    while True:
        # Get input from the user
        command = input("Enter a command (connect, quit): ")

        # If the command is "connect", initiate a hole-punching sequence
        if command == "connect":
            remote_host = input("Enter the remote host: ")
            remote_port = int(input("Enter the remote port: "))

            # Send a hole-punching message to the remote client
            print("Send a hole-punching message to the remote client")
            send_hole_punching_message(remote_host, remote_port)

        # If the command is "quit", exit the program
        elif command == "quit":
            break


# Function for sending hole-punching messages
def send_hole_punching_message(remote_host, remote_port):
    # Create a UDP socket and send the message
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(f"{HOST},{TCP_PORT}".encode(), (remote_host, remote_port))
    udp_socket.close()


# Function for receiving hole-punching messages
def receive_hole_punching_messages():
    # Create a UDP socket and bind it to the local address
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))

    while True:
        # Receive a hole-punching message
        data, addr = udp_socket.recvfrom(BUFFER_SIZE)

        if addr[0] != HOST:
            # Start a new thread to handle the hole-punching message
            hole_punching_thread = threading.Thread(target=handle_hole_punching_message, args=(data, addr[0], addr[1]))
            hole_punching_thread.start()


# Function for handling incoming hole-punching messages
def handle_hole_punching_message(data, remote_host, remote_port):
    # Split the message into the host and port
    host, port = data.decode().split(',')

    # Create a TCP socket and connect to the remote client
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((remote_host, int(port)))

    # Add the client socket to the list
    client_sockets.append(tcp_socket)

    # Start a new thread for receiving messages from the remote client
    receive_thread = threading.Thread(target=receive_messages, args=(tcp_socket,))
    receive_thread.start()


# Function for receiving messages from a client
def receive_messages(client_socket):
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            # If the client socket is closed, remove it from the list and exit the thread
            client_sockets.remove(client_socket)
            break
        print(f"Received message: {data.decode()}")


# Create the TCP socket and bind it to the local address
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((HOST, TCP_PORT))
tcp_socket.listen()

# Start a thread for handling user input
input_thread = threading.Thread(target=handle_user_input)
input_thread.start()

# Accept incoming connections and start a new thread for each client
while True:
    print(f"Host: {HOST}, Port: {tcp_socket.getsockname()[1]} \n")
    print("Waiting for incoming connections...")
    client_socket, addr = tcp_socket.accept()
    print(f"Accepted connection from {addr}")
    client_sockets.append(client_socket)

    # Start a new thread for receiving messages from the client
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # If there are at least two clients connected, initiate a hole-punching sequence between them
    if len(client_sockets) >= 2:
        # Get the remote host and port of the other client
        remote_host, remote_port = client_socket.getpeername()

        for other_socket in client_sockets:
            if other_socket != client_socket:
                # Send a hole-punching message to the other client
                send_hole_punching_message(remote_host, remote_port)

    # Close all client sockets
    for client_socket in client_sockets:
        client_socket.close()

    # Close the TCP socket
    tcp_socket.close()
