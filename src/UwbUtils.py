# Copyright 2022-2025 NXP
#
# NXP Proprietary. This software is owned or controlled by NXP and may only be
# used strictly in accordance with the applicable license terms. By expressly
# accepting such terms or by downloading, installing, activating and/or otherwise
# using the software, you are agreeing that you have read, and that you agree to
# comply with and are bound by, such license terms. If you do not agree to be
# bound by the applicable license terms, then you may not retain, install,
# activate or otherwise use the software.

from ctypes import c_short
import math
import struct
import src.UwbConfig as UwbConfig
import src.Averaging as Avg

class Presence:
    status = 0
    id = 0
    distance = 0
    angle = 0
    previous_angle = 127
    snr = 0
    x = 0
    y = 0
    x_avg = Avg.Averaging()
    y_avg = Avg.Averaging()

detected_presence = Presence()

previous_angle = 127

def clean_presence(presence):
    presence.status = 0
    presence.id = 0
    presence.distance = 0
    presence.angle = 0
    presence.previous_angle = 127
    presence.snr = 0
    presence.x = 0
    presence.y = 0
    presence.x_avg.last_window.clear()
    presence.y_avg.last_window.clear()


def extract_angle(x):
    return c_short(x << 8).value >> 8

def hex_to_ieee754(int_value):
    float_value = struct.unpack('>f', struct.pack('>I', int_value))[0]
    return float_value

def extract_detection (ntf):
    PD = Presence()
    PD.distance = ntf[0] + (ntf[1] << 8)    
    PD.angle = UwbConfig.AngleSignAdaptation(extract_angle(ntf[2]))
    PD.id = ntf[3]
    SNR = ntf[4] + (ntf[5] << 8) + (ntf[6] << 16) + (ntf[7] << 24) 
    PD.snr = hex_to_ieee754(SNR)
    PD.status = 1
    return PD

def presence_coordinates(distance, angle):
    x = - distance * math.sin(math.radians(angle))
    y = distance * math.cos(math.radians(angle))
    return x, y

def compute_position (presence):
    presence.x, presence.y = presence_coordinates(presence.distance, presence.angle)
    presence.x = Avg.adaptative_exponential_moving_avg(presence.x, presence.x_avg)
    presence.y = Avg.adaptative_exponential_moving_avg(presence.y, presence.y_avg)

def handle_detection(ocpd_ntf):
    global detected_presence, previous_angle
    if(ocpd_ntf[0] == 1): # status of presence detected 1--> presence detected
        if(UwbConfig.Multitarget == False):
            detected_presence = extract_detection(ocpd_ntf[4:])
            print(f'target #{detected_presence.id} detected at distance={detected_presence.distance:.0f}cm, angle={detected_presence.angle:.0f}°, snr={detected_presence.snr:.2f}')
            if detected_presence.angle == 127: detected_presence.angle = previous_angle
            previous_angle = detected_presence.angle
        else:
            for i in range (0, ocpd_ntf[2]):
                PD = extract_detection(ocpd_ntf[4 + i * 8:])
                print(f'target #{PD.id} detected at distance={PD.distance:.0f}cm, angle={PD.angle:.0f}°, snr={PD.snr:.0f}')
                if i == 0 or PD.distance < detected_presence.distance:
                    detected_presence.id = PD.id
                    detected_presence.distance = PD.distance
                    detected_presence.angle = PD.angle
                    detected_presence.snr = PD.snr
            print(f'Selected target is #{detected_presence.id}\n')            
            if detected_presence.angle == 127: detected_presence.angle = previous_angle
            previous_angle = detected_presence.angle
    else:
        print(f'no presence detected')
        clean_presence(detected_presence)
    return detected_presence.status