from _ctypes_test import func

from misc import Configuration
from net import Phone
from datetime import datetime

"""
    Default configurations for botscripts.
    - Setup script_name/device/package_name/start_time & default functions for script.
    - Scripts must be an extension of ScriptTemplate to be allowed to be loaded in the ScriptLoader
"""
class ScriptTemplate:
    def __init__(self, script_name: str, device: Phone, package_name: str):
        # Defaults globals setup.
        self.device = device
        self.package_name = package_name
        self.script_name = script_name
        self.asset_path = Configuration.get("file_paths")[script_name]
        self.start_time = datetime.now()

    def start(self):
        Configuration.print_debug(self.package_name, "Start function for script has to be overriden.")

    def _get_runtime(self):
        clock_format: str = "%H:%M:%S"

        # Create time into formated str
        _format_time: func = lambda i: str(str(i.hour) + ":" + str(i.minute) + ":" + str(i.second))
        return datetime.strptime(_format_time(datetime.now()), clock_format) \
               - datetime.strptime(_format_time(self.start_time), clock_format)
