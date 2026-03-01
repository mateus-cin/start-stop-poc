import socket
import struct
import time
import math
import pyautogui

# =========================
# CONFIGURAÇÕES
# =========================

UDP_IP = "127.0.0.1"
UDP_PORT = 4444

RPM_IDLE_MAX = 850          # rpm
RPM_IDLE_BASE = 750         # rpm nominal

THROTTLE_MIN = 2.0          # %
BRAKE_MIN = 10.0            # %
CLUTCH_DISENGAGED = 90.0    # %
CLUTCH_ENGAGE = 80.0        # %

PITCH_STOP_MAX = 6.0        # deg
PITCH_RESTART = 3.0         # deg

SPEED_STOP_MAX = 0.1        # km/h

STABLE_OFF_TIME = 0.5       # s
MAX_ENGINE_OFF_TIME = 120   # s

START_HOLD_TIME = 2.0       # s (key hold)

LOOP_DT = 0.02              # 50 Hz

# =========================
# SOCKET
# =========================

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

# =========================
# ESTADOS
# =========================

engine_on = True
engine_off_timestamp = None
off_condition_start = None

last_pitch_deg = 0.0

# =========================
# FUNÇÕES DE ATUAÇÃO
# =========================

def engine_off():
    print("ENGINE OFF")
    pyautogui.press("v")

def engine_on_action():
    print("ENGINE ON")
    pyautogui.keyDown("v")
    time.sleep(START_HOLD_TIME)
    pyautogui.keyUp("v")

# =========================
# LOOP PRINCIPAL
# =========================

while True:
    outgauge = None
    pitch_deg = None

    # -------------------------
    # Leitura UDP
    # -------------------------
    while True:
        try:
            data, addr = sock.recvfrom(256)
        except socket.error:
            break

        # OutGauge
        if len(data) == 96:
            u = struct.unpack("I4sH2c7f2I3f16s16si", data)

            speed = u[5] * 3.6          # km/h
            rpm = u[6]
            throttle = u[14] * 100
            brake = u[15] * 100
            clutch = u[16] * 100

            outgauge = (speed, rpm, throttle, brake, clutch)

        # BeamNG BNG1
        elif len(data) == 88:
            u = struct.unpack("4s21f", data)
            if u[0] == b"BNG1":
                pitch_rad = u[14]       # CORRETO
                pitch_deg = math.degrees(pitch_rad)
                last_pitch_deg = pitch_deg

    if outgauge is None:
        time.sleep(LOOP_DT)
        continue

    speed, rpm, throttle, brake, clutch = outgauge
    pitch = pitch_deg if pitch_deg is not None else last_pitch_deg

    now = time.time()

    # =========================
    # CONDIÇÃO DE DESLIGAMENTO
    # =========================

    off_conditions = (
        speed <= SPEED_STOP_MAX and
        rpm <= RPM_IDLE_MAX and
        throttle <= THROTTLE_MIN and
        brake >= BRAKE_MIN and
        clutch >= CLUTCH_DISENGAGED and
        abs(pitch) <= PITCH_STOP_MAX
    )

    if engine_on:
        if off_conditions:
            if off_condition_start is None:
                off_condition_start = now
            elif (now - off_condition_start) >= STABLE_OFF_TIME:
                engine_off()
                engine_on = False
                engine_off_timestamp = now
                off_condition_start = None
        else:
            off_condition_start = None

    # =========================
    # CONDIÇÃO DE RELIGAMENTO
    # =========================

    else:
        restart_conditions = (
            throttle > THROTTLE_MIN or
            clutch < CLUTCH_ENGAGE or
            (abs(pitch) >= PITCH_RESTART and brake < BRAKE_MIN)
        )

        timeout_condition = (
            engine_off_timestamp is not None and
            (now - engine_off_timestamp) >= MAX_ENGINE_OFF_TIME
        )

        if restart_conditions or timeout_condition:
            engine_on_action()
            engine_on = True
            engine_off_timestamp = None

    # =========================
    # LOG DEBUG
    # =========================

    print(
        f"SPD={speed:5.2f} km/h | "
        f"RPM={rpm:4.0f} | "
        f"THR={throttle:5.1f}% | "
        f"BRK={brake:5.1f}% | "
        f"CLT={clutch:5.1f}% | "
        f"PITCH={pitch:6.2f}° | "
        f"ENG={'ON' if engine_on else 'OFF'}"
    )

    time.sleep(LOOP_DT)