# Configuration

## File Types

### Overview

File types refer to the suffixes at the end of the file. If a file has more than one suffix, the last matching one is used. The syntax is as follows:

```json
{
    "file-types": {
        "suffix1": "folder name",
        "suffix2": "specialcode"
    }
}
```

As seen above, suffixes are written first and then the destination folder is written. Alternatively, a special character can also be used.

### Special commands

* `!ignore`: Ignore the file.
* `!delete`: Delete the file.
* `!movetotrash`: Move the file to the trash bin.

## Special File Types

There are also some special file types located in `special-file-types`.:

* `unknown-extension`: Files with no matching extensions. Defaults to `!ignore`.
* `no-extension`: Files without any suffixes. Falls back to `unknown-extension`.
* `executable-no-extension`: Executable files (x flag) without any suffixes. Falls back to `no-extension`.
* `directories`: Directories. Ignored if not present.
* `symlinks`: Symlinks. Falls back to the latest suffix.

## Folders to be organized

This is where you add folders to be handled. The syntax is as follows:

```json
    {
        "folders-to-organize": [
            "example-dir"
        ]
    }
```

It is recommended that you write the the absolute path of the directories. If you want to point to your home directory, you can use `$HOME` which will be replaced with `Path.home()`.
