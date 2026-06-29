import os
import csv
import configBH
import json
from mutagen import File

AUDIO_ROOT = "Musicas" # pasta raiz dos arquivos de audio

# retorna as musicas da dificuldade especificada em ordem alfabetica
def getPlaylist(level):
    return sorted(next(os.walk(f"{AUDIO_ROOT}/{level}"))[1])

# retorna os arquivos de audio
def getMusicPath(music_name, level):
    return f"{AUDIO_ROOT}/{level}/{music_name}"

# retorna os arquivos de audio
def getMusic(music_path):
    return f"{music_path}/guitar.ogg", f"{music_path}/song.ogg"

# retorna o arquivo de notas de uma musica pra uma dificuldade especifica
def readNotes(music_path):
    notes = []
    path = f"{music_path}/notes.csv"
    with open(path, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            if not row:
                continue
            notes.append((int(row[0]), int(row[1]), int(row[2])))

    return notes

# retorna a duracao de um audio em milissegundos
def getDuration(path):
    try:
        return File(path).info.length
    except:
        return 0

def to_ms(s):
    m, ssm = s.split(":")
    minutes = int(m)
    v = ssm.split('.', 1)
    sec = v[0]
    mili = 0 if len(v) == 1 else v[1]
    seconds = int(sec)
    return int(round(minutes*60 + seconds)*1000) + int(mili)*100

# precisa verificar os dois pois tanto 'song' quanto 'guitar' podem nao existir
def getTimestamps(path):
    timestamps = os.path.join(path, "config.json")
    if os.path.exists(timestamps):
        with open(timestamps, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return to_ms(data["start"]), to_ms(data["end"])

    guitar, song = getMusic(path)

    d1 = getDuration(guitar)
    d2 = getDuration(song)

    return 0, int(max(d1, d2) * 1000)
