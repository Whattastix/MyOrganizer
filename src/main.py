#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
from threading import Thread
import sys
import errno

from config import Config
from organization_tools import get_folder_name, handle_file

from PySide6.QtWidgets import QMessageBox, QApplication, QWidget
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtCore import QThread

from gui import QLoad, ICONPATH


def main() -> None:
    """Main function."""

    parser = argparse.ArgumentParser(
        prog="MyOrganizer",
        description="Easy to use file organizer."
    )
    parser.add_argument("-d", "--dry-run",
                        help="do not perform folder and file creation,"
                        " move, or deletion",
                        action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="print extra info", action="store_true")
    parser.add_argument("-g", "--gui",
                        help="Use gui instead of cli", action="store_true")
    parser.add_argument("-q", "--quiet", help="print no output",
                        action="store_true")
    parser.add_argument("-D", "--debug", help=argparse.SUPPRESS,
                        action="store_true")
    parser.add_argument("-c", "--config", help="specify config file",
                        default=Path(__file__).resolve()
                        .parent.parent.joinpath("config/config.json"),
                        action="store")

    args_ = parser.parse_args()

    if args_.gui is True:
        app = QApplication(sys.argv)
        global ICON
        ICON = QIcon(ICONPATH)

    if args_.debug and not args_.quiet:
        import faulthandler
        faulthandler.enable()
        global PYTHONFAULTHANDLER
        PYTHONFAULTHANDLER = 1
        if args_.gui is True:
            msgbox = QMessageBox(QMessageBox.Icon.Information,
                                 "MyOrganizer", "Debug mode active.")
            msgbox.setWindowIcon(ICON)
            msgbox.exec()
        else:
            print("Debug mode active.")

    if args_.dry_run and not args_.quiet:
        if args_.gui is True:
            msgbox = QMessageBox(QMessageBox.Icon.Information,
                                 "MyOrganizer", "Running dry-run,"
                                 " no file will be modified")
            msgbox.setWindowIcon(ICON)
            msgbox.exec()
        else:
            print("Running dry-run, no file will be modified")

    config = read_config(args_)

    if args_.gui is True:
        window = QLoad(config=config, args_=args_)
        window.show()
        sys.exit(app.exec())
    else:
        organize_folders_cli(config=config, args_=args_)
        sys.exit(os.X_OK)


def read_config(args_: argparse.Namespace) -> Config:
    """Reads the config file and handles possible exceptions."""
    try:
        config = Config(args_.config)
    except Config.InadequateConfigError:
        if not args_.quiet:
            if args_.gui is True:
                msgbox = QMessageBox(QMessageBox.Icon.Warning,
                                     "MyOrganizer", "Configuration file "
                                     "was missing and was automatically "
                                     "generated. Please edit it "
                                     "as necessary.")
                msgbox.setWindowIcon(ICON)
                msgbox.exec()
            else:
                print("Configuration file was missing and was "
                      "automatically generated. Please edit "
                      "it as necessary.")
        sys.exit(3)
    except FileNotFoundError:
        if not args_.quiet:
            if args_.gui is True:
                msgbox = QMessageBox(QMessageBox.Icon.Warning,
                                     "MyOrganizer", "Configuration file "
                                     "was missing and was automatically "
                                     "generated. Please edit it "
                                     "as necessary.")
                msgbox.setWindowIcon(ICON)
                msgbox.exec()
            else:
                print("Configuration file was missing and was "
                      "automatically generated. Please edit "
                      "it as necessary.")
        sys.exit(errno.ENOENT)
    except PermissionError:
        if not args_.quiet:
            if args_.gui is True:
                msgbox = QMessageBox(QMessageBox.Icon.Critical,
                                     "MyOrganizer", "You do not have adequate"
                                     " permission to read "
                                     f"{args_.config.name}.")
                msgbox.setWindowIcon(ICON)
                msgbox.exec()
            else:
                print("You do not have adequate permission to read"
                      f"{args_.config.name}.")
        sys.exit(errno.EPERM)
    except OSError as exc:
        if not args_.quiet:
            if args_.gui is True:
                msgbox = QMessageBox(QMessageBox.Icon.Critical,
                                     "MyOrganizer", f"An exception was raised."
                                     f" Details:\n{type(exc).__name__}: {exc}")
                msgbox.setWindowIcon(ICON)
                msgbox.exec()
            else:
                print("Configuration file could not be read. Please make "
                      "sure that you have read permission to the file.")
        sys.exit(errno.EIO)

    return config


def organize_folders_cli(config: Config,
                         args_: argparse.Namespace):
    """Organizes the folders. Main component of MyOrganizer."""
    for folder in config.folders_to_organize:
        if folder.startswith("$"):
            folder = folder.replace("$HOME", str(Path.home()))
        folder = Path(folder)

        if not folder.exists():
            if not args_.quiet:
                print(f"Folder {folder.resolve()} does not exist."
                      " Please double-check the path.")

        files = list(folder.glob("*"))

        for file in files:
            files.remove(file)
            folder_name = get_folder_name(file=file, files=files,
                                          config=config, args_=args_)
            handle_file(file=file, parent_folder=folder,
                        folder_name=folder_name, args_=args_,
                        update_function=print)


if __name__ == "__main__":
    main()
