#!/usr/bin/env python3
"""GUI classes and variables used by MyOrganizer"""

import errno
from argparse import Namespace
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, QTimer
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtWidgets import (QWidget, QProgressBar, QTextEdit,
                               QVBoxLayout, QLabel,
                               QMessageBox)

from config import Config
from organization_tools import get_folder_name, handle_file

src_icon_path = Path(__file__).resolve().parent.parent.joinpath("img/logo.png")
ICONPATH: str = (
    str(src_icon_path) if src_icon_path.exists()
    else str(Path(__file__).resolve().parent.joinpath("img/logo.png"))
)


class QLoad(QWidget):
    """Custom QWidget for MyOrganizer providing status as GUI."""

    def __init__(self, config, args_):
        super().__init__()

        self.setWindowTitle("MyOrganizer")
        self.setWindowIcon(QIcon(ICONPATH))
        self.setFixedSize(400, 240)
        self.setMinimumSize(400, 240)

        self.folder_progress = QProgressBar()
        self.folder_progress.setFormat("Scanning folders... (%v/%m)")

        self.label = QLabel("Scanning folder:")

        self.file_progress = QProgressBar()
        self.file_progress.setFormat("Scanning files... (%v/%m)")

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.folder_progress)
        layout.addWidget(self.label)
        layout.addWidget(self.file_progress)
        layout.addWidget(self.log)

        self.setLayout(layout)

        self.worker_thread = QThread(parent=self)

        self.worker = Worker()

        self.worker.folder_progress_set_range.connect(
            self.folder_progress.setRange)
        self.worker.folder_progress_update_value.connect(
            self.folder_progress.setValue)
        self.worker.file_progress_set_range.connect(
            self.file_progress.setRange)
        self.worker.file_progress_update_value.connect(
            self.file_progress.setValue)
        self.worker.folder_update_label.connect(self.label.setText)
        self.worker.add_text.connect(self.add_log_text)

        self.worker.update.connect(self.update)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread().quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(lambda: self.worker.run(
            config=config, args_=args_
        ))

        self.wait_timer = QTimer(self)
        self.wait_timer.setSingleShot(True)
        self.wait_timer.setInterval(100)
        self.wait_timer.timeout.connect(self.worker_thread.start)
        self.wait_timer.start()

    def add_log_text(self, text: str):
        """Adds text at the beginning of the log"""
        self.log.moveCursor(QTextCursor.MoveOperation.Start)
        self.log.insertPlainText(text)


class Worker(QObject):
    """GUI implementation of organize_folders worker class."""
    folder_progress_update_value = Signal(int)
    file_progress_update_value = Signal(int)
    folder_progress_set_range = Signal(int, int)
    file_progress_set_range = Signal(int, int)
    add_text = Signal(str)
    folder_update_label = Signal(str)

    update = Signal()
    finished = Signal()

    def run(self, config: Config, args_: Namespace):
        """GUI implementation of organize_folders."""

        self.folder_progress_set_range.emit(0, len(config.folders_to_organize))
        folder_val = 0

        for folder in config.folders_to_organize:
            if folder.startswith("$"):
                folder = folder.replace("$HOME", str(Path.home()))
            folder_path = Path(folder)
            self.folder_update_label.emit(f"Scanning folder: {folder}")

            if not folder_path.exists():
                if not args_.quiet:
                    msgbox = QMessageBox(QMessageBox.Icon.Critical,
                                         "MyOrganizer",
                                         f"Folder {folder_path.resolve()} does not "
                                         "exist. Please double-check the path."
                                         )
                    msgbox.setWindowIcon(QIcon(ICONPATH))
                    msgbox.exec()
                    exit(errno.ENOENT)

            files = list(folder_path.glob("*"))

            self.file_progress_set_range.emit(1, len(files))
            self.file_progress_update_value.emit(1)

            file_val = 1

            while files:
                file = files.pop(0)
                folder_name = get_folder_name(
                    file=file, files=files, config=config, args_=args_)
                handle_file(file=file, parent_folder=folder,
                            folder_name=folder_name, args_=args_,
                            update_function=lambda text:
                            self.add_text.emit(f"{text}\n"))
                file_val += 1
                self.file_progress_update_value.emit(file_val)
                self.update.emit()

            folder_val += 1
            self.folder_progress_update_value.emit(folder_val)
        self.finished.emit()
