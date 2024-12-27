import os
import sys
import tarfile
import time
from datetime import datetime

from command_handler import CommandHandler
from virtual_file_system import VirtualFileSystem


def main():
    # Пути файлов
    zip_path = "Boatswain.tar"
    log_file_path = "log.json"

    # Инициализация виртуальной файловой системы и обработчика команд
    vfs = VirtualFileSystem(zip_path)
    command_handler = CommandHandler(vfs, log_file_path)

    print("Welcome to the Virtual File System Emulator!")
    print("Type 'exit' to exit the emulator.")

    # Запуск цикла ввода команд
    while True:
        try:
            command = input(f"{vfs.get_relative_path()} > ").strip()
            if command:
                command_handler.execute_command(command)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
