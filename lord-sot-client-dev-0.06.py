import socket
import threading

# Server details
SERVER_IP = "127.0.0.1"  # Replace with the server's IP address if running on another machine
PORT = 9999

def main_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_IP, PORT))
        print("Connected to the server. Waiting for game updates...")

        def listen_for_messages():
            try:
                while True:
                    message = client.recv(1024).decode()
                    if not message:
                        print("Server disconnected.")
                        break
                    print(f"Server: {message}")
            except ConnectionResetError:
                print("Connection to the server was lost.")
            finally:
                print("Exiting the game...")
                client.close()
                exit(0)

        # Start a thread to listen for server messages
        threading.Thread(target=listen_for_messages, daemon=True).start()

        # Handle user input for name and actions
        name = input("> Enter your name: ")
        client.sendall(name.encode())  # Send name to server

        while True:
            action = input("> ")
            client.sendall(action.encode())

    except ConnectionRefusedError:
        print("Unable to connect to the server. Make sure the server is running.")
    except KeyboardInterrupt:
        print("\nExiting the game...")
    finally:
        client.close()

if __name__ == "__main__":
    main_client()

