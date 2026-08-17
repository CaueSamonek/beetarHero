import os
import time
import math

import ledsBH
import lcdBH
import stateBH
import filesBH
import notesBH
import scoreBH
import audioBH
import inputBH
import configBH

def select_music():
    lcdBH.clear()
    ledsBH.light()

    # comeca escolhendo pela dificuldade
    elements = configBH.LEVELS
    level = None
    
    input_locked = False # flag pra mudar apenas 1 vez por aperto de botao
    idx = 0
    while True:
        if stateBH.sideSwitchChanged:
            stateBH.sideSwitchChanged = False
            lcdBH.write("Verifique a\nOrdem das Cores")
            ledsBH.light()
            time.sleep(1)

        if not input_locked:
            delta = 0
            if inputBH.buttons[0]:
                delta = 1
            if inputBH.buttons[1]:
                delta = -1

            if delta:
                idx = (idx + delta) % len(elements)
                input_locked = True

        elif not inputBH.buttons[0] and not inputBH.buttons[1] and not inputBH.buttons[2]:
            input_locked = False

        if inputBH.buttons[2] and not input_locked: # botao de 'enter'
            input_locked = True
            if not level: # escolheu a dificuldade
                level = elements[idx]
                elements = filesBH.getPlaylist(level)
                idx = 0
            else: # escolheu a musica
                if level == configBH.LEVELS[0]:
                    stateBH.countingErrors = False
                else:
                    stateBH.countingErrors = True
                return filesBH.getMusicPath(elements[idx], level)
        
        # botao de "voltar"
        if inputBH.buttons[3] and level:
            level = None
            elements = configBH.LEVELS
            idx = 0

        lcdBH.write('\n'.join(elements[idx].split(" - ", 1)))
        time.sleep(0.05)

def render(now_ms):
    ledsBH.blank()
    notesBH.updateNotes(now_ms)
    notesBH.updateInput(now_ms)
    ledsBH.show()
    lcdBH.write(scoreBH.lastJudgement)

def start_music(music_path):
    # carrega duracao da musica e suas notas
    start_ms, end_ms = filesBH.getTimestamps(music_path)
    duration_ms = end_ms - start_ms

    event_index = 0
    events = notesBH.loadNotes(music_path)
    while (event_index < len(events) and events[event_index].time_ms <= start_ms):
        event_index+=1

    # reseta estados da run, como 'runLost' e 'total_score'
    scoreBH.reset()
    stateBH.reset()

    audioBH.start(music_path, start_ms, end_ms) # comeca a tocar a musica com os timestamps
    configBH.timeCorrection() # delay para sincronizacao

    pct = ""
    base_ms = time.monotonic_ns() // 1_000_000 # relogio base em ms
    while True:
        played_ms = (time.monotonic_ns() // 1_000_000) - base_ms
        now_ms = played_ms + start_ms

        while (event_index < len(events) and events[event_index].time_ms <= now_ms):
            if events[event_index].time_ms <= end_ms:
                e = events[event_index]
                notesBH.spawnNote(e.mask, now_ms, e.length_leds)
            event_index += 1

        # atualiza porcentagem decorrida da musica
        if played_ms%10 == 0:
            pct = math.floor((played_ms/duration_ms)*100)
            pct = str(pct)
 
        # manipula a string de score a fim de 'encaixar' a porcentagem no lado superior direito do lcd
        s = scoreBH.lastJudgement.split('\n')
        s[0] = f"{s[0].split()[0]:<{16-len(pct)-1}}{pct}%"
        scoreBH.lastJudgement = '\n'.join(s)

        render(now_ms)

        if stateBH.runLost: # zerou a vida
            audioBH.stop()
            return 0

        if stateBH.endGame: # jogo morto no meio pelo botao especial
            audioBH.stop()
            return -1

        #acabou a musica
        if played_ms >= duration_ms:
            # espera nao ter mais notas ativas
            while notesBH.hasActive():
                played_ms = (time.monotonic_ns() // 1_000_000) - base_ms
                now_ms = played_ms + start_ms
                render(now_ms)

            # adiciona um pequeno delay pra n ficar estranho qnd acaba as notas
            delay_start_ms = now_ms
            while now_ms - delay_start_ms <= configBH.NOTE_TRAVEL_TIME_MS:
                played_ms = (time.monotonic_ns() // 1_000_000) - base_ms
                now_ms = played_ms + start_ms
                render(now_ms)

            return scoreBH.totalScore


def main():
    # retorna somente depois de conectar o input
    inputBH.start()

    while True:
        # em menu, permite modificacao de canhoto/destro e guitarra/piano
        stateBH.onMenu = True
        music = select_music()
        stateBH.onMenu = False
        
        final_score = start_music(music)

        if final_score == -1:
            lcdBH.write("Jogo Cancelado")
            ledsBH.clear()
            time.sleep(1)
            continue

        lcdBH.write(f"Pontuacao Final:\n{final_score}")

        if final_score:
            ledsBH.blinkLanes()
            ledsBH.slideLanes()
            ledsBH.blinkLanes()
        else:
            ledsBH.blinkRed()


if __name__ == "__main__":
    main()
