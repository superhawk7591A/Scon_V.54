rmdir /s /q tmp.venv
py -m venv create tmp.venv
tmp.venv\bin\python -m pip install <list-of-packages-from-pypi-you-use>
tmp.venv\bin\python PSmain.py