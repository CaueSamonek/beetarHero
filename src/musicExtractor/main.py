import os
import csv
import shutil
import subprocess

import noteExtractor
import audioExtractor

# diretorio com os charts originais
INPUT_ROOT = "Songs"
OUTPUT_ROOT = "Musicas" # destino das musicas extraidas, gerado automaticamente
SUBDIRS = ['Facil', 'Medio', 'Dificil'] # divisao pre definida das musicas

def process_song(src_dir):
    notes_file = None

    # procura o arquivo de notas (.mid ou .chart) no diretorio 'src_dir'
    for f in os.listdir(src_dir):
        lower = f.lower()
        if lower == "notes.chart" or lower == "notes.mid":
            notes_file = os.path.join(src_dir, f)
            break
    for l in SUBDIRS:
        if l in src_dir:
            level = l
            break

    if not notes_file or not level:
        return

    # processa arquivo de notas encontrado em 'Facil', 'Medio' ou 'Dificil'
    notes = noteExtractor.parseFile(notes_file, level)
    if not notes:
        return
    print(f"OK:    {src_dir}")
    
    # se processou alguma nota, cria diretorio da musica no destino
    dest_dir = os.path.join(OUTPUT_ROOT, l, os.path.basename(src_dir))
    os.makedirs(dest_dir, exist_ok=True)

    # salva notas como .csv
    csv_path = os.path.join(dest_dir, "notes.csv")
    with open(csv_path, "w", newline="") as f:
        csv.writer(f).writerows(notes)

    # copia arquivos de audio relevantes para o diretorio destino
    audioExtractor.copyAudio(src_dir, dest_dir)

def main():
    # processa subdiretorios de INPUT_ROOT recursivamente
    for root,_,_ in os.walk(INPUT_ROOT):
        process_song(root)

if __name__ == "__main__":
    main()
