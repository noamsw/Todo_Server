import pytest
import subprocess

# Path to your client script
CLIENT_SCRIPT_PATH = "path/to/your/client/script.py"

@pytest.fixture(scope="module")
def server_process():
    # Start the server as a subprocess
    server_process = subprocess.Popen(["python", "path/to/your/server/script.py"])
    yield server_process
    # Terminate the server process after tests are finished
    server_process.terminate()

def test_add_task(server_process):
    # Test adding a new task
    command = "todo add-task Task1"
    output = subprocess.check_output(["python", CLIENT_SCRIPT_PATH], input=command.encode()).decode().strip()
    assert output == "\"Task1\" added to list of tasks"

    # Test adding a task with the same name
    command = "todo add-task Task1"
    output = subprocess.check_output(["python", CLIENT_SCRIPT_PATH], input=command.encode()).decode().strip()
    assert "already a task called" in output

def test_list_tasks(server_process):
    # Test listing tasks
    command = "todo list-tasks"
    output = subprocess.check_output(["python", CLIENT_SCRIPT_PATH], input=command.encode()).decode().strip()
    assert "Task1" in output

def test_complete_task(server_process):
    # Test completing a task
    command = "todo complete-task Task1"
    output = subprocess.check_output(["python", CLIENT_SCRIPT_PATH], input=command.encode()).decode().strip()
    assert "Task1" in output and "completed" in output

    # Test completing a task that is already completed
    command = "todo complete-task Task1"
    output = subprocess.check_output(["python", CLIENT_SCRIPT_PATH], input=command.encode()).decode().strip()
    assert "already completed" in output

    # Test completing a non-existent task
    command = "todo complete-task NonExistentTask"
    output = subprocess.check_output(["python", CLIENT_SCRIPT_PATH], input=command.encode()).decode().strip()
    assert "no uncompleted task called" in output

# Add more test functions for other commands as needed

if __name__ == "__main__":
    pytest.main(["-v", __file__])


