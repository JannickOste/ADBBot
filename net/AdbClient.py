from ppadb.client import Client
from ppadb.device import Device

from misc import Configuration
from net.Phone import Phone


class AdbClient(Client):
    def __init__(self):
        # Fetch default host & port for ADB connection.
        host, port = Configuration.get("adb_addr")
        super(AdbClient, self).__init__(host=host, port=port) # Create a connection with adb.

    @property
    def devices(self, state=None):
        return list(map(lambda i: Phone(i, i.get_serial_no()), super().devices()))

    def get_device_info(self, phone : Phone):
        return {
            "serial_no": phone.get_serial_no(),
            "battery_level": phone.get_battery_level(),
            "focused_app": phone.get_focused_apk(),
            "package_list": phone.list_packages()
        }

