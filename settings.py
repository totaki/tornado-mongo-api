import importlib
import os

settings = importlib.import_module(os.environ.get('SETTINGS_MODULE'))
