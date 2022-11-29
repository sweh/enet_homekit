"""An example of how to setup and start an Accessory.
This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import logging
import signal
import random

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader
from pyhap.const import CATEGORY_WINDOW_COVERING

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")


class Jalousie(Accessory):
    """"""

    category = CATEGORY_WINDOW_COVERING

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_state = self.add_preload_service('WindowCovering')
        # ['CurrentPosition', 'TargetPosition', 'PositionState']
        self.char_current_position = serv_state.configure_char('CurrentPosition')
        self.char_current_position.setter_callback = self.current_position_changed
        self.char_target_position = serv_state.configure_char('TargetPosition')
        self.char_target_position.setter_callback = self.target_position_changed
        self.char_position_state = serv_state.configure_char('PositionState')
        self.char_position_state.setter_callback = self.position_state_changed

    def current_position_changed(self, value):
        print('Current position changed to: ', value)

    def target_position_changed(self, value):
        # set_target_position_on_enet(100-value)
        import time
        time.sleep(5)
        self.char_current_position.set_value(value)
        print('Target position changed to: ', value)

    def position_state_changed(self, value):
        print('Position state changed to: ', value)

    @Accessory.run_at_interval(60)
    async def run(self):
        value = 50
        self.char_target_position.set_value(value)
        self.char_current_position.set_value(value)


def get_accessory(driver, name='FakeJalousie'):
    """Call this method to get a standalone Accessory."""
    return Jalousie(driver, name)


def get_bridge(driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(driver, 'Jalousien')
    bridge.add_accessory(get_accessory(driver))
    bridge.add_accessory(get_accessory(driver, name='FakeJalousie 2'))
    return bridge


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=get_bridge(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()
