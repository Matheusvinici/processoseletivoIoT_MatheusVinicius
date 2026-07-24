from machine import Pin
import time

sck = Pin(18, Pin.OUT, value=0)
dout = Pin(19, Pin.IN)

EMPTY_THRESHOLD = 200
FULL_WEIGHT = 5000

weight = 5000
state = "NORMAL"
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

    now = time.ticks_ms()
    if state == "NORMAL" and time.ticks_diff(now, last_report) >= 2000:
        last_report = now
        print("Status: Estoque Regular ({}g)".format(weight))

    time.sleep_ms(500)