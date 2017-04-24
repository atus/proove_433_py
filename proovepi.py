"""
Inspired by https://github.com/milaq/rpi-rf/blob/master/rpi_rf/rpi_rf.py
Protocol by https://github.com/JoakimWesslen/Tx433
"""

import logging
import time

from RPi import GPIO

_LOGGER = logging.getLogger(__name__)

class Proove:
    """Control your proove device"""

    gpio = 4
    tx_repeat = 4

    tOneHigh = 250 #275
    tOneLow = 250 #170

    tZeroHigh = 250
    tZeroLow = 1250

    tSyncHigh = 250
    tSyncLow = 2500

    tPauseHigh = 250
    tPauseLow = 10000

    """
        Packet structure:
        Bit nbr:  Name:
        01-52     Transmitter code. 26 bits, sent as 52 (every other bit is the inverse of previous)
        53-54     Group On(01), Off(10)
        55-56     On(01), Off(10) (or Dim(11)?)
        57-60     Channel. 1=1010, 2=1001, 3=0110, 4=0101
        61-64     Switch.  1=1010, 2=1001, 3=0110, 4=0101
        (65-73    Dimmer value, 16 steps. (optional))

        #                10        20        30        40        50           60
        #       1234567890123456789012345678901234567890123456789012 34 56 7890 1234
        ----------------------------------------------------------------------------
        #1 On:  1010100101101001010101100101011001010101010101010110 10 01 0101 0101
        #1 Off: 1010100101101001010101100101011001010101010101010110 10 10 0101 0101
        #2 On:  1010100101101001010101100101011001010101010101010110 10 01 0101 0110
        #2 Off: 1010100101101001010101100101011001010101010101010110 10 10 0101 0110
        #3 On:  1010100101101001010101100101011001010101010101010110 10 01 0101 1001
        #3 Off: 1010100101101001010101100101011001010101010101010110 10 10 0101 1001
        Gr On:  1010100101101001010101100101011001010101010101010110 01 01 0101 0101
        Gr Off: 1010100101101001010101100101011001010101010101010110 01 10 0101 0101
    """

    _transmitter_id = "11100110000100010000000001"
    _on = "0"
    _off = "1"
    _channel = ["00", "01", "10", "11"]
    _switch = ["00", "01", "10", "11"]
    _dim = [ #16 levels
        "0000"
        "0001",
        "0010",
        "0011",
        "0100",
        "0101",
        "0110",
        "0111",
        "1000",
        "1001",
        "1010",
        "1011",
        "1100",
        "1101",
        "1110",
        "1111"
    ]

    def __init__(self, gpio):
        self.gpio = gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.OUT)

    def cleanup(self):
        _LOGGER.debug("Cleanup")
        GPIO.cleanup()

    def channel_on(self, switch_id):
        self._trigger(self._off, self._on, self._switch[switch_id])

    def channel_off(self, switch_id):
        self._trigger(self._off, self._off, self._switch[switch_id])

    def group_on(self):
        self._trigger(self._on, self._on, self._switch[0])

    def group_off(self):
        self._trigger(self._on, self._off, self._switch[0])

    def _trigger(self, group_state, state_value, switch_id):
        data = self._transmitter_id
        data += group_state
        data += state_value
        data += self._channel[0]
        data += switch_id
        packet = self.encode(data)
        self.tx_packets(packet)

    def encode(self, code):
        data = ""
        for byte in range(0, len(code)):
            data += code[byte]
            if code[byte] == '0':
                data += '1'
            else:
                data += '0'
        return data

    def decode(self, packet):
        data = ""
        for byte in range(0, len(packet)/2):
            data += packet[byte*2]
        return data

    def tx_packets(self, packet):
        data = self.decode(packet)
        _LOGGER.debug("Data: " + data)
        for _ in range(0, self.tx_repeat):
            _LOGGER.debug("Repeat: " + str(_))
            self.tx_packet(packet)

    def tx_packet(self, packet):
        _LOGGER.debug("TX packet: " + str(packet))
        self.tx_sync()
        for byte in range(0, len(packet)):
            if packet[byte] == '0':
                self.tx_l0()
            else:
                self.tx_l1()
        self.tx_pause()

    def tx_sync(self):
        self.tx_waveform(self.tSyncHigh, self.tSyncLow)

    def tx_l0(self):
        self.tx_waveform(self.tZeroHigh, self.tZeroLow)

    def tx_l1(self):
        self.tx_waveform(self.tOneHigh, self.tOneLow)

    def tx_pause(self):
        self.tx_waveform(self.tPauseHigh, self.tPauseLow)

    def tx_waveform(self, high_pulse, low_pulse):
        GPIO.output(self.gpio, GPIO.HIGH)
        time.sleep(high_pulse / 1000000.0)
        GPIO.output(self.gpio, GPIO.LOW)
        time.sleep(low_pulse / 1000000.0)


