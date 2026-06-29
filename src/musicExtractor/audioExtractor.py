import os
import shutil
import subprocess

def isAudio(file):
    if file.lower().endswith((".ogg", ".mp3", ".wav", ".opus", ".flac")):
        return True
    return False

def copyAudio(src_root, dst_root):
    guitar = None
    stems = []
    
    #separa arquivo da guitarra de todos os outros possiveis
    for f in os.listdir(src_root):
        if isAudio(f):
            l = f.lower()
            if "guitar" in l:
                guitar = f
            elif 'preview' not in l: #ignora qualquer 'preview'
                stems.append(f)

    # copia guitarra diretamente
    if guitar:
        shutil.copy2(os.path.join(src_root, guitar), os.path.join(dst_root, "guitar.ogg"))
    
    # se houver somente um arquivo, copia ele direto (evitar custo do ffmpeg)
    if len(stems) == 1:
        shutil.copy2(os.path.join(src_root, stems[0]), os.path.join(dst_root, "song.ogg"))

    # se existir mais de uma track de audio extra, junta todas e escreve soh um 'song.ogg'
    elif stems:
        subprocess.run(["ffmpeg", "-y"]
            + sum((["-i", os.path.join(src_root, f)] for f in stems), [])
            + [
                "-filter_complex",
                f"amix=inputs={len(stems)}:duration=longest",
                "-c:a", "libvorbis",
                os.path.join(dst_root, "song.ogg")
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
