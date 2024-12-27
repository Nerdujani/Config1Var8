import os
import tarfile
from datetime import datetime


class FileNotFoundException(Exception):
    pass


class VirtualFileSystem:
    def __init__(self, zip_path):
        self.root = "MyVirtualMachine"
        self.current_path = self.root
        self.extract_tar(zip_path)

    def extract_tar(self, tar_path):
        if not os.path.exists(tar_path):
            raise FileNotFoundException("The TAR file does not exist")
        with tarfile.open(tar_path, "r") as tar:
            tar.extractall(self.root)

    def list_directory(self):
        items = []
        if os.path.exists(self.current_path) and os.path.isdir(self.current_path):
            for file in os.listdir(self.current_path):
                file_path = os.path.join(self.current_path, file)
                size = os.path.getsize(file_path)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                item_type = "Directory" if os.path.isdir(file_path) else "File"
                items.append(f"{item_type:<10} {size:<10} {modified_time} {file}")
        return "\n".join(items)

    def change_directory(self, path):
        if path == "..":
            if self.current_path != self.root:
                self.current_path = os.path.dirname(self.current_path)
            else:
                raise FileNotFoundException("You are already at the root directory")
        else:
            new_path = os.path.join(self.current_path, path)
            if os.path.isdir(new_path):
                self.current_path = os.path.abspath(new_path)
            else:
                raise FileNotFoundException("Directory not found")

    def get_relative_path(self):
        return os.path.relpath(self.current_path, self.root).replace("\\", "/")

    def get_directory_tree(self):
        return self._get_directory_tree_recursive(self.current_path, "")

    def _get_directory_tree_recursive(self, dir_path, indent):
        tree = f"{indent}{os.path.basename(dir_path)}/\n"
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if os.path.isdir(file_path):
                tree += self._get_directory_tree_recursive(file_path, indent + "  ")
            else:
                tree += f"{indent}  {file}\n"
        return tree

    def read_file(self, file_name):
        file_path = os.path.join(self.current_path, file_name)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        else:
            raise FileNotFoundException("File not found")

    def write_file(self, file_name, content):
        file_path = os.path.join(self.current_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
