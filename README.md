# File Organizer

A simple yet effective CLI-based file organizer with custom features.

## Setting up

1. Clone this repository.  

    ```bash
    git clone
    ```

2. Install requirements.  
    MyCleaner uses the "json5" library instead of json to provide the ability to add comments to the config.json file, since it can get a little crowded in there.

    ```bash
    python3 -m pip install json5
    ```

3. Run `main.py -g` to generate configuration files.

    ```bash
    python3 main.py -g
    ```

4. [Edit the config files as needed.](CONFIG.MD) An example configuration file is included.

5. Run the file.

    ```bash
    python3 main.py 
    ```
