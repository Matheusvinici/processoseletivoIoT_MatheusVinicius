from machine import Pin
import time

class HX711:
    def __init__(self, dout_pin, sck_pin):
        self.dout = Pin(dout_pin, Pin.IN, Pin.PULL_UP)
        self.sck = Pin(sck_pin, Pin.OUT, value=0)

    def read(self):
        if self.dout.value() == 1:
            return None
        value = 0
        for _ in range(24):
            self.sck.value(1)
            time.sleep_us(100)
            value = (value << 1) | self.dout.value()
            self.sck.value(0)
            time.sleep_us(100)
        self.sck.value(1)
        time.sleep_us(100)
        self.sck.value(0)
        time.sleep_us(100)
        if value > 0x7fffff:
            value -= 0x1000000
        return value

EMPTY_THRESHOLD = 200
FULL_WEIGHT = 5000
READ_INTERVAL_MS = 200
REPORT_INTERVAL_MS = 2000

sensor = HX711(19, 18)
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