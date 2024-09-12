# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT
"""
`m5stack_pbhub`
================================================================================

CircuitPython driver for M5Stack PbHub


* Author(s): Dario Cammi

Implementation Notes
--------------------

**Hardware:**

* `M5Stack PbHub <https://docs.m5stack.com/en/unit/pbhub_1.1>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

# imports

__version__ = "1.0.0+auto.0"
__repo__ = "https://github.com/CDarius/CircuitPython_M5Stack_PbHub.git"

from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

try:
    from typing import Annotated, Tuple

    # These are only needed for typing
    import busio  # pylint: disable=unused-import
except ImportError:
    pass

_CHANNEL_BASE_REG = [0x40, 0x50, 0x60, 0x70, 0x80, 0xA0]
_MAX_NUM_OF_LED = const(74)


class PbHub:
    """CircuitPython driver for M5Stack PbHub

    :param ~busio.I2C i2c: The I2C bus PbHub is connected to
    :param int device_address: The I2C bus addres. Default to 0x61

    **Quickstart: Importing and using the hub**

    Here is an example of using the :py:class:`PbHub` class.
    First you will need to import the libraries, get an I2C bus and create an hub instance

    .. code-block:: python

        import board
        import m5stack_pbhub

        i2c = board.I2C()
        hub = m5stack_pbhub.PbHub(i2c)

    Now you can create an I/O on one of PbHub channel. For example let create a digital input

    .. code-block:: python

        din = m5stack_pbhub.PbHubDigitalInput(hub, channel = 1, io = 1)
        input_value = din.value

    """

    def __init__(self, i2c: busio.I2C, addr: int = 0x61) -> None:
        self.i2c_device = I2CDevice(i2c, addr)

    @property
    def firmware_version(self) -> int:
        """Return the hub firmware version"""
        buf = bytearray(1)
        buf[0] = 0xFE
        with self.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(buf)

        return buf[0]


class _PbHubChannel:
    """Module internal class that represent a PbHub channel

    :param PbHub pbHub: PhHub to use
    :param int channel: Channel of the hub. Range 0 to 5
    :param int io: Input pin of the channel. Range 0 to 1
    """

    def __init__(self, pbHub: PbHub, channel: int, io: int) -> None:
        self._pbhub = pbHub
        self._channel = channel
        self._io = io
        self._set_reg()

    def _set_reg(self):
        pass

    @property
    def channel(self) -> int:
        """Hub channel"""
        return self._channel

    @channel.setter
    def channel(self, value: int) -> int:
        if not isinstance(value, int):
            raise ValueError("Channel must be an integer number")
        if value < 0 or value > 5:
            raise ValueError("Channel must be an integer number between 0 and 5")
        self._channel = value
        self._set_reg()

    @property
    def io(self) -> int:
        """Hub IO pin"""
        return self._io

    @io.setter
    def io(self, value) -> int:
        if not isinstance(value, int):
            raise ValueError("IO must be an integer number")
        if value < 0 or value > 1:
            raise ValueError("IO must be an integer number between 0 and 1")
        self._io = value
        self._set_reg()


class PbHubDigitalInput(_PbHubChannel):
    """PbHub digital input

    :param PbHub pbHub: PhHub to use
    :param int channel: Channel of the hub. Range 0 to 5
    :param int io: Input pin of the channel. Range 0 to 1

    Here is an example of reading a digital input

    .. code-block:: python

        import board
        import m5stack_pbhub

        i2c = board.I2C()
        hub = m5stack_pbhub.PbHub(i2c)
        din = m5stack_pbhub.PbHubDigitalInput(hub, channel = 0, io = 0)
        print(din.value)

    """

    def __init__(self, pbHub: PbHub, channel: int, io: int) -> None:
        super().__init__(pbHub, channel, io)

    def _set_reg(self):
        self._reg_num = _CHANNEL_BASE_REG[self._channel] | (0x04 if self._io == 0 else 0x05)

    @property
    def value(self) -> bool:
        """Return the digital input value"""
        buf = bytearray(1)
        buf[0] = self._reg_num
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(buf)

        return buf[0] == 1


class PbHubDigitalOutput(_PbHubChannel):
    """PbHub digital output

    :param PbHub pbHub: PhHub to use
    :param int channel: Channel of the hub. Range 0 to 5
    :param int io: Input pin of the channel. Range 0 to 1

    Here is an example of driving a digital output

    .. code-block:: python

        import board
        import m5stack_pbhub

        i2c = board.I2C()
        hub = m5stack_pbhub.PbHub(i2c)
        dout = m5stack_pbhub.PbHubDigitalOutput(hub, channel = 0, io = 0)

        dout.value = 1 # set the output
        print(dout.value) # read the output value

    """

    def __init__(self, pbHub: PbHub, channel: int, io: int) -> None:
        super().__init__(pbHub, channel, io)

    def _set_reg(self):
        self._reg_num = _CHANNEL_BASE_REG[self._channel] | (0x00 if self._io == 0 else 0x01)

    @property
    def value(self) -> bool:
        """Digital output value"""
        buf = bytearray(1)
        buf[0] = self._reg_num
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(buf)

        return buf[0] == 1

    @value.setter
    def value(self, value: bool) -> None:
        buf = bytearray(2)
        with self._pbhub.i2c_device as i2c:
            buf[0] = self._reg_num
            buf[1] = 0x01 if value else 0x00
            i2c.write(buf)


class PbHubAnalogInput(_PbHubChannel):
    """PbHub analog input

    :param PbHub pbHub: PhHub to use
    :param int channel: Channel of the hub. Range 0 to 5

    Analog inputs are always on IO pin 0. The resolution is 12 bit (0 - 4095)

    Here is an example of reading an analog input

    .. code-block:: python

        import board
        import m5stack_pbhub

        i2c = board.I2C()
        hub = m5stack_pbhub.PbHub(i2c)
        ain = m5stack_pbhub.PbHubAnalogInput(hub, channel = 0)
        print(ain.value)

    """

    def __init__(self, pbHub: PbHub, channel: int) -> None:
        super().__init__(pbHub, channel, 0)

    def _set_reg(self):
        self._reg_num = _CHANNEL_BASE_REG[self._channel] | 0x06

    @property
    def value(self) -> int:
        """Input value. Range 0 to 4095"""
        buf = bytearray(1)
        buf[0] = self._reg_num
        bufRet = bytearray(2)
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(bufRet)

        return (bufRet[1] << 8) | bufRet[0]


class PbHubPwmOutput(_PbHubChannel):
    """PbHub PWM output

    :param PbHub pbHub: PhHub to use
    :param int channel: Channel of the hub. Range 0 to 5
    :param int io: Input pin of the channel. Range 0 to 1

    The output resolution is 8 bit (0 - 255)

    Here is an example of driving PWM output

    .. code-block:: python

        import board
        import m5stack_pbhub

        i2c = board.I2C()
        hub = m5stack_pbhub.PbHub(i2c)
        pwm = m5stack_pbhub.PbHubPwmOutput(hub, channel = 0, io = 0)
        pwm.value = 127

    """

    def __init__(self, pbHub: PbHub, channel: int, io: int) -> None:
        super().__init__(pbHub, channel, io)

    def _set_reg(self):
        self._reg_num = _CHANNEL_BASE_REG[self._channel] | (0x02 if self._io == 0 else 0x03)

    @property
    def value(self) -> int:
        """PWM output value"""
        buf = bytearray(1)
        buf[0] = self._reg_num
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(buf)

        return buf[0]

    @value.setter
    def value(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Output value must be an integer")
        if value < 0 or value > 255:
            raise ValueError("Output value must be between 0 and 255")
        buf = bytearray(2)
        with self._pbhub.i2c_device as i2c:
            buf[0] = self._reg_num
            buf[1] = value & 0xFF
            i2c.write(buf)


class PbHubServo(_PbHubChannel):
    """PbHub output to drive RC servo

    :param PbHub pbHub: PhHub to use
    :param int channel: Channel of the hub. Range 0 to 5
    :param int io: Input pin of the channel. Range 0 to 1

    Here is an example of driving an RC servo

    .. code-block:: python

        import board
        import m5stack_pbhub

        i2c = board.I2C()
        hub = m5stack_pbhub.PbHub(i2c)
        servo = m5stack_pbhub.PbHubServo(hub, channel = 0, io = 0)
        servo.angle = 45 # set servo angle in degrees
        servo.pulse = 1500 # set servo angle as pulse with. 1500µs is equivalent to 90 degrees

    """

    def __init__(self, pbHub: PbHub, channel: int, io: int) -> None:
        super().__init__(pbHub, channel, io)

    def _set_reg(self):
        self._reg_num_angle = _CHANNEL_BASE_REG[self._channel] | (0x0C if self._io == 0 else 0x0D)
        self._reg_num_pulse = _CHANNEL_BASE_REG[self._channel] | (0x0E if self._io == 0 else 0x0F)

    @property
    def angle(self) -> int:
        """RC servo angle in degree. Range 0 to 180"""
        buf = bytearray(1)
        buf[0] = self._reg_num_angle
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(buf)

        return buf[0]

    @angle.setter
    def angle(self, angle: int) -> None:
        if not isinstance(angle, int):
            raise ValueError("Servo angle must be an integer")
        if angle < 0 or angle > 180:
            raise ValueError("Servo angle must be between 0 and 180 degrees")
        buf = bytearray(2)
        with self._pbhub.i2c_device as i2c:
            buf[0] = self._reg_num_angle
            buf[1] = angle
            i2c.write(buf)

    @property
    def pulse(self) -> int:
        """RC servo angle in pulse width

        Pulse width is expressed in microseconds and the frequency is 50 Hz
        Allowed range: 500 to 2500
        """
        buf = bytearray(1)
        buf[0] = self._reg_num_pulse
        bufRet = bytearray(2)
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(bufRet)

        return (bufRet[1] << 8) | bufRet[0]

    @pulse.setter
    def pulse(self, pulse_width: int) -> None:
        if not isinstance(pulse_width, int):
            raise ValueError("Servo pusle width must be an integer")
        if pulse_width < 500 or pulse_width > 2500:
            raise ValueError("Servo pulse width must be between 500 and 2500 µs")
        buf = bytearray(3)
        with self._pbhub.i2c_device as i2c:
            buf[0] = self._reg_num_pulse
            buf[1] = pulse_width & 0xFF
            buf[2] = (pulse_width & 0xFF00) >> 8
            i2c.write(buf)


class NeoPixels:
    """Drive an array of NeoPixels connect to the PbHub

    :param pbHub: Instance of PbHub where the leds are connected
    :param channel: Hub channel where the leds are connected
    :param number_of_leds: Number of leds connected to the channel
    :param brightness: Leds brightness

    Here is an example of driving a strip with 10 leds connected on channel 0:

    .. code-block:: python

        import time
        import board
        import m5stack_pbhub

        i2c = board.I2C()
        hub = m5stack_pbhub.PbHub(i2c)
        strip = m5stack_pbhub.NeoPixels(hub, 0, 10)

        strip[0] = 0xFF0000 # Set the color a single led
        strip[3] = 0xFF00FF # Set the color a single led
        time.sleep(1)
        strip[1:3] = 0x00FFFF # Set the color of two leds
        time.sleep(1)
        strip.fill(0xFFFF00) # Set the color of the wall strip
        time.sleep(1)

    """

    def __init__(
        self, pbHub: PbHub, channel: int, number_of_leds: int, brightness: float = 0.5
    ) -> None:
        if not isinstance(channel, int):
            raise ValueError("Channel must be an integer number")
        if channel < 0 or channel > 5:
            raise ValueError("Channel must be an integer number between 0 and 5")

        self._pbhub = pbHub
        self._channel = channel
        self._set_reg()
        self.number_of_leds = number_of_leds
        self.brightness = brightness

    def _set_reg(self):
        self._reg_num_num_leds = _CHANNEL_BASE_REG[self._channel] | 0x08
        self._reg_num_brightness = _CHANNEL_BASE_REG[self._channel] | 0x0B
        self._reg_num_one_led_color = _CHANNEL_BASE_REG[self._channel] | 0x09
        self._reg_num_range_led_color = _CHANNEL_BASE_REG[self._channel] | 0x0A

    @property
    def channel(self) -> int:
        """Channel where the leds are connected"""
        return self._channel

    @property
    def number_of_leds(self) -> int:
        """Number of leds connected to PbHub"""
        buf = bytearray(1)
        buf[0] = self._reg_num_num_leds
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(buf)

        return buf[0]

    @number_of_leds.setter
    def number_of_leds(self, number: int) -> None:
        if not isinstance(number, int):
            raise ValueError("Number of pixels must be an integer")
        if number < 0 or number > _MAX_NUM_OF_LED:
            raise ValueError(f"Number of pixels must be between 0 and {_MAX_NUM_OF_LED}")
        buf = bytearray(3)
        with self._pbhub.i2c_device as i2c:
            buf[0] = self._reg_num_num_leds
            buf[1] = number & 0xFF
            buf[2] = (number >> 8) & 0xFF
            i2c.write(buf)

    @property
    def brightness(self) -> float:
        """Leds brightness. Range 0 to 1

        A change in the brightness take effect only on the subsequent leds color write
        """
        buf = bytearray(1)
        buf[0] = self._reg_num_num_leds
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)
            i2c.readinto(buf)

        return round(buf[0] / 255.0, 2)

    @brightness.setter
    def brightness(self, value: float) -> None:
        if not isinstance(value, float) and not isinstance(value, int):
            raise ValueError("Brightness must be a number")
        if value < 0 or value > 1.0:
            raise ValueError("Brightness must be between 0.0 and 1.0")
        buf = bytearray(2)
        buf[0] = self._reg_num_brightness
        buf[1] = round(255 * value)
        with self._pbhub.i2c_device as i2c:
            i2c.write(buf)

    def __setitem__(self, index: int, color: int | Annotated[list[int], 3]) -> None:
        """Set the color of one led or more leds

        :param index: Single led index or a slice of leds indexes
        :param color: Color to apply at the leds
        """
        if isinstance(index, slice):
            start = index.start
            stop = index.stop
            if start < 0 or start > _MAX_NUM_OF_LED:
                raise ValueError(f"Start index must be and integet 0 and {_MAX_NUM_OF_LED}")
            if stop < 0 or stop > _MAX_NUM_OF_LED:
                raise ValueError(f"Stop index must be and integet 0 and {_MAX_NUM_OF_LED}")
            if stop < start:
                raise ValueError(f"Stop index must be greater then start index")

            count = stop - start
            if count == 0:
                return

            buf = bytearray(8)
            buf[0] = self._reg_num_range_led_color
            buf[1] = start & 0xFF
            buf[2] = (start >> 8) & 0xFF
            buf[3] = count & 0xFF
            buf[4] = (count >> 8) & 0xFF
            if isinstance(color, int):
                buf[5] = (color >> 16) & 0xFF
                buf[6] = (color >> 8) & 0xFF
                buf[7] = color & 0xFF
            else:
                buf[5] = color[0] & 0xFF
                buf[6] = color[1] & 0xFF
                buf[7] = color[2] & 0xFF
            with self._pbhub.i2c_device as i2c:
                i2c.write(buf)
        else:
            if not isinstance(index, int):
                raise ValueError("Index must be an integer")
            if index < 0 or index > _MAX_NUM_OF_LED:
                raise ValueError("Index must be and integet 0 and 74")

            buf = bytearray(6)
            buf[0] = self._reg_num_one_led_color
            buf[1] = index & 0xFF
            buf[2] = (index >> 8) & 0xFF
            if isinstance(color, int):
                buf[3] = (color >> 16) & 0xFF
                buf[4] = (color >> 8) & 0xFF
                buf[5] = color & 0xFF
            else:
                buf[3] = color[0] & 0xFF
                buf[4] = color[1] & 0xFF
                buf[5] = color[2] & 0xFF
            with self._pbhub.i2c_device as i2c:
                i2c.write(buf)

    def fill(self, color: int | Annotated[list[int], 3]) -> None:
        """Fill all the leds with the same color

        :param color: Color to apply at the leds
        """
        self[0 : self.number_of_leds] = color
