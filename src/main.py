from machine import Pin, ADC
import time

ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_12BIT)

btn = Pin(15, Pin.IN, Pin.PULL_UP)

DARK_THRESHOLD = 3000
BRIGHT_THRESHOLD = 2000

counter = 0
last_bright = True
last_btn = True
last_report = 0

print("Contador de Producao Inicializado")

while True:
    now = time.ticks_ms()

    val = ldr.read()
    bright_now = val < BRIGHT_THRESHOLD

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