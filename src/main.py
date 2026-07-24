from machine import Pin
import time

ldr = Pin(4, Pin.IN, Pin.PULL_UP)
btn = Pin(15, Pin.IN, Pin.PULL_UP)

counter = 0
last_bright = True
last_btn = True
last_report = 0

print("Contador de Producao Inicializado")

while True:
    now = time.ticks_ms()

    bright_now = ldr.value()

    if last_bright and not bright_now:
        counter += 1
        print("Peca Detectada! Total: {}".format(counter))
    last_bright = bright_now

    btn_val = btn.value()
    if last_btn and not btn_val:
        counter = 0
        print("Contador resetado para 0")
    last_btn = btn_val

    if time.ticks_diff(now, last_report) >= 2000:
        last_report = now
        print("Contagem atual: {} pecas".format(counter))