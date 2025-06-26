import socket
import time

def build_artnet_packet(universe, dmx_data):
    packet = bytearray()
    packet.extend(b'Art-Net\x00')
    packet.extend((0x00, 0x50))
    packet.extend((0x00, 14))
    packet.append(0x00)
    packet.append(0x00)
    packet.extend((universe & 0xFF, (universe >> 8)))
    packet.extend((len(dmx_data) >> 8, len(dmx_data) & 0xFF))
    packet.extend(dmx_data)
    return packet

GREEN_RGB = [0, 255, 0]
OFF_RGB = [0, 0, 0]

def get_led_count_for_universe(index):
    return 170 if index % 2 == 0 else 89

controllers = [
    {"ip": "192.168.1.45", "universe_start": 0,   "universe_end": 31},
    {"ip": "192.168.1.46", "universe_start": 32,  "universe_end": 63},
    {"ip": "192.168.1.47", "universe_start": 64,  "universe_end": 95},
    {"ip": "192.168.1.48", "universe_start": 96,  "universe_end": 127},
]

# 🟩 Étape 1 : Allumer en VERT
packets_on = []
for controller in controllers:
    ip = controller["ip"]
    for universe_index, universe in enumerate(range(controller["universe_start"], controller["universe_end"] + 1)):
        led_count = get_led_count_for_universe(universe_index)
        data = GREEN_RGB * led_count
        dmx_data = data + [0] * (512 - len(data))
        packets_on.append((ip, build_artnet_packet(universe, dmx_data)))

# ⬛ Étape 2 : Préparer l’extinction
packets_off = []
for controller in controllers:
    ip = controller["ip"]
    for universe_index, universe in enumerate(range(controller["universe_start"], controller["universe_end"] + 1)):
        led_count = get_led_count_for_universe(universe_index)
        data = OFF_RGB * led_count
        dmx_data = data + [0] * (512 - len(data))
        packets_off.append((ip, build_artnet_packet(universe, dmx_data)))

# Envoi ultra-rapide allumage
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for ip, packet in packets_on:
    sock.sendto(packet, (ip, 6454))
sock.close()
print("✅ LEDs allumées en vert")

# Attendre 5 secondes
time.sleep(5)

# Envoi ultra-rapide extinction
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for ip, packet in packets_off:
    sock.sendto(packet, (ip, 6454))
sock.close()
print("🕶️ LEDs éteintes proprement")
