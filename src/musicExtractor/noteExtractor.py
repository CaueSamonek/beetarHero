# vale destacar que, devido a eletrica do artbot, as lanes sao invertidas,
# entao a 'lane 0' ao inves de ser a verde (mais a esquerda) é a azul (mais a direita)

import mido
import re

# recebe um arquivo de notas e o processa nas 3 dificuldades
def parseFile(filePath, level):
    fileType = filePath[filePath.rfind('.')+1:]

    GameConfig = { # configuracao geral de dificuldade e notas
        'chart': {
            'parser': parseChart,
            'Facil':   ("EasySingle"  , {0:4, 1:3, 2:2}),
            'Medio': ("MediumSingle", {0:4, 1:3, 2:2, 3:1}),
            'Dificil':   ("HardSingle"  , {0:4, 1:3, 2:2, 3:1, 4:0}),
        },

        'mid': {
            'parser': parseMidi,
            'Facil':   {60:4, 61:3, 62:2},
            'Medio': {72:4, 73:3, 74:2, 75:1},
            'Dificil':   {84:4, 85:3, 86:2, 87:1, 88:0},
        }
    }

    parser = GameConfig[fileType]['parser']
    config = GameConfig[fileType][level]

    try:
        # tentar retornar arquivo de notas processado
        return parser(filePath, config)

    except Exception as e:
        print("Erro ao ler Arquivo de Notas:", e)
        return None

def parseMidi(mid_path, mid_notes):
    try:
        mid = mido.MidiFile(mid_path) # tenta abrir arquivo .mid, se n der, explode
    except:
        print(f"\n[MIDI ERROR] .mid Ignorado: {mid_path}\n")
        return

    events = []
    active_notes = {}
    current_time_ms = 0.0

    for msg in mid:
        current_time_ms += msg.time * 1000

        if msg.type == 'note_on' and msg.velocity > 0:
            lane = mid_notes.get(msg.note)
            if lane is not None:
                active_notes[msg.note] = (lane, current_time_ms)

        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            note_data = active_notes.pop(msg.note, None)
            if note_data:
                lane, start_ms = note_data
                duration_ms = current_time_ms - start_ms

                # converte duracao pra um inteiro por causa dos leds
                size = max(1, int(duration_ms / 100))
                events.append((int(start_ms), lane, size))

    events.sort() #ordena pelo tempo de spawn de cada nota
    return events


def parseChart(chart_path, chart_config):
    chart_section, chart_notes = chart_config

    with open(chart_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    resolution = 192
    for line in lines:
        match = re.search(r'Resolution = (\d+)', line)
        if match:
            resolution = int(match.group(1))
            break

    bpm = 120.0
    sync_track = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[SyncTrack]"):
            sync_track = True
            continue

        if sync_track:
            if stripped == "}":
                break

            match = re.match(r'(\d+)\s*=\s*B\s*(\d+)', stripped)
            if match:
                bpm = int(match.group(2))/1000
                break

    tick_ms = 60000 / (bpm * resolution)
    events = []
    inside = False
    difficulty_section = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith(f"[{chart_section}]"):
            difficulty_section = True
            continue

        if difficulty_section and stripped == "{":
            inside = True
            continue

        if inside and stripped == "}":
            break

        if inside:
            match = re.match(r'(\d+)\s*=\s*N\s*(\d+)\s*(\d+)', stripped)
            if match:
                tick = int(match.group(1))
                note = int(match.group(2))
                length = int(match.group(3))

                lane = chart_notes.get(note)
                if lane is not None:
                    start_ms = int(tick * tick_ms)
                    duration_ms = int(length * tick_ms)
                    size = max(1, duration_ms // 100)
                    events.append((start_ms, lane, size))

    events.sort()
    return events
