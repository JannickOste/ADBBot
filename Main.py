from net.AdbClient import AdbClient
from misc.Configuration import Configuration
import time, random

from scripts import ArtOfWar, ScriptLoader


class Main:
    def __init__(self):
        Configuration.load()
        self.start_main()

    def start_main(self):
        adb = AdbClient()

        if not adb.devices:
            Configuration.print_debug("AdbClient", "No devices with ADB active found.")
        else:
            scripts = ScriptLoader()

            phone = None
            if len(adb.devices) == 1:
                phone = adb.devices[0]
            if phone:
                scripts.load_script_menu(phone)


if __name__ == "__main__":
    Main()