from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import socket
import struct
import math

# =========================
# UDP SOCKET (single port)
# =========================

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 4444))
sock.setblocking(False)

# =========================
# DATA BUFFERS
# =========================

x_vals = []
y_throttle = []
y_brake = []
y_clutch = []
y_rpm = []
y_speed = []
y_fuel = []
y_pitch = []

# =========================
# PACKET RECEIVER
# =========================

def receiveData():
    outgauge = None
    pitch_deg = None

    while True:
        try:
            data, addr = sock.recvfrom(4096)
        except socket.error:
            break

        # ---------- OutGauge packet (96 bytes) ----------
        if len(data) == 96:
            unpacked = struct.unpack("I4sH2c7f2I3f16s16si", data)

            speed = unpacked[5] * 2.23694  # m/s → mph
            rpm = unpacked[6]
            fuel = unpacked[9] * 100
            throttle = unpacked[14] * 100
            brake = unpacked[15] * 100
            clutch = unpacked[16] * 100

            outgauge = (throttle, brake, clutch, rpm, speed, fuel)

        # ---------- BeamNG vehicle dynamics packet (88 bytes) ----------
        elif len(data) == 88:
            unpacked = struct.unpack("4s21f", data)

            if unpacked[0] == b"BNG1":
                pitch_rad = unpacked[14]       # pitchPos in radians
                pitch_deg = math.degrees(pitch_rad)

    return outgauge, pitch_deg

# =========================
# PLOTTING SETUP
# =========================

plt.style.use("fivethirtyeight")

fig = plt.figure(figsize=(12, 14))
ax1 = fig.add_subplot(5, 1, 1)
ax2 = fig.add_subplot(5, 1, 2)
ax3 = fig.add_subplot(5, 1, 3)
ax4 = fig.add_subplot(5, 1, 4)
ax5 = fig.add_subplot(5, 1, 5)

index = count()

# =========================
# ANIMATION LOOP
# =========================

def animate(i):
    outgauge, pitch = receiveData()

    if outgauge is None:
        return

    throttle, brake, clutch, rpm, speed, fuel = outgauge

    x_vals.append(next(index))
    y_throttle.append(throttle)
    y_brake.append(brake)
    y_clutch.append(clutch)
    y_rpm.append(rpm)
    y_speed.append(speed)
    y_fuel.append(fuel)
    y_pitch.append(pitch if pitch is not None else 0)

    for ax in (ax1, ax2, ax3, ax4, ax5):
        ax.clear()

    if len(x_vals) > 100:
        for ax in (ax1, ax2, ax3, ax4, ax5):
            ax.set_xlim(x_vals[-100], x_vals[-1])

    ax1.set_ylim(-5, 105)
    ax2.set_ylim(-500, 10000)
    ax3.set_ylim(-5, 180)
    ax4.set_ylim(-5, 105)
    ax5.set_ylim(-20, 20)  # degrees

    ax1.plot(x_vals, y_throttle, label="Throttle", color="blue")
    ax1.plot(x_vals, y_brake, label="Brake", color="red")
    ax1.plot(x_vals, y_clutch, label="Clutch", color="green")
    ax1.legend(loc="upper left")

    ax2.plot(x_vals, y_rpm, color="black")
    ax3.plot(x_vals, y_speed, color="black")
    ax4.plot(x_vals, y_fuel, color="black")
    ax5.plot(x_vals, y_pitch, color="purple")

    ax1.set_ylabel("Pedals (%)")
    ax2.set_ylabel("RPM")
    ax3.set_ylabel("Speed (MPH)")
    ax4.set_ylabel("Fuel (%)")
    ax5.set_ylabel("Pitch (deg)")

    plt.tight_layout()

# =========================
# START
# =========================

ani = FuncAnimation(fig, animate, interval=10)
plt.show()

sock.close()