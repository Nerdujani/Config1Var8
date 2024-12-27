import unittest
import os
import json
from unittest.mock import patch, mock_open
from virtual_file_system import VirtualFileSystem, FileNotFoundException
from command_handler import CommandHandler

class TestVirtualFileSystem(unittest.TestCase):

    def setUp(self):
        # Создаем тестовый TAR-файл для проверки
        self.test_tar_path = "test.tar"
        self.test_root_dir = "MyVirtualMachine"
        with tarfile.open(self.test_tar_path, "w") as tar:
            tar.addfile(tarfile.TarInfo("test_dir/"))
            file_data = tarfile.TarInfo("test_dir/test_file.txt")
            file_data.size = len(b"Hello, World!")
            tar.addfile(file_data, open("test_file.txt", "wb"))

        self.vfs = VirtualFileSystem(self.test_tar_path)

    def tearDown(self):
        # Удаляем все созданные файлы и директории
        if os.path.exists(self.test_root_dir):
            for root, dirs, files in os.walk(self.test_root_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(self.test_root_dir)

        if os.path.exists(self.test_tar_path):
            os.remove(self.test_tar_path)

    def test_extract_tar(self):
        # Проверка успешной распаковки
        self.assertTrue(os.path.exists(os.path.join(self.test_root_dir, "test_dir")))

    def test_extract_tar_missing_file(self):
        # Проверка на ошибку при отсутствии TAR файла
        with self.assertRaises(FileNotFoundException):
            VirtualFileSystem("missing.tar")

    def test_list_directory(self):
        # Проверка содержимого директории
        self.vfs.change_directory("test_dir")
        listing = self.vfs.list_directory()
        self.assertIn("test_file.txt", listing)

    def test_change_directory(self):
        # Проверка смены директории
        self.vfs.change_directory("test_dir")
        self.assertTrue(self.vfs.get_relative_path(), "test_dir")

    def test_change_directory_invalid(self):
        # Проверка ошибки при несуществующей директории
        with self.assertRaises(FileNotFoundException):
            self.vfs.change_directory("missing_dir")

    def test_read_file(self):
        # Проверка чтения файла
        self.vfs.change_directory("test_dir")
        content = self.vfs.read_file("test_file.txt")
        self.assertEqual(content, "Hello, World!")

    def test_read_file_missing(self):
        # Проверка ошибки при отсутствии файла
        with self.assertRaises(FileNotFoundException):
            self.vfs.read_file("missing_file.txt")

    def test_write_file(self):
        # Проверка записи файла
        self.vfs.change_directory("test_dir")
        self.vfs.write_file("new_file.txt", "New content")
        self.assertTrue(os.path.exists(os.path.join(self.vfs.current_path, "new_file.txt")))

    def test_get_directory_tree(self):
        # Проверка структуры директории
        tree = self.vfs.get_directory_tree()
        self.assertIn("test_dir", tree)

class TestCommandHandler(unittest.TestCase):

    def setUp(self):
        # Создание тестовой файловой системы и лог-файла
        self.vfs = VirtualFileSystem("test.tar")
        self.log_file_path = "test_log.json"
        self.command_handler = CommandHandler(self.vfs, self.log_file_path)

    def tearDown(self):
        # Удаление тестового лог-файла
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

    @patch("builtins.print")
    def test_list_directory_command(self, mock_print):
        # Проверка выполнения команды ls
        self.command_handler.execute_command("ls")
        mock_print.assert_called()

    @patch("builtins.print")
    def test_change_directory_command(self, mock_print):
        # Проверка выполнения команды cd
        self.command_handler.execute_command("cd test_dir")
        self.assertEqual(self.vfs.get_relative_path(), "test_dir")

    def test_log_action(self):
        # Проверка записи лога
        self.command_handler.log_action("test_command", "test_result")
        with open(self.log_file_path, "r") as log_file:
            log_entry = json.loads(log_file.readlines()[-1])
            self.assertEqual(log_entry["command"], "test_command")
            self.assertEqual(log_entry["result"], "test_result")

    @patch("builtins.print")
    def test_exit_command(self, mock_print):
        # Проверка команды exit
        with self.assertRaises(SystemExit):
            self.command_handler.execute_command("exit")

if __name__ == "__main__":
    unittest.main()
