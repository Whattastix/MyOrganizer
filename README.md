# MyOrganizer

A simple yet effective CLI-based customizable file organizer.

## Setting up

MyOrganizer supports both running directly and bundling via PyInstaller.

### Running Directly

1. Clone this repository.  

    ```bash
    git clone https://github.com/Whattastix/MyOrganizer.git
    ```

2. Install the required libraries. You may want to create a virtual environment first.

    ```bash
    python3 -m venv env 
    source env/bin/activate

    pip install -r requirements.txt
    ```

3. [Edit the config files as needed.](CONFIG.md) An example configuration file is included.

4. Run the file. You may move the .py file as necessary.

    ```bash
    python3 src/main.py 
    ```

### Bundling via PyInstaller

1. Clone this repository.  

    ```bash
    git clone https://github.com/Whattastix/MyOrganizer.git
    ```

2. Install the required libraries. You may want to create a virtual environment first.

    ```bash
    python3 -m venv env 
    source env/bin/activate

    pip install -r requirements.txt
    pip install -r requirements-build.txt
    ```

3. Use the following command to use pyinstaller. The program will be located in the dist directory.

   ```bash
    ./env/bin/pyinstaller ./MyOrganizer.spec --distpath ./dist --workpath ./temp
   ```

4. [Edit the config files as needed.](CONFIG.md) An example configuration file is included.

5. Run the file. You can now move the MyOrganizer folder to wherever necessary

    ```bash
    ./MyOrganizer
    ```
