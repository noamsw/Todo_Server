import sys
import re
import socket

class SmallShellServer:
    def __init__(self):
        self.commands = {
            "todo sayhello": self.say_hello,
            "todo add-task": self.add_task,
            "todo update-task": self.update_task,
            "todo complete-task": self.complete_task,
            "todo undo-task": self.undo_task,
            "todo delete-task": self.delete_task,
            "todo list-tasks": self.list_tasks,
            "todo list-completed-tasks": self.list_completed_tasks,
        }
        self.uncompleted_tasks = set()
        self.completed_tasks = set()

    def start_server(self, host='127.0.0.1', port=12345):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Server listening on {host}:{port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connected to client: {client_address}")

            self.handle_client(client_socket)

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break
                command, args = self.parse_command(data)
                self.execute_command(command, args, client_socket)
            except Exception as e:
                print(f"Error handling client request: {e}")
                break
        print("Closing connection")
        client_socket.close()

    def parse_command(self, command):
        pattern = r'^\s*(\S+)\s+(\S+)\s*(?:"([^"]*)")?\s*(?:"([^"]*)")?(.*)$'
        match = re.match(pattern, command)
        if match:
        # Extract the command name and optional arguments
            small_command = match.group(1) +" "+ match.group(2)
            arg1 = match.group(3)
            arg2 = match.group(4)
        else:
            print(f'unable to parse command')
        optional_args = [arg for arg in (arg1, arg2) if arg is not None]
        return small_command, optional_args

    def execute_command(self, command, args, client_socket):
        if command in self.commands:
            result = self.commands[command](*args)
            client_socket.sendall(result.encode())
        else:
            client_socket.sendall("Command not found".encode())

    def add_task(self, *args):
        if len(args)!=1:
            result = 'you did not enter the command as expected\n'
            result+= 'the correct format is: todo add-task \"task name\"'
            return result
        task_name = args[0]
        if task_name == 'completed' or task_name=='undo':
            result = 'task name can not be completed or undo, please choose a different name'
        elif task_name in self.uncompleted_tasks or task_name in self.completed_tasks:
            result = f"There is already a task called \"{task_name}\", please choose a different name"
        else:
            self.uncompleted_tasks.add(task_name)
            result = f"\"{task_name}\" added to list of tasks"
        return result

    def update_task(self, *args):
        if len(args)!=2:
            result = f'you did not enter the command as expected\n'
            result+= f'the correct format is: todo update-task \"old task name\" \"new task name\"'
            return result
        old_task_name = args[0]
        new_task_name = args[1]
        if old_task_name not in self.uncompleted_tasks:
            result = f"There is no uncompleted task called \"{old_task_name}\""
        elif new_task_name in self.uncompleted_tasks or new_task_name in self.completed_tasks:
            result = f"There is already a task called \"{new_task_name}\", please choose a different name"
        elif new_task_name == 'completed' or new_task_name=='undo':
            result = f'task name can not be completed or undo, please choose a different name'
        else:
            self.uncompleted_tasks.remove(old_task_name)
            self.uncompleted_tasks.add(new_task_name)
            result = f"\"{old_task_name}\" updated to \"{new_task_name}\""
        return result

    def complete_task(self, *args):
        if len(args)!=1:
            result = f'you did not enter the command as expected\n'
            result+= f'the correct format is: todo complete-task \"task name\"'
            return result
        task_name = args[0]
        if task_name in self.completed_tasks:
            result=f"\"{task_name}\" is already completed"
        elif task_name not in self.uncompleted_tasks:
            result = f"there is no uncompleted task called \"{task_name}\""
        else:
            self.uncompleted_tasks.remove(task_name)
            self.completed_tasks.add(task_name)
            result = f"\"{task_name}\" completed"
        return result

    def undo_task(self, *args):
        if len(args)!=1:
            result = f'you did not enter the command as expected\n'
            result+= f'the correct format is: todo undo-task \"task name\"'
            return result
        task_name = args[0]
        if task_name in self.uncompleted_tasks:
            result = f"\"{task_name}\" is not yet completed"
        elif task_name not in self.completed_tasks:
            result = f"there is no task called: \"{task_name}\""
        else:
            self.completed_tasks.remove(task_name)
            self.uncompleted_tasks.add(task_name)
            result = f"\"{task_name}\" moved to uncompleted tasks"
        return result

    def delete_task(self, *args):
        if len(args)!=1:
            result = f'you did not enter the command as expected\n'
            result+= f'the correct format is: todo delete-task \"task name\"'
            return result
        task_name = args[0]
        if task_name in self.uncompleted_tasks:
            self.uncompleted_tasks.remove(task_name)
            result = f'\"{task_name}\" removed from tasks list'
        elif task_name in self.completed_tasks:
            self.completed_tasks.remove(task_name)
            result = f'\"{task_name}\" removed from tasks list'
        else:
            result = f"there is no task: \"{task_name}\""
        return result
    
    def list_tasks(self, *args):
        if len(args)!=0:
            result = f'you did not enter the command as expected'
            result+= f'the correct format is: todo list-tasks'
            return result
        if len(self.completed_tasks)==0 and len(self.uncompleted_tasks)==0:
            result = f'there are no tasks'
        else:
            result = "{:<30} {:<10}\n".format("Name", "Completed")
            for task in self.completed_tasks:
                result+="{:<30} {:<10}\n".format(task, "+")
            for task in self.uncompleted_tasks:
                result+="{:<30} {:<10}\n".format(task, "-")
        return result
        
    def list_completed_tasks(self, *args):
        if len(args)!=0:
            result = f'you did not enter the command as expected'
            result+= f'the correct format is: todo list-tasks'
            return result
        if len(self.completed_tasks)==0:
            result = f'there are no completed tasks'
        else:
            result = "{:<30} {:<10}\n".format("Name", "Completed")
            for task in self.completed_tasks:
                result+="{:<30} {:<10}\n".format(task, "+")
        return result

    def say_hello(self):
        return "Hello, I am a small server"

if __name__ == "__main__":
    smallshell_server = SmallShellServer()
    smallshell_server.start_server()
