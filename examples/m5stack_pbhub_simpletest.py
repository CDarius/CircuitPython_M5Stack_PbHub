# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: Unlicense
"""
Configure channel 1 io pin 1 as a digital input and read the value
"""

import board

import m5stack_pbhub

hub = m5stack_pbhub.PbHub(board.I2C())
din = m5stack_pbhub.PbHubDigitalInput(hub, channel=1, io=1)
print(f"Digitial input value: {din.value}")
