"""Organization tools for MyOrganizer"""
from pathlib import Path
from typing import List, Callable, Optional
import os
import argparse
import shutil

from send2trash import send2trash

from config import Config


def get_folder_name(file: Path, files: List[Path], config: Config,
                    args_: argparse.Namespace) -> str:
    """Gets folder name using the info in the config file."""
    suffixes: List[str] = file.suffixes
    folder_name: Optional[str] = None

    if not os.access(file, os.W_OK) or not os.access(file, os.R_OK):
        folder_name = "!ignore"
    elif file.is_dir():
        if file.name not in config.file_types_var.values() and "directories" in config.special_file_types:
            folder_name = config.special_file_types["directories"]
        else:
            folder_name = "!ignore"
    elif file.is_symlink():
        if "symlinks" in config.special_file_types:
            folder_name = config.special_file_types["symlinks"]
        else:
            for suffix in suffixes:
                if suffix[1:] in config.file_types_var:
                    folder_name = config.file_types_var[suffix[1:]]
    elif suffixes and (
            suffixes[-1].endswith("#") or
            suffixes[-1][1:] == "lock" or
            file.name.startswith("~")
    ):

        if ("handle-locked-files" in config.settings
                and config.settings["handle-locked-files"]):
            file_name = file.name
            for substring in [".lock", "lock", "~", "#"]:
                file_name = file_name.replace(substring, "")
            for file_ in files:
                if file_.name == file_name:
                    files.remove(file_)
                    folder_name = "!ignore"
                    break
        elif suffixes[-1][1:] == "lock":
            suffixes.pop()

    else:
        file_name = file.name
        if ("handle-locked-files" in config.settings
                and config.settings["handle-locked-files"]):
            for file_ in files:
                if file_name in file_.name:
                    files.remove(file_)
                    folder_name = "!ignore"
                    break

        if "extracted-archives" in config.special_file_types and (
                ".tar" in file.suffixes or
                ".zip" in file.suffixes or
                ".7z" in file.suffixes or
                ".rar" in file.suffixes):
            file_name = str(file)
            for file_ in files:
                if file_.is_dir() and file_name in file_.name:
                    folder_name = \
                        config.special_file_types["extracted-archives"]
        if not folder_name:
            for suffix in suffixes:
                if suffix[1:] in config.file_types_var:
                    folder_name = config.file_types_var[suffix[1:]]
    if not folder_name and not suffixes \
            and os.access(file, os.X_OK):
        if "executable-no-extension" in config.special_file_types:
            folder_name = config.special_file_types[
                "executable-no-extension"]
        elif "no-extension" in config.special_file_types:
            folder_name = config.special_file_types["no-extension"]
        else:
            folder_name = config.special_file_types[
                "unknown-extension"]
    elif not folder_name and not suffixes:
        folder_name = config.special_file_types["no-extension"]
    if not folder_name:
        folder_name = config.special_file_types["unknown-extension"]
    if args_.debug and not args_.quiet:
        print(folder_name)
    return folder_name


def handle_file(file: Path, parent_folder: str, folder_name: str,
                args_: argparse.Namespace,
                update_function: Callable[[str], None]):
    """Handles files."""
    if folder_name.startswith("!"):
        match folder_name:
            case "!ignore":
                if not args_.quiet:
                    update_function(f"Ignoring {file}")
                return
            case "!delete":
                if not args_.quiet:
                    update_function(f"Deleting {file}")
                if not args_.dry_run:
                    os.remove(file)
                return
            case "!movetotrash":
                if not args_.quiet:
                    update_function(f"Sending {file} to trash")
                if not args_.dry_run:
                    send2trash(file)
                return

    destination_folder: Path = Path(parent_folder).joinpath(folder_name)
    if not args_.dry_run and not destination_folder.exists():
        destination_folder.mkdir()

    destination_file: Path = destination_folder.joinpath(file.name)
    i = 1
    stem = Path(destination_file.name)
    while destination_file.exists():
        while len(Path(stem).suffixes) > 0:
            stem = Path(Path(stem).stem)
        destination_file = destination_file.parent.joinpath(
            f"{str(stem)}({i})".join(destination_file.suffixes))
        i += 1
    if not args_.quiet:
        update_function(f"Moving {file}\nDestination: {destination_file}")
    if not args_.dry_run:
        shutil.move(file, destination_file)
