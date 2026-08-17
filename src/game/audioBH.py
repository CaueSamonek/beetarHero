import subprocess
from mutagen import File
import filesBH
import threading
import filesBH

# mata o processo dos audios que estiverem rodando
processes = []
def stop():
    for p in processes:
        if p.poll() is None:
            p.terminate()

    processes.clear()

def to_mmss(ms):
    total_sec = ms // 1000
    mili = ms % 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes}:{seconds}.{mili}"

# comeca a tocar um audio qualquer
def start(music_path, start_ms=None, end_ms=None):
    threading.Thread(target=audioWorker, args=(music_path, start_ms, end_ms), daemon=True).start()

def play(filePath, start_ms=None, end_ms=None):
    cmd = ['mpv', '--no-video']
    if start_ms: cmd.append(f"--start={to_mmss(start_ms)}")
    if end_ms: cmd.append(f"--end={to_mmss(end_ms)}")
    
    cmd.append(filePath)
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# cria subprocessos que tocam a musica passada por parametro
def audioWorker(music_path, start, end):
    global processes
    guitar, song = filesBH.getMusic(music_path)

    try:
        p1 = play(guitar, start, end)
        p2 = play(song, start, end)

        processes = [p1,p2]

        p1.wait()
        p2.wait()

    except Exception as e:
        print(f"Audio Error: {e}")
    
    stop()
