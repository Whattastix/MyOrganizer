#!/bin/python3
import argparse
import os
import shutil
from pathlib import Path
from typing import Dict, List

import json


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
    parser.add_argument("-c", "--config", help="specify config file",
                        default=Path(__file__).resolve()
                        .parent.joinpath("config.json"), action="append")

    args_ = parser.parse_args()

    file_types_var: Dict[str, str]
    folders_to_organize: List[str]
    settings: Dict[str, any]

    try:
        with open(args_.config, encoding="utf-8") as file:
            temp: Dict[str, any] = json.loads(file.read())
            if "file-types" in temp:
                file_types_var = temp["file-types"]
            else:
                file_types_var = {}
            if "organize-folders" in temp:
                folders_to_organize = temp["organize-folders"]
            else:
                folders_to_organize = []
            if "settings" in temp:
                settings = temp["settings"]
            else:
                settings = {"unknown-extension": "Misc"}
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
            if not os.access(file, os.W_OK):
                folder_name = "!ignore"
            elif file.is_dir():
                if "directories" in settings:
                    folder_name = settings["directories"]
                else:
                    folder_name = "!ignore"
            elif file.is_symlink():
                if "symlinks" in settings:
                    folder_name = settings["symlinks"]
                else:
                    for suffix in suffixes:
                        if suffix[1:] in file_types_var:
                            folder_name = file_types_var[suffix[1:]]
            elif suffixes and (
                    suffixes[-1].endswith("#") or
                    suffixes[-1][1:] == "lock" or
                    file.name.startswith("~")
                    ):
                file_name = file.name
                for substring in [".lock", "lock", "~", "#"]:
                    file_name = file_name.replace(substring, "")
                for file_ in files:
                    if file_.name == file_name:
                        files.remove(file_)
                        folder_name = "!ignore"
                        break
            else:
                for file_ in files:
                    if file_name in file_.name:
                        files.remove(file_)
                        folder_name = "!ignore"
                        break
                if not folder_name:
                    for suffix in suffixes:
                        if suffix[1:] in file_types_var:
                            folder_name = file_types_var[suffix[1:]]
            if not folder_name and not suffixes \
                    and os.access(file, os.X_OK):
                if "executable-no-extension" in settings:
                    folder_name = settings["executable-no-extension"]
                elif "no-extension" in settings:
                    folder_name = settings["no-extension"]
                else:
                    folder_name = settings["unknown-extension"]
            elif not folder_name and not suffixes:
                folder_name = settings["no-extension"]
            if not folder_name:
                folder_name = settings["unknown-extension"]
            if folder_name.startswith("!"):
                match folder_name:
                    case "!ignore":
                        print(f"Ignoring {file}")
                        continue
                    case "!delete":
                        if not args_.quiet:
                            print(f"Deleting {file}")
                        if not args_.dry_run:
                            os.remove(file)

            destination_folder: Path = folder.joinpath(folder_name)
            if not args_.dry_run and not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            destination_file: Path = destination_folder.joinpath(file.name)
            if not args_.quiet:
                print(f"Moving {file}\nDestination: {destination_file}")
            if not args_.dry_run:
                shutil.move(file, destination_file)


if __name__ == "__main__":
    main()
