import sqlite3
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
        # use SQLite for an in-memory database
        self.connection = sqlite3.connect(":memory:")
        self.cursor = self.connection.cursor()

        # Create tasks table with a unique name
        # self.table_name = f"tasks_{int(time.time())}"
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS Tasks (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                task TEXT UNIQUE,
                                status TEXT
                            )''')
        self.connection.commit()
        # Set up signal handler to catch termination signals
                      

    def close_server(self):
        self.cursor.close()
        self.connection.close()

    #release resources when done
    def __del__(self):
        self.close_server()

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

    # parse the command given into the command and arguments
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

    #check if the command is recognized and run it if so
    def execute_command(self, command, args, client_socket):
        if command in self.commands:
            result = self.commands[command](*args)
            client_socket.sendall(result.encode())
        else:
            client_socket.sendall("Command not found".encode())

    # add a task to the list of tasks
    def add_task(self, *args):
        if len(args)!=1:
            result = 'you did not enter the command as expected\n'
            result+= 'the correct format is: todo add-task \"task name\"'
            return result
        task_name = args[0]
        if task_name == 'completed' or task_name=='undo':
            return f'task name can not be completed or undo, please choose a different name'
        try:
            self.cursor.execute("INSERT INTO Tasks (task, status) VALUES (?,?)", (task_name, '-'))
            self.connection.commit()
            return f"\"{task_name}\" added to list of tasks"
        except sqlite3.IntegrityError:
            return f"There is already a task called \"{task_name}\", please choose a different name"

    #change the name of an existing task to a new name
    #the new name must not be the name of another existing task
    def update_task(self, *args):
        if len(args)!=2:
            result = f'you did not enter the command as expected\n'
            result+= f'the correct format is: todo update-task \"old task name\" \"new task name\"'
            return result
        old_task_name = args[0]
        new_task_name = args[1]
        if new_task_name == 'completed' or new_task_name=='undo':
            return f'task name can not be completed or undo, please choose a different name'
        self.cursor.execute("SELECT * FROM Tasks WHERE task=?", (old_task_name,))
        existing_task = self.cursor.fetchone()

        if existing_task:
            # Check if the new task name already exists
            self.cursor.execute("SELECT * FROM Tasks WHERE task=?", (new_task_name,))
            existing_new_task = self.cursor.fetchone()

            if existing_new_task:
                return f"There is already a task called \"{new_task_name}\", please choose a different name"
            else:
                # Update the old task name to the new one
                self.cursor.execute("UPDATE Tasks SET task=? WHERE task=?", (new_task_name, old_task_name))
                self.connection.commit()
                return f"\"{old_task_name}\" updated to \"{new_task_name}\""
        else:
            return f"There is no uncompleted task called \"{old_task_name}\""

    #move an existing task from the uncompleted task to completed
    def complete_task(self, *args):
        if len(args)!=1:
            result = f'you did not enter the command as expected\n'
            result+= f'the correct format is: todo complete-task \"task name\"'
            return result
        task_name = args[0]
        #check if the task exits and is completed
        self.cursor.execute("SELECT * FROM Tasks WHERE task=? AND status=?", (task_name, '+'))
        existing_task = self.cursor.fetchone()
        if existing_task:
            return f"\"{task_name}\" is already completed"
        # Check if the task exists and is uncompleted
        self.cursor.execute("SELECT * FROM Tasks WHERE task=? AND status=?", (task_name, '-'))
        existing_task = self.cursor.fetchone()

        if existing_task:
            # Update the status of the task
            self.cursor.execute("UPDATE Tasks SET status=? WHERE task=?", ('+', task_name))
            self.connection.commit()
            return f"\"{task_name}\" completed"
        else:
            return f"there is no uncompleted task called \"{task_name}\""

    #move a completed task to uncomplete
    def undo_task(self, *args):
        if len(args)!=1:
            result = f'you did not enter the command as expected\n'
            result+= f'the correct format is: todo undo-task \"task name\"'
            return result
        task_name = args[0]
        # Check if the task exists and is uncompleted
        self.cursor.execute("SELECT * FROM Tasks WHERE task=? AND status=?", (task_name, '-'))
        existing_task = self.cursor.fetchone()
        if existing_task:
            return f"\"{task_name}\" is not yet completed"
        # Check if the task exists and is completed
        self.cursor.execute("SELECT * FROM Tasks WHERE task=? AND status=?", (task_name, '+'))
        existing_task = self.cursor.fetchone()
        
        if existing_task:
            # Update the status of the task
            self.cursor.execute("UPDATE Tasks SET status=? WHERE task=?", ('-', task_name))
            self.connection.commit()
            return f"\"{task_name}\" moved to uncompleted tasks"
        else:
            return f"there is no task called: \"{task_name}\""
    
    #remove a task from the list
    #completed or not
    def delete_task(self, *args):
        if len(args)!=1:
            result = f'you did not enter the command as expected\n'
            result+= f'the correct format is: todo delete-task \"task name\"'
            return result
        task_name = args[0]
        # Check if the task exists
        self.cursor.execute("SELECT * FROM Tasks WHERE task=?", (task_name,))
        existing_task = self.cursor.fetchone()

        if existing_task:
            # Delete the task from the Tasks table
            self.cursor.execute("DELETE FROM Tasks WHERE task=?", (task_name,))
            self.connection.commit()
            return f'\"{task_name}\" removed from tasks list'
        else:
            return f"ERROR there is no task: \"{task_name}\""

    #list the tasks in the DB, both completed and uncompleted
    def list_tasks(self, *args):
        if len(args)!=0:
            result = f'you did not enter the command as expected'
            result+= f'the correct format is: todo list-tasks'
            return result
        # Fetch all tasks from the database
        self.cursor.execute("SELECT task, status FROM Tasks")
        tasks = self.cursor.fetchall()
        if not tasks:
            return f'there are no tasks'
        
        result = "{:<30} {:<10}\n".format("Name", "Completed")
        for task, status in tasks:
            if status == '+':
                result += "{:<30} {:<10}\n".format(task, "+")
            elif status == '-':
                result += "{:<30} {:<10}\n".format(task, "-")

        return result
    
    #list the completed tasks in the DB
    def list_completed_tasks(self, *args):
        if len(args)!=0:
            result = f'you did not enter the command as expected'
            result+= f'the correct format is: todo list-tasks'
            return result
        self.cursor.execute("SELECT task, status FROM Tasks")
        tasks = self.cursor.fetchall()
        if not tasks:
            return f'there are no tasks'
        completed = False
        result = "{:<30} {:<10}\n".format("Name", "Completed")
        for task, status in tasks:
            if status == '+':
                result += "{:<30} {:<10}\n".format(task, "+")
                completed = True
        if not completed:
            return f'there are no completed tasks'
        return result

    #a little hello
    def say_hello(self):
        return "Hello, I am a small server"

if __name__ == "__main__":
    smallshell_server = SmallShellServer()
    smallshell_server.start_server()
