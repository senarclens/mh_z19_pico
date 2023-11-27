"""
Serial port output (UART) module for the MH_Z19 sensor family.
"""

from machine import UART, Pin
from utime import sleep
import struct

UART_TX_PIN = 0
UART_RX_PIN = 1
UART_ID = 0
BAUD_RATE = 9600  # according to manual
DATA_BIT = 8  # 8 bytes according to manual
STOP_BIT = 1  # 1 byte according to manual
PARITY_BIT = None  # null according to manual

class MH_Z19:
    """
    Communicate with the MH_Z19 sensor from the Raspberry Pi Pico.
    
    This rudimentary implementation is my very first attempt of working with
    uart in micropython. Use with caution. There is no warranty.
    
    The MH_Z19B sensor's datasheet can be found at
    https://www.winsen-sensor.com/d/files/infrared-gas-sensor/mh-z19b-co2-ver1_0.pdf
    
    The MH_Z19C sensor's datasheet can be found at
    https://www.winsen-sensor.com/d/files/infrared-gas-sensor/mh-z19c-pins-type-co2-manual-ver1_0.pdf
    """
    RETRY_COUNT = 5

    def __init__(self, tx_pin: Pin, rx_pin: Pin, uart_id=0):
        self.sensor = UART(uart_id, baudrate=BAUD_RATE, tx=tx_pin, rx=rx_pin,
                           bits=DATA_BIT, parity=PARITY_BIT, stop=STOP_BIT)

    def read_co2(self):
        """
        Read the CO2 value (command 0x86, checksum 0x79).
        """
        for _retry in range(self.RETRY_COUNT):
            result = self.sensor.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
            s = self.sensor.read(result)

            if (s and len(s) >= 4 and s[0] == 0xff and s[1] == 0x86 and
                ord(self.checksum(s[1:-1])) == s[-1]):
                return s[2]*256 + s[3]
            sleep(0.1)
        return

    def read_all(self):
        for _retry in range(self.RETRY_COUNT):
            result = self.sensor.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
            s = self.sensor.read(result)

            if (s and len(s) >= 9 and s[0] == 0xff and s[1] == 0x86 and
                ord(self.checksum(s[1:-1])) == s[-1]):
                return {'co2': s[2]*256 + s[3],
                        'temperature': s[4] - 40,
                        'TT': s[4],
                        'SS': s[5],
                        'UhUl': s[6]*256 + s[7]}
            sleep(0.1)
        return {}
    
    def calibrate_zero(self) -> None:
        """
        Perform zero point calibration (0x87).
        
        Zero point is 400ppm, please make sure the sensor had been worked
        under 400ppm for at least 20 minutes.
        """
        request = b"\xff\x01\x87\x00\x00\x00\x00\x00\x78"
        result = self.sensor.write(request)

    def calibrate_span(self, span) -> None:
        """
        Perform span calibration (0x88).
        
        Note: Please do zero calibration (`calibrate_zero`) before span
        calibration.
        Please make sure the sensor worked under the given level of co2 for
        at least 20 minutes.
        Use at least 1000ppm as span, ideally 2000ppm.
        """
        b3 = span // 256  # high byte
        byte3 = struct.pack('B', b3)
        b4 = span % 256  # low byte
        byte4 = struct.pack('B', b4)
        c = checksum([0x01, 0x88, b3, b4])
        request = b"\xff\x01\x88" + byte3 + byte4 + b"\x00\x00\x00" + c
        result = self.sensor.write(request)

    def enable_self_calibration(self) -> None:
        """
        Enable automatic baseline correction (command 0x79).
        
        This function is usually suitable for indoor air quality monitor
        such as offices, schools and homes.
        The sensor factory default is to enable the automatic zero calibration
        function.
        Enable with 0xa0.
        """
        self.sensor.write(b"\xff\x01\x79\xa0\x00\x00\x00\x00\xe6")
        
    def disable_self_calibration(self) -> None:
        """
        Disable automatic baseline correction (command 0x79).
        
        This function is usually suitable for greenhouse, farm and
        refrigerators.
        Disable with 0x00.
        """
        self.sensor.write(b"\xff\x01\x79\x00\x00\x00\x00\x00\x86")

    def checksum(self, array) -> bytes:
        """
        Return the checksum byte.
        """
        csum = sum(array) % 0x100
        if csum == 0:
            return struct.pack('B', 0)
        else:
            return struct.pack('B', 0xff - csum + 1)


if __name__ == "__main__":
    sensor = MH_Z19(Pin(UART_TX_PIN), Pin(UART_RX_PIN), UART_ID)
    print(sensor.read_co2())
