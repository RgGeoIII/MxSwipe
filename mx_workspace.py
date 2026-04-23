#!/usr/bin/env python3
"""
MX Master 3 - Gesture workspace switcher pour Hyprland
Batch atomique : focusmonitor + workspace + movecursor en une seule commande
"""

import evdev
from evdev import InputDevice, ecodes
import subprocess
import json
import time

# ---- CONFIG ----
DEVICE_PATH = "/dev/input/event9"
THRESHOLD = 40
COOLDOWN = 0.5
# ----------------

btn_held = False
rel_x_accum = 0
last_switch_time = 0
origin_monitor = None
origin_cursor_x = None
origin_cursor_y = None

monitor_history = {}
monitor_index = {}


def get_cursor_pos():
    result = subprocess.run(["hyprctl", "cursorpos", "-j"], capture_output=True, text=True)
    pos = json.loads(result.stdout)
    return pos["x"], pos["y"]


def get_monitor_at(cursor_x, cursor_y):
    result = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True)
    monitors = json.loads(result.stdout)
    for m in monitors:
        if m["x"] <= cursor_x < m["x"] + m["width"] and m["y"] <= cursor_y < m["y"] + m["height"]:
            return m["name"], m["activeWorkspace"]["id"]
    return monitors[0]["name"], monitors[0]["activeWorkspace"]["id"]


def get_all_history_ids():
    ids = set()
    for history in monitor_history.values():
        ids.update(history)
    return ids


def get_all_existing_ids():
    result = subprocess.run(["hyprctl", "workspaces", "-j"], capture_output=True, text=True)
    workspaces = json.loads(result.stdout)
    return set(ws["id"] for ws in workspaces)


def get_visible_ids():
    result = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True)
    monitors = json.loads(result.stdout)
    return set(m["activeWorkspace"]["id"] for m in monitors)


def get_next_free_id():
    blocked = get_all_history_ids() | get_all_existing_ids() | get_visible_ids()
    i = 1
    while i in blocked:
        i += 1
    return i


def init_monitor(monitor_name, current_ws):
    other_history = set()
    for mon, hist in monitor_history.items():
        if mon != monitor_name:
            other_history.update(hist)

    if monitor_name not in monitor_history:
        if current_ws in other_history:
            # Ce workspace appartient à un autre moniteur, on ignore et on crée un nouveau
            monitor_history[monitor_name] = []
            monitor_index[monitor_name] = -1
        else:
            monitor_history[monitor_name] = [current_ws]
            monitor_index[monitor_name] = 0
    else:
        idx = monitor_index[monitor_name]
        history = monitor_history[monitor_name]
        if not history or (idx >= 0 and history[idx] != current_ws):
            if current_ws not in other_history:
                if current_ws in history:
                    monitor_index[monitor_name] = history.index(current_ws)
                else:
                    history.append(current_ws)
                    monitor_index[monitor_name] = len(history) - 1


def go_forward(monitor_name):
    idx = monitor_index[monitor_name]
    history = monitor_history[monitor_name]
    if idx < len(history) - 1:
        monitor_index[monitor_name] += 1
        return history[monitor_index[monitor_name]]
    new_ws = get_next_free_id()
    history.append(new_ws)
    monitor_index[monitor_name] += 1
    return new_ws


def go_back(monitor_name):
    idx = monitor_index[monitor_name]
    if idx <= 0:
        return None
    monitor_index[monitor_name] -= 1
    return monitor_history[monitor_name][monitor_index[monitor_name]]


def switch_workspace(direction):
    if direction > 0:
        target = go_forward(origin_monitor)
        arrow = "→"
    else:
        target = go_back(origin_monitor)
        arrow = "←"

    if target is None:
        print(f"{arrow} [{origin_monitor}] Début de l'historique")
        return

    # Batch atomique : les 3 commandes en une seule fois
    batch = (
        f"dispatch focusmonitor {origin_monitor} ; "
        f"dispatch workspace {target} ; "
        f"dispatch movecursor {origin_cursor_x} {origin_cursor_y}"
    )
    subprocess.run(["hyprctl", "--batch", batch])

    idx = monitor_index[origin_monitor]
    history = monitor_history[origin_monitor]
    print(f"{arrow} [{origin_monitor}] ws{target} ({idx+1}/{len(history)}) {history}")


def main():
    global btn_held, rel_x_accum, last_switch_time
    global origin_monitor, origin_cursor_x, origin_cursor_y

    try:
        device = InputDevice(DEVICE_PATH)
        print(f"✓ Connecté à : {device.name}")
        print("  Batch atomique - isolation maximale")
        print("  Ctrl+C pour quitter\n")
    except PermissionError:
        print("✗ Permission refusée : sudo usermod -aG input $USER")
        return
    except FileNotFoundError:
        print(f"✗ Périphérique {DEVICE_PATH} introuvable.")
        return

    for event in device.read_loop():
        if event.type == ecodes.EV_KEY and event.code == 277:
            if event.value == 1:
                origin_cursor_x, origin_cursor_y = get_cursor_pos()
                origin_monitor, current_ws = get_monitor_at(origin_cursor_x, origin_cursor_y)
                init_monitor(origin_monitor, current_ws)
                btn_held = True
                rel_x_accum = 0
                idx = monitor_index[origin_monitor]
                hist = monitor_history[origin_monitor]
                print(f"● [{origin_monitor}] ws{current_ws} ({idx+1}/{len(hist)}) {hist}")
            elif event.value == 0:
                btn_held = False
                rel_x_accum = 0

        elif event.type == ecodes.EV_REL and event.code == ecodes.REL_X:
            if btn_held:
                rel_x_accum += event.value
                now = time.time()

                if rel_x_accum >= THRESHOLD and (now - last_switch_time) > COOLDOWN:
                    switch_workspace(+1)
                    rel_x_accum = 0
                    last_switch_time = now

                elif rel_x_accum <= -THRESHOLD and (now - last_switch_time) > COOLDOWN:
                    switch_workspace(-1)
                    rel_x_accum = 0
                    last_switch_time = now


if __name__ == "__main__":
    main()
