# Copyright 2022-2025 NXP
#
# NXP Proprietary. This software is owned or controlled by NXP and may only be
# used strictly in accordance with the applicable license terms. By expressly
# accepting such terms or by downloading, installing, activating and/or otherwise
# using the software, you are agreeing that you have read, and that you agree to
# comply with and are bound by, such license terms. If you do not agree to be
# bound by the applicable license terms, then you may not retain, install,
# activate or otherwise use the software.

class Averaging:
    def __init__(self):
        self.last_value = 0
        self.last_window = []

def adaptative_exponential_moving_avg(val, val_avg):
    AEMA = 20
    alpha = 2/(int(AEMA)+1)

    val_avg.last_window.insert(0, val)
    if len(val_avg.last_window) != 1:
        while (len(val_avg.last_window) > int(AEMA)): val_avg.last_window.pop()
        val = (alpha*val) + (1 - alpha) * val_avg.last_value
    val_avg.last_value = val
    return val