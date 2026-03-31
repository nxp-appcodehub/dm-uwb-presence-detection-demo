# Copyright 2022-2025 NXP
#
# NXP Proprietary. This software is owned or controlled by NXP and may only be
# used strictly in accordance with the applicable license terms. By expressly
# accepting such terms or by downloading, installing, activating and/or otherwise
# using the software, you are agreeing that you have read, and that you agree to
# comply with and are bound by, such license terms. If you do not agree to be
# bound by the applicable license terms, then you may not retain, install,
# activate or otherwise use the software.

from threading import Thread, Event
import signal
import sys
import time
import tkinter as tk
from tkinter import Button

import src.UartInterface as UartIntf
import src.UwbUtils as UwbUtils
import src.UwbConfig as UwbConfig
import src.DisplayUtils as DisplayUtils

# Default values
com_port = "COM40"
max_dist = 500 # default maximum presence detection in cm
debug_uci = 0 # enable/disable UCI measurment NTFs

# Create the main application window 
root = tk.Tk()
root.attributes('-fullscreen', True)
root.title("SR250 OCPD demos")
canvas = tk.Canvas(root, bg="light blue")
canvas.pack(fill=tk.BOTH, expand=True) 
 
ntf_event = Event()
exit_event = Event()

# Serial communication mgt #################################
class SIGINThandler():
    def __init__(self):
        self.sigint = False
    
    def signal_handler(self, signal, frame):
        print("You pressed Ctrl+C!")
        self.sigint = True

def stop_threads():
    UartIntf.stop_write_thread = True
    UartIntf.stop_read_thread = True
    UartIntf.command_queue.put([0xFF, 0xFF])  # End of write
    time.sleep(0.1)

def kill_app():
    stop_threads()
    handler.sigint = True
    sys.exit()

def exit_pressed():
    exit_event.set()
    time.sleep(0.1)
    kill_app()

def wait_before_stop(timeout):
    time.sleep(0.1)
    exit_event.wait(timeout)
    kill_app()

current_mode = ""

# switch mode between checking and monitoring on presence detection status change
def switch_mode(mode):
    global current_mode
    if current_mode != mode:
        current_mode = mode
        if mode == "checking": 
            UwbConfig.setOCPD(angle=False, magnitude=False, multitarget=False, sensitivity=0x34, maxDistance=max_dist, powerMode='LowPower')
        elif mode == "monitoring": 
            UwbConfig.setOCPD(angle=True, magnitude=True, multitarget=True, sensitivity=0x2e, maxDistance=max_dist, maxFoV=60, freq=50, hold=2000, powerMode='Default')
        UartIntf.command_queue.put(UwbConfig.getRadarCommands("OCPD"))

# decoding OCPD notification
def handle_ocpd_ntf(ocpd_ntf):
    # Parse OCPD notifcation to retrieve all detected targets
    status = UwbUtils.handle_detection(ocpd_ntf)
    if(status):
        # Presence detected, select monitoring mode
        switch_mode("monitoring")
    ntf_event.set()

def start_processing():
    canvas.update()
    exit_button = Button(root, text="Exit", command=exit_pressed) 
    exit_button.place(x=canvas.winfo_width(), y=2, anchor="ne") 
    DisplayUtils.process_generic(canvas, max_dist, ntf_event, handler)
         
    stop_threads()

HELP = "Arguments: demo_presence_detection.py <com_port> <max_distance=xxx> <-D>\n \
    \t- com_port: default port is \"COM40\"\n \
    \t- max_distance: maximum detection distance in cm (default is 500cm)\n \
    \t- -D: enable UCI logging\n \
    "

def main():
    global handler
    global com_port, max_dist, debug_uci

    handler = SIGINThandler()
    signal.signal(signal.SIGINT, handler.signal_handler)
    
    for idx in range (1, len(sys.argv)):
        arg = sys.argv[idx]
        if (str(arg).__contains__("help")): 
            print(HELP)
            sys.exit()
        elif (str(arg).__contains__("COM")):
            com_port = arg
        elif (arg.__contains__("max_distance=")):
            max_dist = int(arg[13:])
        elif (arg.__contains__("-D")):
            debug_uci = 1
        else:
            print(f'Error: Unknown parameter [{arg}]')
            print(HELP)
            sys.exit()  

    print("\n~~ Presence detection demo")
    print(f"~ The application will sense for presence detection in low power mode until presence is being detected")
    print(f"~ in the maximum defined range ({max_dist}cm). As soon as presence is detected, the application will monitor")
    print(f"~ the presence localization (only closest detected target) on a 2D map.\n")

    UartIntf.serial_port_configure(com_port, debug_uci)

    Cmds = UwbConfig.getConfigCommands()
    for i in range (0, len(Cmds)): UartIntf.command_queue.put(Cmds[i])  

    # Radar session creation
    UartIntf.command_queue.put(UwbConfig.getRadarCommands("INIT"))

    # Select starting mode as presence checking (will switch to monitoring as soon as presence is being detected) 
    switch_mode("checking")

    # Radar session configuration and start
    Cmds = UwbConfig.getRadarCommands("START")
    for i in range (0, len(Cmds)): UartIntf.command_queue.put(Cmds[i]) 

    read_thread = Thread(target=UartIntf.read_from_serial_port, args=(handle_ocpd_ntf, UartIntf.null_fct, UartIntf.null_fct))
    read_thread.start()
        
    write_thread = Thread(target=UartIntf.write_to_serial_port, args=())
    write_thread.start()
       
    start_processing()

if __name__ == "__main__":
    main()
