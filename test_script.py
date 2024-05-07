import unittest
import subprocess
import socket
import time


class TestSmallShellServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the server in a subprocess
        cls.server_process = subprocess.Popen(["python", "server.py"])

        # Wait for the server to start listening
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        # Terminate the server subprocess
        cls.server_process.terminate()

    def test_add_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            self.assertEqual(response.strip(), "\"Task 1\" added to list of tasks")

    def test_update_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 2\"".encode())
            client_socket.recv(1024)  # Clear buffer
            client_socket.sendall("todo update-task \"Task 2\" \"Updated Task\"".encode())
            response = client_socket.recv(1024).decode()
            self.assertEqual(response.strip(), "\"Task 2\" updated to \"Updated Task\"")

    # Add more test methods for other commands...


if __name__ == "__main__":
    unittest.main()
