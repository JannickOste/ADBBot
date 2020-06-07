# Library imports
import random, time, cv2, datetime
from _ctypes_test import func
from os import listdir
from os.path import isfile, join
from typing import Union

from net import Phone
from misc import Configuration
from scripts import ScriptTemplate


# Main script class.
class ArtOfWar(ScriptTemplate):
    def __init__(self, device: Phone) -> None:
        super(ArtOfWar, self).__init__("art_of_war", device,
                                       "com.addictive.strategy.army/com.addictive.strategy.army.UnityPlayerActivity")

        # Bots counters/settings/assets
        self.conf: dict = {
            "battles_played": 0,
            "enable_lootboxes": False,
            "last_action": datetime.datetime.now(),
            "next_lootbox": datetime.datetime.now(),
            "update_screen": False,
            "images": {},
            "current_action": {
                "state": "",
                "location": (0, 0)
            }
        }

        # Load image assets.
        for fn in [f for f in listdir(self.asset_path) if isfile(join(self.asset_path, f))]:
            self.conf["images"] = {**self.conf["images"], **{fn.split(".")[0]: cv2.imread(join(self.asset_path, fn))}}

    """
        getLocation(state_name: str)
        - Fetch location for clicks.
        
        @:return (width, height))
    """
    def __getLocation(self, state_name: str = None, custom_color_code: list = None) -> Union:
        state_name: str = self.conf["current_action"]["state"] if state_name is None else state_name

        if not state_name in list(self.conf["images"].keys()):
            Configuration.print_debug("ArtOfWar::getLocation({state_name})".format(state_name=state_name),
                                      "Unable to fetch location for {state_name}".format(state_name=state_name))
            return
        else:
            # Fetch the current phone display & image to identify a state.
            _search_image: Union = self.conf["images"][state_name]
            _display_image: Union = self.device.screenshot(image_type="cv2", update=self.conf["update_screen"])

            # Search image within display image with opencv.
            _mask: Union = cv2.matchTemplate(_search_image, _display_image, cv2.TM_SQDIFF_NORMED)
            _, _, _mn, _ = cv2.minMaxLoc(_mask)

            # Check or the pixel background matches the color of submit buttons.
            custom_color_code = custom_color_code if all([not custom_color_code, state_name != "exit"]) else [132, 91, 33]
            _check_color_code: func = lambda i: i == custom_color_code if custom_color_code else i == [0, 204, 253]
            if _check_color_code(list(_display_image[_mn[1], _mn[0]])):
                # Get size of preloaded image, and  create position tuple with positions based on image search &
                # - image size offset.
                _image_size: tuple = (len(_search_image[0]), len(_search_image))
                _pos: tuple = tuple(
                    (round(_mn[i] + _image_size[i] / 100 * 40), round(_mn[i] + _image_size[i] / 100 * 75)) for i in
                    range(len(_mn)))

                return tuple(map(lambda s: random.randint(s[0], s[1]), _pos))

    """
        getAction(opt: state_name)
        - Executes actions required for specific state, voided function(no return)
    """

    def __getAction(self, state_name: str = None) -> None:
        state_name: str = self.conf["current_action"]["state"] if state_name is None or not isinstance(state_name,
                                                                                                       str) else state_name
        _loc: tuple = ()
        if state_name != "in_battle":
            _loc = self.conf["current_action"]["location"] if self.conf["current_action"][
                                                                  "state"] == state_name else self.__getLocation(
                state_name)

        # Handles the battle start functionality.
        if state_name == "battle":
            # Start the actual battle.
            Configuration.print_debug("ArtOfWar::Logger", "Battle button found, Starting new match.")
            while True:
                if _loc:  # Send 2 touch press inputs with delay (battle & battle start button).
                    for i in range(2):
                        self.device.press(_loc[0], _loc[1])
                        time.sleep(2)
                    break
            self.__getAction("in_battle")

        # Actual in-battle loop process.
        elif state_name == "in_battle":
            # Create a loop for if next button isnt found and cap to few scans to increase speed(about +20% faster)
            battle_time = datetime.datetime.now() + datetime.timedelta(seconds=15)
            _loc = self.__getLocation("next")
            self.conf["update_screen"] = True

            while all([not _loc, datetime.datetime.now() <= battle_time]):
                self.device.press(round(self.device.display_size[0] / 2),
                                  round(self.device.display_size[1] / 100 * 40))

                _loc = self.__getLocation("next")
            if _loc:
                self.device.press(_loc[0], _loc[1])

        # If the next button to return to the main menu has been found:
        elif state_name == "next":
            self.conf["battles_played"] += 1

            self.device.press(self.conf["current_action"]["location"][0], self.conf["current_action"]["location"][1])
            next_lootbox = self.conf["next_lootbox"] - datetime.datetime.now()

            # Create/print statistics string.
            statics_str = "Botlog:\n" \
                          "- {battles_played} battles played.\n" \
                          "- Average battles per hour: {timer}.\n" \
                          "- Next lootbox scan in: {next_lootbox} minutes.".format(**{
                "battles_played": self.conf["battles_played"],
                "timer": round(datetime.timedelta(hours=1) / self._get_runtime(), 1),
                "next_lootbox": "{min}:{sec}".format(**{
                    "min": round(next_lootbox.total_seconds() // 60),
                    "sec": round(abs(next_lootbox.seconds - (60 * int(next_lootbox.total_seconds() / 60))))
                })
            })

            Configuration.print_debug("ArtOfWar::Statics", statics_str)

        elif state_name == "open":  # @!todo: Add looper for box opening to fix getting stuck (similair battle while loop method?)
            self.device.press(_loc[0], _loc[1])

            while True:
                _loc = self.__getLocation("open")
                if _loc:
                    self.device.press(_loc[0], _loc[1])
                    break

        elif state_name == "exit":
            print("Exit sceen found attempting to exit...")
            self.device.press(_loc[0], _loc[1])

        else:  # Default action if action isnt specified.
            Configuration.print_debug("ArtOfWar", "Unable to fetch game action {action}.".format(
                action=self.conf["current_action"]["state"]))

    """
        start
        - start overide for the default start function in ScriptTemplate,
            required to start with ScriptLoader.
    """

    def start(self) -> None:
        while True:
            # Loop through the possible game states
            for state_id, state_name in enumerate(["open", "battle", "next", "exit"]):
                # Only update screen first iteration.
                self.conf["update_screen"] = True if state_id <= 1 else False

                # if not passed lootbox check timer continue to next state.
                if state_name == "open" and datetime.datetime.now() <= self.conf["next_lootbox"]:
                    continue

                if self.package_name in str(self.device.get_focused_apk()):
                    _loc = self.__getLocation(state_name)
                    # If an image is found in the state screen and it isnt the same as the previous executed state:
                    if all([_loc, state_name != self.conf["current_action"]["state"]]):
                        # Set current actions values.
                        self.conf = {**self.conf,
                            "current_action": {
                                "state": state_name,
                                "location": _loc,
                                "last_action": datetime.datetime.now()
                            }
                        }

                        # if a open lootbox icon is found, add scan delay to increase speed.
                        if state_name == "open":
                            self.conf["next_lootbox"] = datetime.datetime.now() + datetime.timedelta(minutes=30)

                            Configuration.print_debug("ArtOfWar::Logger", "Active lootbox found, attempting to open.")
                        # Get actions for current state.
                        self.__getAction()

                    # If searching for a lootbox but no location is found, add 5min delay for next lootbox scan.
                    elif state_name == "open":
                        self.conf["next_lootbox"] = datetime.datetime.now() + datetime.timedelta(minutes=5)

                        Configuration.print_debug("ArtOfWar::Logger",
                                                  "Searched for lootbox without results, adding 5min delay for scan.")
                else:
                    self.device.open_apk(self.package_name)


if __name__ == "__main__":
    Configuration.start_main_file("ArtOfWar")