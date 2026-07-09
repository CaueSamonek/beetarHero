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

# awa soh veno se cabe
def format_time(ms):
    total_seconds = ms / 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def updateDisplay():
    ledsBH.show()
    lcdBH.write(scoreBH.lastJudgement)

def select_music():
    lcdBH.clear()
    ledsBH.light()

    # comeca escolhendo pela dificuldade
    elements = configBH.LEVELS
    level = None
    confirmando_troca = False
    
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
                if confirmando_troca:
                    confirmando_troca = False
                else:
                    delta = 1
            if inputBH.buttons[1]:
                if confirmando_troca:
                    confirmando_troca = False
                else:
                    delta = -1

            if delta:
                idx = (idx + delta) % len(elements)
                input_locked = True

        elif not inputBH.buttons[0] and not inputBH.buttons[1] and not inputBH.buttons[2] and not inputBH.buttons[4]:
            input_locked = False

        if inputBH.buttons[4] and not input_locked:
            input_locked = True
            if not confirmando_troca:
                confirmando_troca = True
                lcdBH.clear()
                lcdBH.write("Confirmar?\nAperte novamente")
                time.sleep(0.05)
            else:
                inputBH.sendKeyChange()                
                confirmando_troca = False

        if inputBH.buttons[2] and not input_locked: # botao de 'enter'
            input_locked = True
            if confirmando_troca:
                confirmando_troca = False
            elif not level: # escolheu a dificuldade
                level = elements[idx]
                elements = filesBH.getPlaylist(level)
                idx = 0
            else: # escolheu a musica
                if level == configBH.LEVELS[0]:
                    stateBH.countingErrors = False
                else:
                    stateBH.countingErrors = False
                return filesBH.getMusicPath(elements[idx], level)
            
        if inputBH.buttons[3] and not input_locked and confirmando_troca:
            input_locked = True
            confirmando_troca = False

        if inputBH.buttons[3] and level:
            level = None
            elements = configBH.LEVELS
            idx = 0

        if not confirmando_troca:
            lcdBH.write('\n'.join(elements[idx].split(" - ", 1)))
        time.sleep(0.05)


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

    base_ms = time.monotonic_ns() // 1_000_000 # relogio base em ms
    while True:
        played_ms = (time.monotonic_ns() // 1_000_000) - base_ms
        now_ms = played_ms + start_ms
        while (event_index < len(events) and events[event_index].time_ms <= now_ms):
            if events[event_index].time_ms <= end_ms:
                e = events[event_index]
                notesBH.spawnNote(e.mask, now_ms, e.length_leds)
                event_index += 1

        ledsBH.blank()
        notesBH.updateNotes(now_ms)
        notesBH.updateInput(now_ms)



        # soh teste
        if played_ms%1000 == 0: #atualiza porcentagem a cada segundo
            # awa to veno
            s = scoreBH.lastJudgement.split('\n')
            a = math.floor((played_ms/duration_ms)*100)
            if a>100:
                a=100 #evitar umas porcentagens extras por causa do TRAVEL TIME no fim
            a = str(a)
            s[0] = f"{s[0].split()[0]:<{16-len(a)-1}}{a}%"
            scoreBH.lastJudgement = '\n'.join(s)

        updateDisplay()

        if stateBH.runLost: # zerou a vida
            audioBH.stop()
            return 0

        if stateBH.endGame: # jogo morto no meio pelo botao especial
            audioBH.stop()
            return -1

        if played_ms >= duration_ms + configBH.NOTE_TRAVEL_TIME_MS:
            audioBH.stop()
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
