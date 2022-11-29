"""Setup and start an eNet Accessory."""
import logging
import signal
import os
from enet import EnetClient

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_WINDOW_COVERING

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")


class Jalousie(Accessory):
    """"""

    category = CATEGORY_WINDOW_COVERING

    def __init__(self, driver, channel, name):
        super().__init__(driver, name)
        self.channel = channel

        serv_state = self.add_preload_service('WindowCovering')
        # ['CurrentPosition', 'TargetPosition', 'PositionState']
        self.char_current_position = serv_state.configure_char(
            'CurrentPosition'
        )
        self.char_target_position = serv_state.configure_char('TargetPosition')
        self.char_target_position.setter_callback = (
            self.target_position_changed
        )
        self.char_position_state = serv_state.configure_char('PositionState')

    def target_position_changed(self, value):
        # set_target_position_on_enet(100-value)
        self.channel.set_value(100-value)
        self.char_current_position.set_value(value)
        print('Target position changed to: ', 100-value)

    @Accessory.run_at_interval(60)
    async def run(self):
        value = 100 - self.channel.get_value()
        self.char_target_position.set_value(value)
        self.char_current_position.set_value(value)


def get_accessory(driver, channel, name):
    """Call this method to get a standalone Accessory."""
    return Jalousie(driver, channel, name)


def get_bridge(driver, client):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(driver, 'Jalousien')

    for device in client.get_devices():
        location = device.location.split(':')[-1]
        if not device.channels:
            continue
        channel = device.channels[0]
        type_ = channel.name
        if type_ == 'Schalten':
            # XXX Make a button
            continue
        bridge.add_accessory(
            get_accessory(driver, channel, name=f'{type_} {location}')
        )
    return bridge


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.

client = EnetClient(
    'http://10.0.1.12', 'admin', os.environ.get('ENET_PASSWORD')
)
client.simple_login()
driver.add_accessory(accessory=get_bridge(driver, client))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()
