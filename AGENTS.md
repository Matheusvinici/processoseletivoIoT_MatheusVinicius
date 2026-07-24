# AGENTS.md

## Project

Wokwi ESP32 (DevKit C v4) MicroPython firmware simulation. IoT selection process project.

## Scenarios (pick exactly one)

| Scenario  | Topic                        | Sensor ID  | Init message                        |
|-----------|------------------------------|------------|-------------------------------------|
| `weight`  | Kanban stock monitor         | `hx711`    | `Sistema Kanban Inicializado`       |
| `light`   | Production piece counter     | `ldr1`     | `Contador de Producao Inicializado` |
| `temperature` | Temp & door monitor      | `imu1`     | `Sistema de Monitoramento Inicializado` |

## CI pipeline

1. Detect active scenario: checks which `scenarios/*.md` exists (priority: WEIGHT > TEMPERATURE > LIGHT)
2. `docker build -t esp32-builder -f Dockerfile .` (build ESP-IDF + mklittlefs image)
3. `docker run` copies `src/*.py` into littlefs and produces `fs.bin`
4. Wokwi CI runs 3 tests per scenario: `scenarios/{folder}/test_{1,2,3}.yaml`

Secret must be set as `WOKWI_CLI_TOKEN` (README says `WOKWI_API_KEY` but CI uses `WOKWI_CLI_TOKEN`).

## Critical rules

- **Exact string matching**: CI compares serial output character-by-character including accents and punctuation
- **Non-blocking architecture**: never use `time.sleep()` or blocking loops; use `time.ticks_ms()` timers instead
- **Only one scenario active**: delete unused scenario `.md` files and folders before committing
- **diagram.json** must include the required sensor with the exact ID from the scenario spec

## Available components per scenario

**Weight (Kanban):** `hx711` — no button needed _(abandoned, HX711 buggy in Wokwi)_
**Light (Counter):** `ldr1` (DO→GPIO4 PULL_UP, active-low) + `btn1` (reset, GPIO15 PULL_UP, active-low) ← **active**
**Temperature:** `imu1` (MPU6050 I2C) + `btn1` (door switch)

## Local build

```bash
docker build -t esp32-builder -f Dockerfile .
docker run --rm -v "$(pwd)/src:/mnt/src" -v "$(pwd):/mnt/out" esp32-builder bash -c "mkdir -p /tmp/fs && cp -r /mnt/src/* /tmp/fs/ && /mklittlefs/mklittlefs -c /tmp/fs -b 4096 -p 256 -s 0x200000 /mnt/out/fs.bin"
```

Dev container available at `.devcontainer/devcontainer.json`. Deps: `pip install mpremote`.

## Test format (scenarios/*/test_*.yaml)

Steps use three actions:
- `wait-serial: '<exact string>'` — blocks until string appears on serial
- `set-control: { part-id, control, value }` — changes sensor value
- `delay: <duration>` — waits (e.g. `1s`, `500ms`)