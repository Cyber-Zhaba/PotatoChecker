import subprocess
import os
import sys


def setup_venv_win():
    commands = [fr'set venv_root_dir={os.getcwd()}',
                fr'set venv_install_dir=%venv_root_dir%\venv',
                fr'cd %venv_root_dir%',
                fr'python -m venv venv',
                fr'call %venv_install_dir%\Scripts\activate.bat',
                fr'pip install -r requirements.txt',
                fr'pip freeze > %venv_install_dir%\pip-freeze-%venv_name%.txt',
                fr'call %venv_install_dir%\Scripts\deactivate.bat',
                fr'start /B %venv_install_dir%\Scripts\python.exe %venv_root_dir%\WebApp\main.py',
                fr'start /B %venv_install_dir%\Scripts\python.exe %venv_root_dir%\BotApp\main.py']

    with open('setup.bat', 'w') as file:
        file.write('\n'.join(commands))


def setup_venv_lin():
    commands = [fr'cd {os.getcwd()}',
                fr'python -m venv venv',
                fr'source {os.getcwd()}/venv/bin/activate',
                fr'pip install -r requirements.txt',
                fr'pip freeze > {os.getcwd()}/venv/pip-freeze-venv.txt',
                fr'{os.getcwd()}/venv/bin/python {os.getcwd()}/WebApp/main.py &',
                fr'{os.getcwd()}/venv/bin/python {os.getcwd()}/BotApp/main.py &',
                fr'deactivate']

    with open('setup.sh', 'w') as file:
        file.write('\n'.join(commands))


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        setup_venv_win()
        subprocess.call(['setup.bat'])
    else:
        setup_venv_lin()
        print('Please run setup.sh file')
