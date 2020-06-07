import json, pytesseract
from os.path import join
from pathlib import Path
from os import system
import datetime

class Configuration:
    __project_root = Path(__file__).parent.parent
    __configuration_filepath = "lib\\configuration.json"
    __config = dict()
    __first_key = None

    def __init__(self):
        pass

    @classmethod
    def load(cls):
        data = None
        try:
            with open(join(cls.__project_root, cls.__configuration_filepath), "r") as reader:
                data = json.load(reader)
        except Exception as e:
            print(e)
        finally:
            if data:
                cls.__first_key = list(data.keys())[0]
                cls.__config = data[cls.__first_key]
                pytesseract.pytesseract.tesseract_cmd = str(Configuration.get("tesseract_ocr"))

    @classmethod
    def get(cls, value_name: str = None):
        if value_name:
            if isinstance(value_name, str) and value_name in list(cls.__config.keys()):
                return cls.__config[value_name]
        else:
            return cls.__config

    @classmethod
    def print_debug(cls, debug_type :str, debug_str: str, force_print=False):
        if cls.get("debug") or force_print:
            print("[{time}][{debug_type}]: {debug_str}".format(**{
                "debug_type" : debug_type,
                "time": datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S"),
                "debug_str": debug_str
            }))

    @classmethod
    def start_main_file(cls, class_name: str):
        cls.print_debug(class_name, "Script executed from wrong file, attempting to run main file.",
                                  force_print=True)

        try:
            system("python {default_path}\\Main.py".format(default_path=Path(__file__).parent.parent))
        except Exception as e:
            print(e)