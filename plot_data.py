# Plotting imports

from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# UDP set up

import socket
import struct


# Create UDP socket.

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# BeamNG BNG1 socket (vehicle dynamics)
sock_bng = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_bng.bind(("127.0.0.1", 62689))
sock_bng.setblocking(False)


# Bind to BeamNG OutGauge.

sock.bind(("127.0.0.1", 4444))
sock.setblocking(False)


# Receive UDP data and unpack


def receiveData():
    data = None

    while True:
        try:
            data, fromAddr = sock.recvfrom(4096)
        except socket.error:
            break

    if data is None:
        return None, None, None, None, None, None
    outsim_pack = struct.unpack("I4sH2c7f2I3f16s16si", data)
    gear = outsim_pack[3]
    speed = 2.23694 * outsim_pack[5]
    rpm = outsim_pack[6]
    engTemp = outsim_pack[8]
    fuel = 100 * outsim_pack[9]
    throttle = 100 * outsim_pack[14]
    brake = 100 * outsim_pack[15]
    clutch = 100 * outsim_pack[16]
    # print(f"RPM: {rpm:4.0f} Speed: {speed:3.0f}")
    return throttle, brake, clutch, rpm, speed, fuel


# Real-time graph

plt.style.use("fivethirtyeight")

x_vals = []
y_throttle = []
y_brake = []
y_clutch = []
y_rpm = []
y_speed = []
y_fuel = []

# Settings for subplots (Total number of plots, column position, row position)

fig = plt.figure(figsize=(12, 12))
ax1 = fig.add_subplot(4, 1, 1)
ax2 = fig.add_subplot(4, 1, 2)
ax3 = fig.add_subplot(4, 1, 3)
ax4 = fig.add_subplot(4, 1, 4)


def animate(i):

    throttle, brake, clutch, rpm, speed, fuel = receiveData()
    print(throttle, brake, clutch, rpm, speed, fuel)

    x_vals.append(next(index))
    y_throttle.append(throttle)
    y_brake.append(brake)
    y_clutch.append(clutch)
    y_rpm.append(rpm)
    y_speed.append(speed)
    y_fuel.append(fuel)

    # Needed to stop graphs changing colours

    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    # Moving x axis

    if len(x_vals) > 100:
        ax1.set_xlim(x_vals[-100], x_vals[-1])
        ax2.set_xlim(x_vals[-100], x_vals[-1])
        ax3.set_xlim(x_vals[-100], x_vals[-1])
        ax4.set_xlim(x_vals[-100], x_vals[-1])

    # Setting vertical axis limits

    ax1.set_ylim(-5, 105)
    ax2.set_ylim(-150, 10000)
    ax3.set_ylim(-5, 180)
    ax4.set_ylim(-5, 105)

    # Plotting graphs, with labels and colours

    ax1.plot(x_vals, y_throttle, lw=1, color="blue")
    ax1.plot(x_vals, y_brake, lw=1, color="red")
    ax1.plot(x_vals, y_clutch, lw=1, color="green")
    ax2.plot(x_vals, y_rpm, lw=1, color="black")
    ax3.plot(x_vals, y_speed, lw=1, color="black")
    ax4.plot(x_vals, y_fuel, lw=1, color="black")

    ax1.set_ylabel("Throttle, brake, clutch (%)")
    ax2.set_ylabel("RPM")
    ax3.set_ylabel("Speed (MPH)")
    ax4.set_ylabel("Fuel (%)")

    plt.tight_layout()


index = count()
ani = FuncAnimation(fig, animate, interval=10)

plt.show()


# Release the socket.
sock.close()
