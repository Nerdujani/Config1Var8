import json
import sys
import time
from virtual_file_system import FileNotFoundException


class CommandHandler:
    def __init__(self, vfs, log_file_path):
        self.vfs = vfs
        self.log_file_path = log_file_path

    def execute_command(self, command):
        if command.startswith("ls"):
            self.list_directory()
        elif command.startswith("cd"):
            self.change_directory(command)
        elif command.startswith("exit"):
            self.exit()
        elif command.startswith("cp"):
            self.copy_file(command)
        elif command.startswith("tree"):
            self.tree()
        else:
            print(f"Unknown command: {command}")

    def list_directory(self):
        result = self.vfs.list_directory()
        print(result)
        self.log_action("ls", result)

    def change_directory(self, command):
        path = command[2:].strip()
        try:
            self.vfs.change_directory(path)
            self.log_action("cd", f"Changed directory to {path}")
        except FileNotFoundException as e:
            print(e)

    def exit(self):
        self.log_action("exit", "Exiting emulator")
        print("Goodbye!")
        sys.exit(0)

    def copy_file(self, command):
        args = command.split()
        if len(args) == 3:
            source, destination = args[1], args[2]
            try:
                content = self.vfs.read_file(source)
                self.vfs.write_file(destination, content)
                print(f"Copied from {source} to {destination}")
                self.log_action("cp", f"Copied from {source} to {destination}")
            except FileNotFoundException as e:
                print(e)
        else:
            print("Invalid arguments for cp command")

    def tree(self):
        result = self.vfs.get_directory_tree()
        print(result)
        self.log_action("tree", result)

    def log_action(self, command, result):
        log_entry = {
            "command": command,
            "result": result,
            "timestamp": int(time.time())
        }
        try:
            with open(self.log_file_path, "a") as log_file:
                log_file.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Error logging action: {e}")
