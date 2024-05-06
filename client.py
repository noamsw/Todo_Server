import socket

# Define host and port
HOST = '127.0.0.1'
PORT = 12345

# Create a socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Connect to the server
    client_socket.connect((HOST, PORT))

    print("Connected to server. Type 'exit' to quit.")

    # REPL loop
    while True:
        # Prompt the user for a command
        command = input("> ").strip()

        # If the user types 'exit', close the connection and break the loop
        if command.lower() == 'exit':
            print("Exiting...")
            break
        if len(command) == 0:
            continue
        # Send the command to the server
        client_socket.sendall(command.encode())

        # Receive and print the response from the server
        response = client_socket.recv(1024).decode()
        print(response)
