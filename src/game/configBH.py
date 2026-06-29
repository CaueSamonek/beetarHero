import time

# disposicao dos leds
NUM_LANES = 5
LEDS_PER_LANE = 12
HIT_LINE = 8

# velocidade das notas
NOTE_TRAVEL_TIME_MS = 1500
NOTE_SPEED = (LEDS_PER_LANE - 1) / NOTE_TRAVEL_TIME_MS

# abstracao dos niveis de dificuldade disponiveis pra cada musica
# texto exibido no display lcd e nome dos diretorios dentro de 'Musicas/'
LEVELS = ['Facil', 'Medio', 'Dificil']

# delay adicionado entre inicio da musica e inicio das notas
# necessario porque nossa HIT_LINE nao condiz com a original
def timeCorrection():
    time.sleep(0.9)
