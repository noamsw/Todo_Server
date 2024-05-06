import sys
import re

class SmallShell:
    def __init__(self):
        self.commands = {
            "todo sayhello": self.say_hello,
            "todo exit": self.exit_shell,
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

    def run(self):
        print("Welcome to the Small Shell!")

        while True:
            command = input("$ ")  # Display shell prompt
            smallcommand, arguments = self.parse_command(command)
            self.execute_command(smallcommand, arguments)
    
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
        
    
    def execute_command(self, command, args):
        if command in self.commands:
            self.commands[command](*args)
        else:
            print("Command not found:", command)

    def add_task(self, *args):
        if len(args)!=1:
            print(f'you did not enter the command as expected')
            print(f'the correct format is: todo add-task \"task name\"')
            return
        task_name = args[0]
        if task_name == 'completed' or task_name=='undo':
            print(f'task name can not be completed or undo, please choose a different name')
        if task_name in self.uncompleted_tasks or task_name in self.completed_tasks:
            print(f"There is already a task called \"{task_name}\", please choose a different name")
        else:
            self.uncompleted_tasks.add(task_name)
            print(f"\"{task_name}\" added to list of tasks")
    
    def update_task(self, *args):
        if len(args)!=2:
            print(f'you did not enter the command as expected')
            print(f'the correct format is: todo update-task \"old task name\" \"new task name\"')
            return
        old_task_name = args[0]
        new_task_name = args[1]
        if old_task_name not in self.uncompleted_tasks:
            print(f"There is no uncompleted task called \"{old_task_name}\"")
            return
        if new_task_name in self.uncompleted_tasks or new_task_name in self.completed_tasks:
            print(f"There is already a task called \"{new_task_name}\", please choose a different name")
            return
        if new_task_name == 'completed' or new_task_name=='undo':
            print(f'task name can not be completed or undo, please choose a different name')
        else:
            self.uncompleted_tasks.remove(old_task_name)
            self.uncompleted_tasks.add(new_task_name)
            print(f"\"{old_task_name}\" updated to \"{new_task_name}\"")
    
    def complete_task(self, *args):
        if len(args)!=1:
            print(f'you did not enter the command as expected')
            print(f'the correct format is: todo complete-task \"task name\"')
            return
        task_name = args[0]
        if task_name in self.completed_tasks:
            print(f"{task_name} is already completed")
            return
        if task_name not in self.uncompleted_tasks:
            print(f"there is no task called: \"{task_name}\"")
            return
        self.uncompleted_tasks.remove(task_name)
        self.completed_tasks.add(task_name)
        print(f"\"{task_name}\" completed")
    
    def undo_task(self, *args):
        if len(args)!=1:
            print(f'you did not enter the command as expected')
            print(f'the correct format is: todo undo-task \"task name\"')
            return
        task_name = args[0]
        if task_name in self.uncompleted_tasks:
            print(f"{task_name} is not yet completed")
            return
        if task_name not in self.completed_tasks:
            print(f"there is no task called: \"{task_name}\"")
            return
        self.completed_tasks.remove(task_name)
        self.uncompleted_tasks.add(task_name)
        print(f"\"{task_name}\" moved to uncompleted tasks")

    def delete_task(self, *args):
        if len(args)!=1:
            print(f'you did not enter the command as expected')
            print(f'the correct format is: todo delete-task \"task name\"')
            return
        task_name = args[0]
        if task_name in self.uncompleted_tasks:
            self.uncompleted_tasks.remove(task_name)
            print(f'\"{task_name}\" removed from tasks list')
            return
        if task_name in self.completed_tasks:
            self.completed_tasks.remove(task_name)
            print(f'\"{task_name}\" removed from tasks list')
            return
        print(f"there is no task: \"{task_name}\"")
    
    def list_tasks(self, *args):
        if len(args)!=0:
            print(f'you did not enter the command as expected')
            print(f'the correct format is: todo list-tasks')
            return
        if len(self.completed_tasks)==0 and len(self.uncompleted_tasks)==0:
            print(f'there are no tasks')
            return
        print("{:<30} {:<10}".format("Name", "Completed"))
        for task in self.completed_tasks:
            print("{:<30} {:<10}".format(task, "+"))
        for task_name in self.uncompleted_tasks:
            print("{:<30} {:<10}".format(task_name, "-"))
    
    def list_completed_tasks(self, *args):
        if len(args)!=0:
            print(f'you did not enter the command as expected')
            print(f'the correct format is: todo list-tasks')
            return
        if len(self.completed_tasks)==0:
            print(f'there are no completed tasks')
            return
        print("{:<30} {:<10}".format("Name", "Completed"))
        for task in self.completed_tasks:
            print("{:<30} {:<10}".format(task, "+"))
        
    def say_hello(self):
        print("Hello, I am a small shell")

    def exit_shell(self):
        print("Exiting the shell. Goodbye!")
        sys.exit()

if __name__ == "__main__":
    smallshell = SmallShell()
    smallshell.run()
