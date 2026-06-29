import time
import board
import neopixel
import stateBH
import configBH

# Configuracoes pra fita de LSD
BRIGHTNESS = 0.1

COLOR_BLACK  = (0,0,0)
COLOR_WHITE  = (255,255,255)
COLOR_GREEN  = (0,255,0)
COLOR_RED    = (255,0,0)
COLOR_YELLOW = (255,255,0)
COLOR_BLUE   = (0,0,255)
COLOR_ORANGE = (255,100,0)

# mapeia cores pra cada lane: 'lane 0' = verde
laneColors = [COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_BLUE, COLOR_ORANGE]

# Constroi uma fita de LED (vetor de RGB)
pixels = neopixel.NeoPixel(board.D21, configBH.NUM_LANES * configBH.LEDS_PER_LANE,
                                          brightness=BRIGHTNESS, auto_write=False)

# funcao pra converter indexacao por matriz para indexacao de vetor
def ledPos(lane, pos):
    if lane % 2 == 0:
        return lane * configBH.LEDS_PER_LANE + pos

    return lane * configBH.LEDS_PER_LANE + (configBH.LEDS_PER_LANE - pos - 1)

# wrapper pra exibicao
def show():
    pixels.show()

# wrapper pra set de cores
def setColor(lane, pos, color=None):
    pixels[ledPos(lane, pos)] = lane2color(lane) if color is None else color

# inverte as cores de acordo com o estado
def lane2color(lane):
    if lane < 0 or lane >= configBH.NUM_LANES:
        return COLOR_WHITE # fora do range das lanes normais

    if stateBH.sideSwitch:
        return laneColors[lane]
    else:
        return laneColors[configBH.NUM_LANES-lane-1]

# usado apenas pra limpar o buffer do led, sem exibir ele inteiro apagado
def blank():
    pixels.fill(COLOR_BLACK)

# apagar e exibir todos os leds
def clear():
    blank()
    pixels.show()

# acende todas as lanes com suas cores
def light():
    for j in range(configBH.NUM_LANES):
        for k in range(configBH.LEDS_PER_LANE):
            setColor(j, k)
    pixels.show()

# fazer as cores deslizarem pro lado em loop
def slideLanes():
    for i in range(15):
        for j in range(configBH.NUM_LANES):
            for k in range(configBH.LEDS_PER_LANE):
                setColor(j, k, lane2color((j+i)%configBH.NUM_LANES))
        pixels.show()
        time.sleep(0.3)
    clear()

# faz as lanes piscarem em suas respectivas cores
def blinkLanes():
    for i in range(5):
        light()
        time.sleep(0.3)
        clear()
        time.sleep(0.3)

# faz todos os leds piscarem em vermelho
def blinkRed():
    for i in range(5):
        for j in range(configBH.NUM_LANES):
            for k in range(configBH.LEDS_PER_LANE):
                setColor(j, k, COLOR_RED)
        pixels.show()
        time.sleep(0.3)
        clear()
        time.sleep(0.3) 
