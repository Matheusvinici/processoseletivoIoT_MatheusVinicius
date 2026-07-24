# Monitor de Estoque Kanban Inteligente

## Identificação do Candidato

- **Nome completo:** Matheus Vinicius Vidal de Andrade
- **GitHub:** [@Matheusvinici](https://github.com/Matheusvinici/processoseletivoIoT_MatheusVinicius)

## Visão Geral da Solução

Sistema embarcado para monitoramento de estoque em almoxarifados utilizando sensor de peso HX711 com ESP32. O firmware lê continuamente o peso de uma caixa organizadora, detecta consumo de peças, dispara alertas de reposição quando o estoque atinge nível crítico, e identifica anomalias como caixa ausente ou falha no sensor.

## Arquitetura do Sistema Embarcado

O firmware opera com uma máquina de estados não-bloqueante baseada em `time.ticks_ms()`:

- **NORMAL** — estoque dentro da faixa segura. Reporta periodicamente o peso atual.
- **EMPTY** — peso abaixo do limiar mínimo (200g). Dispara alerta de reposição único.
- **ANOMALY** — peso igual a 0g (caixa removida ou falha). Alerta de manutenção crítica.

Transições: NORMAL → EMPTY (consumo total), EMPTY → NORMAL (reabastecimento), qualquer estado → ANOMALY (peso zero).

## Componentes Utilizados na Simulação

| Componente     | ID     | Função                              |
|----------------|--------|--------------------------------------|
| ESP32 DevKit C | esp    | Microcontrolador                     |
| HX711          | hx711  | Sensor de peso (célula de carga)     |

### Conexões (diagram.json)

- HX711 VCC → ESP32 3V3
- HX711 GND → ESP32 GND
- HX711 DT → GPIO19
- HX711 SCK → GPIO18

## Decisões Técnicas Relevantes

- **Arquitetura não-bloqueante**: todo o loop usa `time.ticks_ms()` para temporização, sem `time.sleep()`, garantindo que os testes CI do Wokwi não percam eventos.
- **Mensagens exatas**: strings seguem rigorosamente o especificado nos testes (sem acentos em mensagens como "reposicao", "calibracao", "concluido") para casamento caractere-por-caractere do CI.
- **HX711 via bit-banging**: implementação do protocolo do HX711 via GPIO, sem dependências externas.

## Resultados Obtidos

O firmware passa nos 3 cenários de teste do Wokwi CI:

1. **Consumo Parcial** — peso cai de 5000g para 2500g → reporta "Status: Estoque Regular (2500g)"
2. **Ciclo Completo** — peso cai para 150g → alerta de reposição; retorna para 5000g → confirma reabastecimento
3. **Anomalia** — peso vai a 0g → alerta de caixa ausente/erro de calibração

### Como executar localmente

```bash
docker build -t esp32-builder -f Dockerfile .
docker run --rm -v "$(pwd)/src:/mnt/src" -v "$(pwd):/mnt/out" esp32-builder bash -c "mkdir -p /tmp/fs && cp -r /mnt/src/* /tmp/fs/ && /mklittlefs/mklittlefs -c /tmp/fs -b 4096 -p 256 -s 0x200000 /mnt/out/fs.bin"
```

Após o build, faça push para o GitHub para executar os testes automáticos via GitHub Actions.