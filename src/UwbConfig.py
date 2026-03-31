# Copyright 2022-2025 NXP
#
# NXP Proprietary. This software is owned or controlled by NXP and may only be
# used strictly in accordance with the applicable license terms. By expressly
# accepting such terms or by downloading, installing, activating and/or otherwise
# using the software, you are agreeing that you have read, and that you agree to
# comply with and are bound by, such license terms. If you do not agree to be
# bound by the applicable license terms, then you may not retain, install,
# activate or otherwise use the software.

import src.UwbConfig_SR250ARD as Evk

SessionNb = 0
RadarSessionId = 0
RangingSessionId = 0
Multitarget = False

CORE_DEVICE_INIT_CMD = [0x2E,0x00,0x00,0x02,0x00,0x00]
CORE_DEVICE_RESET_CMD = [0x20,0x00,0x00,0x01,0x00]
CORE_GET_DEV_INFO = [0x20,0x02,0x00,0x00]
CORE_SET_CONFIG_CMD_LOW_POWER_MODE = [0x20,0x04,0x00,0x04,0x01,0x01,0x01,0x01]

RADAR_SESSION_INIT_CMD = [0x21,0x00,0x00,0x05,0x88,0x77,0x66,0x55,0xF0]
RADAR_SESSION_SET_APP_CONFIG_CMD = [0x21,0x03,0x00,0x0B,0x00,0x00,0x00,0xF0,0x02,
                                    0x04,0x01,0x09,     # CHANNEL NUMBER
                                    0x14,0x01,0x1A      # PREAMBLE_CODE_INDEX
]
RADAR_SET_VENDOR_APP_CONFIG_CMD = [0x2F,0x00,0x00,0x1E,0x00,0x00,0x00,0xF0,0x06,
                                   0x7F,0x01,0x01,
                                   0xA0,0x01,0x01,                                  # RADAR_MODE
                                   0xA8,0x07,0x03,0x76,0x02,0x76,0x02,0x76,0x02,    # RADAR_CIR_START_OFFSET
                                   0xAD,0x01,0x01,                                  # RADAR_PERFORMANCE
                                   0xAE,0x01,0x41,                                  # RADAR_PULSE_SHAPE
                                   0xB2,0x02,0xCD,0x0C                              # RADAR_DRIFT_COMPENSATION
]
RADAR_OCPD_CMD = [0x2F,0x00,0x00,0x1C,0x00,0x00,0x00,0xF0,0x02,
                  0xAA,0x0C,                # RADAR_PRESENCE_DET_CFG
                      0x01,                     # Mode
                      0x00,                     # Raw + report frequency 
                      0x30,                     # snr: 0x34-->52/16(Q4) = 3.25
                      0x00,                     # GPIO
                      0x1E,0x00,                # Min distance
                      0x20,0x03,                # Max distance
                      0x40,0x06,                # Hold delay
                      0xa6,                     # Min angle
                      0x5a,                     # Max angle
                  0xA9,0x07,                # RADAR_RFRI
                      0x32,0x00,0x00,0x00,      # Ranging interval
                      0x70,0x17,                # Slot duration
                      0x01,                     # Slots per RR
]
RADAR_START_CMD = [0x22,0x00,0x00,0x04,0x00,0x00,0x00,0xF0]
RADAR_STOP_CMD = [0x22,0x01,0x00,0x04,0x00,0x00,0x00,0xF0]

def getConfigCommands():
    GenericCommands = [
        CORE_DEVICE_INIT_CMD,
        CORE_DEVICE_RESET_CMD,
        CORE_GET_DEV_INFO,
        CORE_SET_CONFIG_CMD_LOW_POWER_MODE
    ]
    return GenericCommands + Evk.EvkCommands

def getRadarCommands(key):
    global SessionNb, RadarSessionId
    if key == "INIT":
        SessionNb +=1
        RadarSessionId = SessionNb
        return RADAR_SESSION_INIT_CMD
    elif key == "START":
        RADAR_SET_VENDOR_APP_CONFIG_EVK_CMD = [0x2F,0x00,0x00,4+len(Evk.RADAR_EVK_ANT_CONFIG),0x00,0x00,0x00,0xF0] + Evk.RADAR_EVK_ANT_CONFIG
        RadarSessionCommands = [
            RADAR_SESSION_SET_APP_CONFIG_CMD,
            RADAR_SET_VENDOR_APP_CONFIG_CMD,
            RADAR_SET_VENDOR_APP_CONFIG_EVK_CMD,
            RADAR_OCPD_CMD,
            RADAR_START_CMD
        ]
        for cmd in RadarSessionCommands: cmd[4] = RadarSessionId
        return RadarSessionCommands
    elif key == "OCPD":
        RADAR_OCPD_CMD[4] = RadarSessionId
        return RADAR_OCPD_CMD
    elif key == "STOP":
        RADAR_STOP_CMD[4] = RadarSessionId
        return RADAR_STOP_CMD

def setOCPD(angle=False, magnitude=False, multitarget=False, raw=False, freq=0, sensitivity=0x3C, maxDistance=800, maxFoV=90, hold=1600, powerMode='Default'):
    global RADAR_OCPD_CMD, Multitarget
    Multitarget = multitarget
    RADAR_OCPD_CMD[11] = 0x01 | (0x02 if not angle == False else 0) \
                              | (0x04 if not multitarget == False else 0) \
                              | (0x10 if not magnitude == False else 0)
    RADAR_OCPD_CMD[12] = (0x01 if not raw == False else 0) | (0x02 if freq == 50 else 0x04 if freq == 400 else 0x06 if freq == 1600 else 0)
    RADAR_OCPD_CMD[13] = sensitivity
    RADAR_OCPD_CMD[17] = maxDistance & 0xFF
    RADAR_OCPD_CMD[18] = maxDistance >> 8
    RADAR_OCPD_CMD[19] = hold & 0xFF
    RADAR_OCPD_CMD[20] = hold >> 8
    RADAR_OCPD_CMD[21] = -maxFoV & 0xFF
    RADAR_OCPD_CMD[22] = maxFoV
    if powerMode == 'LowPower':
        # Low power mode: 160ms
        RADAR_OCPD_CMD[25] = 0xA0
        RADAR_OCPD_CMD[26] = 0x00
        RADAR_OCPD_CMD[27] = 0x00
        RADAR_OCPD_CMD[28] = 0x00
        RADAR_OCPD_CMD[29] = 0x70
        RADAR_OCPD_CMD[30] = 0x17
        RADAR_OCPD_CMD[31] = 0x01
    else:
        # Default: 50ms
        RADAR_OCPD_CMD[25] = 0x32
        RADAR_OCPD_CMD[26] = 0x00
        RADAR_OCPD_CMD[27] = 0x00
        RADAR_OCPD_CMD[28] = 0x00
        RADAR_OCPD_CMD[29] = 0x70
        RADAR_OCPD_CMD[30] = 0x17
        RADAR_OCPD_CMD[31] = 0x01

def AngleSignAdaptation(angle):
    if Evk.InvertAoASign == True: return -angle
    else: return angle
