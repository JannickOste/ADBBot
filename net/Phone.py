from os import listdir
from os.path import isfile, join

from ppadb.device import Device
import json
from misc import Configuration
import cv2
from PIL import Image
import numpy
from io import BytesIO


class Phone(Device):
    def __init__(self, device : Device, serial_no: str):
        super(Phone, self).__init__(device, serial_no)
        self.__config_root = Configuration.get("file_paths")["phone_configuration"]
        self.__display_image = None

        # Create configuration file for each phone -> if existing doesnt exist yet.
        if not "{serial}.json".format(serial=self.get_serial_no()) in [f for f in listdir(self.__config_root) if isfile(join(self.__config_root, f))]:
            Configuration.print_debug("DeviceHandler", "New device connected with serial no '{serial}'.\n- Creating configuration for file".format(serial=self.get_serial_no()))
            self.build_phone_configuration()

    @property
    def display_size(self):
        result = self.shell("dumpsys window | grep 'DisplayFrames'")
        return tuple(map(lambda i: int(i.split("=")[1]), result.strip().split(" ")[1:3]))

    def get_focused_apk(self):
        result = self.shell('dumpsys window | grep -e "mCurrentFocus"')

        if result:
            result = result.strip()[result.find("{")+1:result.find("}")].split(" ")
            result = result[2] if len(result)==3 else None

        return result

    def files_in_path(self, filepath: str = "/") -> list:
        result = [i.strip() for i in self.shell("ls {filepath}".format(filepath=filepath)).split("\n") if not "Permission denied" in i]
        return [i for i in " ".join(result).split(" ") if i]

    def build_phone_configuration(self) -> None:
        default_configuration, package_list = {}, {}
        for package in self.list_packages():
            try:
                if package:
                    package_list = {**package_list,
                        package: {
                            "version": self.get_package_version_name(package),
                        }
                    }
            except Exception as e:
                Configuration.print_debug("Phone->build_phone_configuration", str(e))
            finally:
                default_configuration = {self.get_serial_no(): {
                    "storage_root": "/storage/emulated/0/",
                    "packages": {**package_list}
                }}

        with open(join(self.__config_root, "{serial_no}.json".format(serial_no=self.get_serial_no())), "w+") as writer:
            json.dump(default_configuration, writer)

    """
        parse_display_image_location
        - Gives default image path if not any path specified, otherwise return set path.
    """
    def __parse_display_image_location(self, location: str = "") -> str:
        return Configuration.get("file_paths")["default_display_image"] if not location else location

    """
        Screenshot
        - Creates an image of the phone's display and save/load into cv2/uint8 or PIL array.
    """
    def screenshot(self, image_type: str = None, update:bool = True):
        if update or self.__display_image is None:
            self.__display_image = Image.open(BytesIO(self.screencap()))

        image = self.__display_image

        if image_type == "cv2":
            image = cv2.cvtColor(numpy.array(image, dtype=numpy.uint8), cv2.COLOR_RGB2BGR)

        elif image_type == "cv2_arr":
            image = numpy.array(self.screenshot(image_type="cv2"), dtype=numpy.uint8)

        return image

    def search_image_on_screen(self, search_image, centered=False):
        display_image = self.screenshot(image_type="cv2")
        search_image = cv2.imread(search_image) if isinstance(search_image, str) else search_image
        image_mask = cv2.matchTemplate(search_image, display_image, cv2.TM_SQDIFF_NORMED)
        _, mn, mx2, mx = cv2.minMaxLoc(image_mask)
        if not centered:
            return mx2
        else:
            return mx2[0]+len(search_image[0]), mx2[1]+round(len(search_image) / 2)

    def press(self, x, y):
        self.shell("input touchscreen swipe {x} {y} {x} {y} 5".format(x=x, y=y))

    def open_apk(self, package_name:str):
        return self.shell("am start -n {package_name}".format(package_name=package_name))