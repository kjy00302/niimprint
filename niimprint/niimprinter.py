import time
import math
from . import printencoder

from .printerclient import PrinterClient, InfoEnum

from .util import render_text

from .logger import logger


# Pixel = Millimeter * ( Resolution(DPI) / 25.4 )
# Niimbot D11 has 203 DPI (https://www.niimbotlabel.com/products/niimbot-d11-label-maker)
def mm_to_px(x):
    return math.ceil(x / 25.4 * 203)


class Niimprinter:
    def __init__(self, address):
        self._client = PrinterClient(address)

    def get_info(self):
        """Get printer information"""
        data = {
            "SW": self._client.get_info(InfoEnum.SOFTVERSION),
            "HW": self._client.get_info(InfoEnum.HARDVERSION),
            "S/N": self._client.get_info(InfoEnum.DEVICESERIAL),
        }

        return data

    def get_rfid(self):
        """Get RFID information"""
        return self._client.get_rfid()

    def heartbeat(self):
        """Send heartbeat"""
        return self._client.heartbeat()

    def print_label(self, text, quantity=1, label_width_mm=12, label_length_mm=40):
        """Print label with specified text"""

        label_width_px = mm_to_px(label_width_mm)
        label_length_px = mm_to_px(label_length_mm)

        image = render_text(text, size=(label_length_px, label_width_px))

        logger.debug("Label size: %dpx x %dpx", image.width, image.height)

        # ensure that label width and length are within printer's supported range
        assert image.width == label_width_px and image.height <= label_length_px

        self._client.set_label_type(1)  # 1~3
        self._client.set_label_density(2)  # 1~3
        self._client.start_print()
        self._client.allow_print_clear()
        self._client.start_page_print()
        self._client.set_dimension(image.height, image.width)
        self._client.set_quantity(quantity)
        for pkt in printencoder.naive_encoder(image):
            self._client._send(pkt)

        self._client.end_page_print()

        while (a := self._client.get_print_status())["page"] != quantity:
            logger.debug("Print status: %s", a)
            time.sleep(0.1)
        self._client.end_print()
