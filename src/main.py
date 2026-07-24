import time
from hx711_spi import HX711

sensor = HX711(23, 19, gain=128)

EMPTY_THRESHOLD = 200
FULL_WEIGHT = 5000
READ_INTERVAL_MS = 500
REPORT_INTERVAL_MS = 2000

last_read = 0
last_report = 0
state = "NORMAL"
weight = 5000

print("Sistema Kanban Inicializado")

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_read) >= READ_INTERVAL_MS:
        last_read = now
        raw = sensor.read()
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