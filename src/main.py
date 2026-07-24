import machine
import time

machine.Pin(18, machine.Pin.OUT, value=0)
machine.Pin(19, machine.Pin.IN)

OUT_W1TS = 0x3FF44008
OUT_W1TC = 0x3FF4400C
IN_REG = 0x3FF4403C

GPIO18 = 1 << 18
GPIO19 = 1 << 19

EMPTY_THRESHOLD = 200
FULL_WEIGHT = 5000
READ_INTERVAL_MS = 1000
REPORT_INTERVAL_MS = 2000

weight = 5000
state = "NORMAL"
last_read = 0
last_report = 0

def hx711_read():
    if machine.mem32[IN_REG] & GPIO19:
        return None
    v = 0
    for _ in range(24):
        machine.mem32[OUT_W1TS] = GPIO18
        v = (v << 1) | ((machine.mem32[IN_REG] & GPIO19) >> 19)
        machine.mem32[OUT_W1TC] = GPIO18
    machine.mem32[OUT_W1TS] = GPIO18
    machine.mem32[OUT_W1TC] = GPIO18
    if v > 0x7fffff:
        v -= 0x1000000
    return v

print("Sistema Kanban Inicializado")

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_read) >= READ_INTERVAL_MS:
        last_read = now
        raw = hx711_read()
        if raw is not None and 0 <= raw <= 100000:
            weight = raw
            if weight == 0:
                if state != "ANOMALY":
                    state = "ANOMALY"
                    print("ALERTA: Caixa ausente ou erro de calibração no sensor HX711!")
            elif weight <= EMPTY_THRESHOLD:
                if state != "EMPTY":
                    state = "EMPTY"
                    print("Evento de reposição disparado! Caixa vazia detectada.")
            else:
                if state == "EMPTY" and weight >= FULL_WEIGHT:
                    state = "NORMAL"
                    print("Abastecimento concluído. Caixa cheia.")
                elif state != "NORMAL":
                    state = "NORMAL"

    if state == "NORMAL" and time.ticks_diff(now, last_report) >= REPORT_INTERVAL_MS:
        last_report = now
        print("Status: Estoque Regular ({}g)".format(weight))