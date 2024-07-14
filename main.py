#!/bin/python3
import argparse
import os
import shutil
from pathlib import Path
from typing import Dict, List

import json5 as json


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        prog="MyOrganizer",
        description="Easy to use file organizer."
    )
    parser.add_argument("-d", "--dry-run", help="do not perform folder and file creation, move, or deletion", action="store_true")
    parser.add_argument("-v", "--verbose", help="print extra info", action="store_true")
    parser.add_argument("-q", "--quiet", help="print no output", action="store_true")
    parser.add_argument("-c", "--config", help="specify config file",
                        default=os.path.join(Path(os.path.realpath(__file__)).parent, "config.json"), action="append")

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
                print("Configuration file was missing and was automatically generated. Please edit it as necessary")
        exit(3)

    for folder in folders_to_organize:
        if folder.startswith("$"):
            folder = folder.replace("$HOME", str(Path.home()))
        for file in os.listdir(folder):
            file = Path(os.path.join(folder, file))
            suffixes: List[str] = Path(file).suffixes
            foldername: str = None

            try:
                if file.is_dir():
                    foldername = settings["directories"]
                elif file.is_symlink():
                    foldername = settings["symlinks"]
                else:
                    if suffixes and suffixes[-1].endswith("#"):
                        suffixes[-1] = suffixes[-1][:-1]  # Lock files with "#" have the hash symbol removed
                    elif suffixes and suffixes[-1][1:] == "lock":
                        suffixes.pop()  # Ignore the "lock" suffix because it is usually used by editors
                    for suffix in suffixes:
                        if suffix[1:] in file_types_var:
                            foldername = file_types_var[suffix[1:]]
                if not foldername and not suffixes and os.access(file, os.X_OK):
                    if "executable-no-extension" in settings:
                        foldername = settings["executable-no-extension"]
                    elif "no-extension" in settings:
                        foldername = settings["no-extension"]
                    else:
                        foldername = settings["unknown-extension"]
                elif not foldername:
                    foldername = settings["unknown-extension"]
            except KeyError:
                foldername = "!ignore"
            if foldername.startswith("!"):
                match foldername:
                    case "!ignore":
                        print(f"Ignoring {file}")
                        continue
                    case "!delete":
                        if not args_.quiet:
                            print(f"Deleting {file}")
                        if not args_.dry_run:
                            os.remove(file)

            destination_folder: str = os.path.join(folder, foldername)
            if not args_.dry_run and not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            destination_file: Path = os.path.join(destination_folder, file.name)
            if not args_.quiet:
                print(f"Moving {file}\nDestination: {destination_file}")
            if not args_.dry_run:
                shutil.move(file, destination_file)


if __name__ == "__main__":
    main()
