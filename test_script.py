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
    
    #call a non existent command
    def test_non_existent_command(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-tasks \"Task 1\" \"also a task\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = "Command not found"
            self.assertEqual(response.strip(), expected_response)

    #add a task to the todo list with incorrect format
    def test_add_task_incorrectly(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\" \"also a task\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = 'you did not enter the command as expected\n'
            expected_response+= 'the correct format is: todo add-task \"task name\"'
            self.assertEqual(response.strip(), expected_response)
    
    #add a task with the name "undo/completed"
    def test_add_task_undo(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"undo\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = 'task name can not be completed or undo, please choose a different name'
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo add-task \"completed\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = 'task name can not be completed or undo, please choose a different name'
            self.assertEqual(response.strip(), expected_response)
    
    #add first task
    def test_add_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            self.assertEqual(response.strip(), "\"Task 1\" added to list of tasks")
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)

    #add task with the same name as an existing task
    def test_add_task_with_same_name(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f"There is already a task called \"Task 1\", please choose a different name"
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)

    #call update response incorrectly
    def test_call_update_task_incorrectly(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo update-task \"Task 2\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = 'you did not enter the command as expected\n'
            expected_response+= 'the correct format is: todo update-task \"old task name\" \"new task name\"'
            self.assertEqual(response.strip(), expected_response)

    #add a task called "Task 2" and update its name to Updated Task
    def test_update_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 2\"".encode())
            client_socket.recv(1024)  # Clear buffer
            client_socket.sendall("todo update-task \"Task 2\" \"Updated Task\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = "\"Task 2\" updated to \"Updated Task\""
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Updated Task\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Updated Task\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)
    
    #update a non existent Task
    def test_update_non_existent_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo update-task \"Task 2\" \"Task 3\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = "There is no uncompleted task called \"Task 2\""
            self.assertEqual(response.strip(), expected_response)

    #update a task name to an existing task name
    def test_update_task_to_existing_name(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 4\"".encode())
            client_socket.recv(1024)  # Clear buffer
            client_socket.sendall("todo add-task \"Task 5\"".encode())
            client_socket.recv(1024)  # Clear buffer
            client_socket.sendall("todo update-task \"Task 4\" \"Task 5\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f"There is already a task called \"Task 5\", please choose a different name"
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Task 5\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 5\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Task 4\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 4\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)

    #update a task name to undo/completed
    def test_update_task_to_undo(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            client_socket.recv(1024)  # Clear buffer
            client_socket.sendall("todo update-task \"Task 1\" \"undo\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'task name can not be completed or undo, please choose a different name'
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo update-task \"Task 1\" \"completed\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'task name can not be completed or undo, please choose a different name'
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)
            

    #complete a task
    def test_complete_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            client_socket.sendall("todo complete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" completed'
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)

    #complete a completed task
    def test_complete_completed_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo complete-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo complete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f"\"Task 1\" is already completed"
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)

    #complete a non existent task
    def test_complete_non_existent_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo complete-task \"giberish\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f"there is no uncompleted task called \"giberish\""
            self.assertEqual(response.strip(), expected_response)
            
    #undo an uncompleted task
    def test_undo_uncompleted_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo undo-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f"\"Task 1\" is not yet completed"
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)
            
    #undo a non existent task
    def test_undo_non_existent_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo undo-task \"giberish\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f"there is no task called: \"giberish\""
            self.assertEqual(response.strip(), expected_response)
    
    #undo a task
    def test_undo_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo complete-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo undo-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f"\"Task 1\" moved to uncompleted tasks"
            self.assertEqual(response.strip(), expected_response)
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)
    
    #delete a non existent task
    def test_delete_non_existent_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo delete-task \"giberish\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f"there is no task: \"giberish\""
            self.assertEqual(response.strip(), expected_response)

    #delete an uncompleted task
    def test_delete_uncomplete_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)
    
    #delete a completed task
    def test_delete_complete_task(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo add-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo complete-task \"Task 1\"".encode())
            client_socket.recv(1024).decode()
            client_socket.sendall("todo delete-task \"Task 1\"".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'\"Task 1\" removed from tasks list'
            self.assertEqual(response.strip(), expected_response)
    
    # test listing no tasks
    def test_list_empty_list(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            client_socket.sendall("todo list-tasks".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'there are no tasks'
            self.assertEqual(response.strip(), expected_response)
    
    #test listing tasks
    def test_list(self):
        tasks = ['Task 1', 'Task 2','Task 3', 'Task 4']
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            for task in tasks:
                client_socket.sendall(f"todo add-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            client_socket.sendall("todo list-tasks".encode())
            response = client_socket.recv(1024).decode()
            expected_response = set()
            expected_response.add("{:<30} {:<10}".format("Name", "Completed"))
            for task in tasks:
                expected_response.add("{:<30} {:<10}".format(task, "-"))
            for task in tasks:
                client_socket.sendall(f"todo delete-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            response_line_array = response.split('\n')
            for line in response_line_array:
                if len(line.strip()) == 0:
                    continue
                self.assertTrue(line in expected_response)
                expected_response.remove(line)
            self.assertTrue(len(expected_response)==0)
    
    #test listing tasks with completed tasks
    def test_list_with_completed_tasks(self):
        completed_tasks = ['Task 1', 'Task 2']
        uncompleted_tasks = ['Task 3', 'Task 4']
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            for task in completed_tasks:
                client_socket.sendall(f"todo add-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            for task in completed_tasks:
                client_socket.sendall(f"todo complete-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            for task in uncompleted_tasks:
                client_socket.sendall(f"todo add-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            client_socket.sendall("todo list-tasks".encode())
            response = client_socket.recv(1024).decode()
            expected_response = set()
            expected_response.add("{:<30} {:<10}".format("Name", "Completed"))
            for task in completed_tasks:
                expected_response.add("{:<30} {:<10}".format(task, "+"))
            for task in uncompleted_tasks:
                expected_response.add("{:<30} {:<10}".format(task, "-"))
            for task in completed_tasks:
                client_socket.sendall(f"todo delete-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            for task in uncompleted_tasks:
                client_socket.sendall(f"todo delete-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            response_line_array = response.split('\n')
            for line in response_line_array:
                if len(line.strip()) == 0:
                    continue
                self.assertTrue(line in expected_response)
                expected_response.remove(line)
            self.assertTrue(len(expected_response)==0)
    
    #test listing completed tasks
    def test_list_completed_tasks(self):
        completed_tasks = ['Task 1', 'Task 2']
        uncompleted_tasks = ['Task 3', 'Task 4']
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            for task in completed_tasks:
                client_socket.sendall(f"todo add-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            for task in completed_tasks:
                client_socket.sendall(f"todo complete-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            for task in uncompleted_tasks:
                client_socket.sendall(f"todo add-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            client_socket.sendall("todo list-completed-tasks".encode())
            response = client_socket.recv(1024).decode()
            expected_response = set()
            expected_response.add("{:<30} {:<10}".format("Name", "Completed"))
            for task in completed_tasks:
                expected_response.add("{:<30} {:<10}".format(task, "+"))
            for task in completed_tasks:
                client_socket.sendall(f"todo delete-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            for task in uncompleted_tasks:
                client_socket.sendall(f"todo delete-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            response_line_array = response.split('\n')
            for line in response_line_array:
                if len(line.strip()) == 0:
                    continue
                self.assertTrue(line in expected_response)
                expected_response.remove(line)
            self.assertTrue(len(expected_response)==0)
    
    #test listing comleted tasks in a list of tasks with no completed tasks
    def test_complete_list_with_no_complete_tasks(self):
        tasks = ['Task 1', 'Task 2','Task 3', 'Task 4']
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(("127.0.0.1", 12345))
            for task in tasks:
                client_socket.sendall(f"todo add-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            client_socket.sendall("todo list-completed-tasks".encode())
            response = client_socket.recv(1024).decode()
            expected_response = f'there are no completed tasks'
            for task in tasks:
                client_socket.sendall(f"todo delete-task \"{task}\"".encode())
                client_socket.recv(1024).decode()
            self.assertEqual(response.strip(), expected_response.strip())






if __name__ == "__main__":
    unittest.main()
