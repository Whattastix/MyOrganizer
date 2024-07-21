"""Configuration tools used by MyOrganizer"""
from pathlib import Path
from typing import Dict, List, overload, Optional, Union, Any
import json


class Config:
    """Configuration class used by MyOrganizer for the handling of config.json"""

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, json_file: str) -> None: ...

    @overload
    def __init__(self, json_file: Path) -> None: ...

    @overload
    def __init__(self, json_file: None) -> None: ...

    def __init__(self, json_file: Optional[Union[Path, str]]) -> None:
        self.file_types_var: Dict[str, str]
        self.folders_to_organize: List[str]
        self.special_file_types: Dict[str, str]
        self.settings: Dict[str, Any]

        self.__have_read_file: bool = False

        if json_file is not None:
            self.read_file(json_file=json_file)

    def read_file(self, json_file: Path | str) -> None:
        """Reads the config file provided and assigns the values."""
        if self.__have_read_file is True:
            raise self.AlreadyRunError

        self.__have_read_file = True

        if not isinstance(json_file, Path):
            json_file = Path(json_file)

        try:
            with open(json_file, encoding="utf-8") as file:
                temp: Dict[str, dict] = json.loads(file.read())

                if "file-types" in temp and len(temp["file-types"].keys()) > 0:
                    self.file_types_var = temp["file-types"]
                elif "file-types" in temp:
                    raise self.InadequateConfigError("file-types is empty "
                                                     f"in {json_file.name}.")
                else:
                    raise self.InadequateConfigError("file-types is not "
                                                     "defined in "
                                                     f"{json_file.name}.")

                if "folders-to-organize" in temp:
                    self.folders_to_organize = temp["folders-to-organize"]
                elif "folders-to-organize" in temp:
                    raise self.InadequateConfigError("folders-to-organize is"
                                                     "empty in "
                                                     f"{json_file.name}.")
                else:
                    raise self.InadequateConfigError("folders-to-organize is "
                                                     "not defined in "
                                                     f"{json_file.name}.")

                if "special-file-types" in temp:
                    self.special_file_types = temp["special-file-types"]
                else:
                    self.special_file_types = {"unknown-extension": "Misc"}

                if "settings" in temp:
                    self.settings = temp["settings"]
                else:
                    self.settings = {
                        "handle-locked-Files": False
                    }
                file.close()
        except FileNotFoundError as exc:
            with open(json_file, "x", encoding="utf-8") as file:
                file.write(json.dumps({
                    "file-types": {},
                    "organize-folders": [],
                    "settings": {
                        "unknown-extension": "Misc"
                        }
                    }))
                file.close()
            raise FileNotFoundError from exc

    class AlreadyRunError(Exception):
        """Exception to raise when read_file is run more than once."""
        def __init__(self) -> None:
            super().__init__("read_file can only be used once.")

    class InadequateConfigError(Exception):
        """Exception to raise when configuration file does not provide enough settings."""
        def __init__(self, *args: object) -> None:
            super().__init__(*args)
