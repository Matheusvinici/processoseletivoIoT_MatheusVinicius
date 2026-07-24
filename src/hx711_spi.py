from machine import SPI, Pin
import time

class HX711:
    def __init__(self, sck_pin, dout_pin, spi_id=2, gain=128):
        self.clock = Pin(sck_pin, Pin.OUT, value=0)
        self.data = Pin(dout_pin, Pin.IN)
        self.spi = SPI(spi_id, baudrate=1000000, polarity=0, phase=0)

        clock_25 = b'\xaa\xaa\xaa\xaa\xaa\xaa\x80'
        clock_26 = b'\xaa\xaa\xaa\xaa\xaa\xaa\xa0'
        clock_27 = b'\xaa\xaa\xaa\xaa\xaa\xaa\xa8'
        self.clock_table = [None, clock_25, clock_26, clock_27]
        self.gain_table = {128: 1, 32: 2, 64: 3}
        self.lookup = (b'\x00\x01\x00\x00\x02\x03\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x04\x05\x00\x00\x06\x07\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x08\x09\x00\x00\x0a\x0b\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x0d\x00\x00'
                       b'\x0e\x0f')
        self.in_data = bytearray(7)
        self.set_gain(gain)

    def set_gain(self, gain):
        self.MODE = self.gain_table.get(gain, 1)
        self.read()

    def read(self):
        if self.data() == 1:
            return None
        self.spi.write_readinto(self.clock_table[self.MODE], self.in_data)
        result = 0
        for i in range(6):
            result = (result << 4) + self.lookup[self.in_data[i] & 0x55]
        return result - ((result & 0x800000) << 1)