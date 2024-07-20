#!/bin/python3
import argparse
import os
import shutil
from pathlib import Path
from typing import Dict, List
import json

from send2trash import send2trash


def main():
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
    parser.add_argument("-q", "--quiet", help="print no output",
                        action="store_true")
    parser.add_argument("-D", "--debug", help=argparse.SUPPRESS,
                        action="store_true")
    parser.add_argument("-c", "--config", help="specify config file",
                        default=Path(__file__).resolve()
                        .parent.parent.joinpath("config/config.json"),
                        action="store")

    args_ = parser.parse_args()

    file_types_var: Dict[str, str]
    folders_to_organize: List[str]
    special_file_types: Dict[str, str]
    settings: Dict[str, any]

    if args_.dry_run and not args_.quiet:
        print("Running dry-run, no file will be modified")

    try:
        with open(args_.config, encoding="utf-8") as file:
            temp: Dict[str, any] = json.loads(file.read())
            if "file-types" in temp:
                file_types_var = temp["file-types"]
            else:
                file_types_var = {}
            if "folders-to-organize" in temp:
                folders_to_organize = temp["folders-to-organize"]
            else:
                folders_to_organize = []
            if "special-file-types" in temp:
                special_file_types = temp["special-file-types"]
            else:
                special_file_types = {"unknown-extension": "Misc"}
            if "settings" in temp:
                settings = temp["settings"]
            else:
                settings = {
                    "handle-locked-Files": False
                }
            file.close()
    except FileNotFoundError:
        with open(args_.config, encoding="utf-8") as file:
            file.write(json.dumps({
                "file-types": {},
                "organize-folders": [],
                "settings": {
                    "unknown-extension": "Misc"
                    }
                }))
            if not args_.quiet:
                print("Configuration file was missing and was "
                      "automatically generated. Please edit it as necessary.")
        exit(3)

    for folder in folders_to_organize:
        if folder.startswith("$"):
            folder = folder.replace("$HOME", str(Path.home()))
        folder = Path(folder)

        files = list(folder.glob("*"))

        for file in files:

            suffixes: List[str] = file.suffixes
            folder_name: str = None
            files.remove(file)

            if not os.access(file, os.W_OK) or not os.access(file, os.R_OK):
                folder_name = "!ignore"
            elif file.is_dir():
                if "directories" in special_file_types:
                    folder_name = special_file_types["directories"]
                else:
                    folder_name = "!ignore"
            elif file.is_symlink():
                if "symlinks" in special_file_types:
                    folder_name = special_file_types["symlinks"]
                else:
                    for suffix in suffixes:
                        if suffix[1:] in file_types_var:
                            folder_name = file_types_var[suffix[1:]]
            elif suffixes and (
                    suffixes[-1].endswith("#") or
                    suffixes[-1][1:] == "lock" or
                    file.name.startswith("~")
                    ):

                if ("handle-locked-files" in settings
                        and settings["handle-locked-files"]):
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
                if ("handle-locked-files" in settings
                        and settings["handle-locked-files"]):
                    for file_ in files:
                        if file_name in file_.name:
                            files.remove(file_)
                            folder_name = "!ignore"
                            break

                if "extracted-archives" in special_file_types and (
                        ".tar" in file.suffixes or
                        ".zip" in file.suffixes or
                        ".7z" in file.suffixes or
                        ".rar" in file.suffixes):
                    file_name = str(file)
                    for file_ in files:
                        if file_.is_dir() and file_name in file_.name:
                            folder_name = \
                                special_file_types["extracted-archives"]
                if not folder_name:
                    for suffix in suffixes:
                        if suffix[1:] in file_types_var:
                            folder_name = file_types_var[suffix[1:]]
            if not folder_name and not suffixes \
                    and os.access(file, os.X_OK):
                if "executable-no-extension" in special_file_types:
                    folder_name = special_file_types["executable-no-extension"]
                elif "no-extension" in special_file_types:
                    folder_name = special_file_types["no-extension"]
                else:
                    folder_name = special_file_types["unknown-extension"]
            elif not folder_name and not suffixes:
                folder_name = special_file_types["no-extension"]
            if not folder_name:
                folder_name = special_file_types["unknown-extension"]
            if args_.debug:
                print(folder_name)
            if folder_name.startswith("!"):
                match folder_name:
                    case "!ignore":
                        if not args_.quiet:
                            print(f"Ignoring {file}")
                        continue
                    case "!delete":
                        if not args_.quiet:
                            print(f"Deleting {file}")
                        if not args_.dry_run:
                            os.remove(file)
                        continue
                    case "!movetotrash":
                        if not args_.quiet:
                            print(f"Sending {file} to trash")
                            send2trash(file)
                        continue

            destination_folder: Path = folder.joinpath(folder_name)
            if not args_.dry_run and not destination_folder.exists():
                destination_folder.mkdir()

            destination_file: Path = destination_folder.joinpath(file.name)
            i = 1
            while destination_file.exists():
                stem = destination_file.name
                while len(Path(file_name).suffixes) > 0:
                    stem = Path(Path(file_name).stem)
                destination_file = destination_file.parent.joinpath(
                    f"{str(stem)}({i})".join(destination_file.suffixes))
                i += 1
            if not args_.quiet:
                print(f"Moving {file}\nDestination: {destination_file}")
            if not args_.dry_run:
                shutil.move(file, destination_file)


if __name__ == "__main__":
    main()
