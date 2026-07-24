from machine import Pin
import time

sck = Pin(18, Pin.OUT, value=0)
dout = Pin(19, Pin.IN, Pin.PULL_UP)

EMPTY_THRESHOLD = 200
FULL_WEIGHT = 5000
READ_INTERVAL_MS = 1000
REPORT_INTERVAL_MS = 2000

weight = 5000
state = "NORMAL"
last_read = 0
last_report = 0

def hx711_read():
    if dout.value():
        return None
    v = 0
    for _ in range(24):
        sck.value(1)
        v = (v << 1) | dout.value()
        sck.value(0)
    sck.value(1)
    sck.value(0)
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