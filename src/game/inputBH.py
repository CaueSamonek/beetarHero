import time
import socket
import threading
import configBH

# vetor correspondente as teclas de cada lane
buttons = [0] * configBH.NUM_LANES

# pra conectar no esp32 da guitarra
ESP32_MAC = "30:76:F5:E5:B8:DA"
ESP32_PORT = 1

# fica tentando conectar no esp32 ateh conseguir
def connectGuitar():
    while True:
        try:
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)        
            sock.connect((ESP32_MAC, ESP32_PORT))
            print("ESP32 Bluetooth Conectado")
            print("Verfique se a música aparece no display", flush=True)

            return sock
        except Exception as e:
            print(f"Erro: {e}", flush=True)


# recebe e atribui 0 (botao foi solto) ou 1 (botao foi apertado) para cada botao
def bluetoothWorker(sock):
    while True:
        f = sock.makefile('r')

        try:
            for line in f:
                line = line.strip()
                
                # o ideal seria simplificar, mas com o esp32 morto
                # eh melhor deixar quieto isso por enquanto
                if line.startswith("BTN/"):
                    topic, value = line.split(':')
                    btn_id = int(topic.split('/')[1])
                    buttons[btn_id - 1] = int(value)

        except Exception as e:
            print(f"Bluetooth Thread Error: {e}")

        finally:
            f.close()
            sock.close()

# inicia processamento
def start():
    sock = connectGuitar()
    threading.Thread(target=bluetoothWorker, args=(sock,), daemon=True).start()
