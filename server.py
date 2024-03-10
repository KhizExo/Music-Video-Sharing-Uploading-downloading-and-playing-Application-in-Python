import socket
import os

def is_file_present(filename):
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, filename)
    
    return os.path.isfile(file_path)

def transfer_file(conn, filename):
    # Open the file in binary mode
    file = open(filename, 'rb')

    # Read the file data in chunks and send it to the client
    while True:
        data = file.read(1024)
        if not data:
            break
        conn.send(data)

    # Close the file and connection
    file.close()
    conn.close()

def server():
    # Server IP address and port
    server_ip = '127.0.0.1'
    server_port = 1234

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the server IP address and port
    server_socket.bind((server_ip, server_port))

    # Listen for incoming connections
    server_socket.listen(1)
    print('Server is listening for incoming connections...')

    while True:
        # Accept a client connection
        conn, addr = server_socket.accept()
        print('Connected to client:', addr)

        # Receive the filename from the client
        filename = conn.recv(1024).decode()
        print('Received filename:', filename)

        # Transfer the file to the client
        if is_file_present(filename):
            transfer_file(conn, filename)
            print('File transfer complete.')
        else:
            message = "File not found!"
            conn.sendall(message.encode())

    # Close the server socket
    server_socket.close()

if __name__ == '__main__':
    server()