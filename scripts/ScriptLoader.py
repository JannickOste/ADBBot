from os import listdir
from os.path import isfile, join
from pathlib import Path
import importlib

from misc import Configuration
from net import Phone


class ScriptLoader:
    def __init__(self):
        self.script_root = Path(__file__).parent
        self.ignored_files = ["__init__", "ScriptLoader", "ScriptTemplate"]
        self.scripts = self.__get_script_modules()

    def __get_script_modules(self):
        script_files = [f for f in listdir(self.script_root) if isfile(join(self.script_root, f))]
        script_files = [self.__import_script_module(f) for f in script_files if not f.split(".")[0] in self.ignored_files]

        return script_files

    def __import_script_module(self, script_name: str, **kwargs):
        module_config: dict = dict()
        module_config["name"]: Path = Path(join(self.script_root, script_name)).stem
        module_config["module"]: importlib = getattr(importlib.import_module(".".join([Path(join(self.script_root, script_name)).parent.stem, module_config["name"]])), module_config["name"])

        return module_config

    def load_script_menu(self, device: Phone):
        for indx, i in enumerate(self.scripts):
            print("[{indx}]: {i}".format(indx=indx, i=i["name"]))

        while True:
            inp: str = input("Enter corespondent script id to launch the script: ")
            if inp.isdigit():
                script_config = self.scripts[int(inp[0])]
                Configuration.print_debug(script_config["name"], "Starting script.")
                return script_config["module"](device).start()