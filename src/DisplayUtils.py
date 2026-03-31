# Copyright 2022-2025 NXP
#
# NXP Proprietary. This software is owned or controlled by NXP and may only be
# used strictly in accordance with the applicable license terms. By expressly
# accepting such terms or by downloading, installing, activating and/or otherwise
# using the software, you are agreeing that you have read, and that you agree to
# comply with and are bound by, such license terms. If you do not agree to be
# bound by the applicable license terms, then you may not retain, install,
# activate or otherwise use the software.

import src.UwbUtils as UwbUtils
import src.Averaging as Avg

# Global variables
Multiplier_index = 900
circle_size = 30
change_detection_trigger = 10
prev_display_x = prev_display_y = 0

def delete_map():
    global isMapShown
    isMapShown = False
    canvas.delete("map")
    canvas.delete(f"presence")

def draw_map(max_dist):
    global isMapShown
    isMapShown = True
    canvas.delete("no_target")
    for i in range (100, max_dist, 100):
        canvas.create_arc(center_x - i*Multiplier_factor,
                          center_y - i*Multiplier_factor,
                          center_x + i*Multiplier_factor,
                          center_y + i*Multiplier_factor,
                          start=210,
                          extent=120,
                          dash=(3,3), outline='black', tag="map")
        canvas.create_text(center_x, center_y + i*Multiplier_factor + 20, text=f'{i}cm', fill ="black", font=('Helvetica 16'), tag="map")
    canvas.create_arc(center_x - max_dist*Multiplier_factor,
                      center_y - max_dist*Multiplier_factor,
                      center_x + max_dist*Multiplier_factor,
                      center_y + max_dist*Multiplier_factor,
                      start=210,
                      extent=120,
                      dash=(3,3), outline='black', tag="map")
    canvas.create_arc(center_x - (10)*Multiplier_factor,
                      center_y - (10)*Multiplier_factor,
                      center_x + (10)*Multiplier_factor,
                      center_y + (10)*Multiplier_factor,
                      start=180,
                      extent=180,
                      fill="black", tag="map")
    canvas.create_text(center_x, center_y + max_dist*Multiplier_factor + 20, text=f'{max_dist}cm', fill ="black", font=('Helvetica 20 bold'), tag="map")
    canvas.update()

def display_presence (x, y, tag):
    global prev_display_x, prev_display_y, Multiplier_factor
    next_display_x, next_display_y = check_presence_move(prev_display_x, x * Multiplier_factor, prev_display_y, y * Multiplier_factor)
    size = circle_size / Multiplier_factor * 1.5
    canvas.create_oval(center_x + next_display_x + size*Multiplier_factor,
                       center_y + next_display_y + size*Multiplier_factor,
                       center_x + next_display_x - size*Multiplier_factor,
                       center_y + next_display_y - size* Multiplier_factor,
                       fill="white",
                       tags=tag)
    prev_display_x = next_display_x
    prev_display_y = next_display_y

def print_presence_info(d, a):
    canvas.create_text(canvas.winfo_width()-300, 100, text=f'Distance = {d:4.0f}cm', anchor="ne", fill ="white", font=('Helvetica 30 bold'), tag=f"presence")
    canvas.create_text(canvas.winfo_width()-300, 150, text=f'Angle = {a:4.0f}deg', anchor="ne", fill ="white", font=('Helvetica 30 bold'), tag=f"presence")

def show_presence(presence):
    canvas.delete(f"presence")
    if(presence.status == True):
        UwbUtils.compute_position(presence)
        display_presence(presence.x, presence.y, f"presence")
        print_presence_info(presence.distance, presence.angle)

def check_presence_move(p_x, n_x, p_y, n_y):
    if(abs(p_x - n_x) > (change_detection_trigger*Multiplier_factor) or abs(p_y - n_y) > (change_detection_trigger*Multiplier_factor)):
        return n_x, n_y
    return p_x, p_y

def process_generic(cv, max_dist, ntf_event, handler):
    global canvas, center_x, center_y, Multiplier_factor
    # Loop until GUI is closed or execution aborted
    canvas = cv    
    canvas.update()
    Multiplier_factor = canvas.winfo_height() / 1200 * Multiplier_index / max_dist
    center_x = int(canvas.winfo_width() // 2)
    center_y = int(canvas.winfo_height() // 6)

    canvas.create_text(50, 50, text=f'Presence detection demo', anchor="nw", fill ="white", font=('Helvetica 50 bold'))
    canvas.create_text(50, 150, text=f'Max detection distance = {max_dist}cm', anchor="nw", fill ="white", font=('Helvetica 30 bold'))

    while (1):
        if not UwbUtils.detected_presence.status:
            delete_map()
            canvas.create_text(center_x, 400, text=f'Running low power presence checking', fill ="white", font=('Helvetica 50 bold'), tags="no_target")
            canvas.create_text(center_x, 600, text=f'No target detected', fill ="red", font=('Helvetica 50 bold'), tags="no_target")
        else: 
            if not isMapShown: draw_map(max_dist)
            show_presence(UwbUtils.detected_presence)
        canvas.update()

        ntf_event.wait(1)
        ntf_event.clear()
        if handler.sigint:
            break
