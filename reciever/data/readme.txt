Create the virtual environment:

    Use the python -m venv command followed by the desired name for your virtual environment.
    A common practice is to name it venv or env.
    For example: python -m venv myenv.
    This command creates a new directory named myenv (or whatever you named it) in your project directory. This directory will contain the necessary files and directories for your virtual environment, including the Python executable and a site-packages directory where packages will be installed. 

Activate the virtual environment:

    On Windows (using Command Prompt): myenv\Scripts\activate
    On Windows (using PowerShell): . \myenv\Scripts\Activate.ps1
    On macOS/Linux (using Bash/Zsh): source myenv/bin/activate
    On macOS/Linux (using Fish): source myenv/bin/activate.fish

Download requirments.txt
    pip install --no-index --find-links /path/to/offline_folder -r requirements.txt

