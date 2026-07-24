# Contador de Peca Produzidas

## Identificacao do Candidato

- **Nome completo:** Matheus Vinicius Vidal de Andrade
- **GitHub:** [@Matheusvinici](https://github.com/Matheusvinici/processoseletivoIoT_MatheusVinicius)

## Visao Geral da Solucao

Sistema embarcado para contagem de pecas produzidas utilizando sensor LDR (fotoresistor) e ESP32-S3. O firmware monitora a luminosidade ambiente: quando uma peca passa e bloqueia a luz, o contador incrementa. Um botao fisico permite resetar o contador. Ideal para linhas de producao industrial.

## Arquitetura do Sistema Embarcado

O firmware opera com um loop nao-bloqueante baseado em `time.ticks_ms()`:

- Leitura digital do pino DO do LDR (HIGH = escuro, LOW = claro)
- Deteccao de borda de descida (transicao claro → escuro) incrementa o contador
- Botao (GPIO15, PULL_UP, active-low) reseta o contador
- Relatorio periodico de status a cada 2 segundos

## Componentes Utilizados na Simulacao

| Componente          | ID    | Funcao                          |
|---------------------|-------|----------------------------------|
| ESP32-S3 DevKit C-1 | esp   | Microcontrolador                 |
| LDR (fotoresistor)  | ldr1  | Sensor de luminosidade (DO)      |
| Pushbutton          | btn1  | Botao de reset (ativo baixo)     |

### Conexoes (diagram.json)

- LDR VCC → ESP32 3V3.1
- LDR GND → ESP32 GND.1
- LDR DO → GPIO4
- Botao 1.l → GPIO15
- Botao 2.l → ESP32 GND.1

## Decisoes Tecnicas Relevantes

- **Arquitetura nao-bloqueante**: todo o loop usa `time.ticks_ms()` para temporizacao, sem `time.sleep()`, garantindo que os testes CI do Wokwi nao percam eventos.
- **Mensagens exatas**: strings seguem rigorosamente o especificado nos testes para casamento caractere-por-caractere do CI.
- **DO digital**: uso da saida digital do LDR (nao ADC) para maior robustez na simulacao Wokwi.
- **Pull-up interno**: GPIO4 e GPIO15 configurados com pull-up interno para evitar flutuacao.

## Resultados Obtidos

O firmware passa nos 3 cenarios de teste do Wokwi CI:

1. **Deteccao de Primeira Peca** — bloqueio de luz → incrementa contador para 1
2. **Reset do Contador** — bloqueio de luz → contagem 1 → pressiona botao → reseta para 0
3. **Contagem Multipla** — 3 bloqueios consecutivos → contagem ate 3

### Como executar localmente

```bash
docker build -t esp32-builder -f Dockerfile .
docker run --rm -v "$(pwd)/src:/mnt/src" -v "$(pwd):/mnt/out" esp32-builder bash -c "mkdir -p /tmp/fs && cp -r /mnt/src/* /tmp/fs/ && /mklittlefs/mklittlefs -c /tmp/fs -b 4096 -p 256 -s 0x200000 /mnt/out/fs.bin"
```

Apos o build, faca push para o GitHub para executar os testes automaticos via GitHub Actions.

### Wokwi CLI Token

O token deve estar configurado como `WOKWI_CLI_TOKEN` nos secrets do GitHub.
