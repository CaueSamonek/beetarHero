import ledsBH
import configBH
import stateBH
import scoreBH
import filesBH
import inputBH

class NoteEvent:
    def __init__(self, time_ms, mask, length_leds):
        self.time_ms = time_ms
        self.mask = mask
        self.length_leds = length_leds

class ActiveNote:
    def __init__(self):
        self.active = False
        self.start_time_ms = 0
        self.length_leds = 0
        self.missed = False

class HeldNote:
    def __init__(self):
        self.note = None
        self.start_head = 0

    def clear(self):
        self.note = None
        self.start_head = 0

held = [HeldNote() for _ in range(configBH.NUM_LANES)]
active_notes = [[ActiveNote() for _ in range(configBH.LEDS_PER_LANE)]
                                            for _ in range(configBH.NUM_LANES)]

def loadNotes(music_path):
    notes = []

    for time_ms, lane, length_leds in filesBH.readNotes(music_path):
        if lane == 0:
            continue
        notes.append(NoteEvent(time_ms, lane-1, length_leds))
        #notes.append(NoteEvent(time_ms, lane, length_leds))

    return notes

def spawnNote(lane, now_ms, length_leds):
    for note in active_notes[lane]:
        if note.active:
            continue

        note.active = True
        note.start_time_ms = now_ms
        note.length_leds = length_leds
        note.missed = False
        return


def despawnNote(lane, note):
    note.active = False
    if held[lane].note is note:
        held[lane].clear()



def updateNotes(now_ms):
    for lane in range(configBH.NUM_LANES):
        lane_hold = held[lane]

        for note in active_notes[lane]:
            if not note.active:
                continue

            elapsed_ms = now_ms - note.start_time_ms

            head = int(elapsed_ms * configBH.NOTE_SPEED + 0.5)
            tail = head - note.length_leds + 1

            if head >= configBH.LEDS_PER_LANE and not note.missed:
                note.missed = True
                scoreBH.update(scoreBH.SCORE_MISS)

            draw_head = head
            draw_tail = tail

            if lane_hold.note is note:
                consumed = max(0, head - lane_hold.start_head)

                #if input.BH.buttons[lane]:
                #   consumed = 0

                draw_head = head - consumed
                draw_tail = draw_head - note.length_leds + 1 + consumed

                if consumed >= note.length_leds:
                    despawnNote(lane, note)
                    continue

            if tail >= configBH.LEDS_PER_LANE:
                despawnNote(lane, note)
                continue

            for pos in range(draw_tail, draw_head + 1):
                if 0 <= pos < configBH.LEDS_PER_LANE:
                    ledsBH.setColor(lane, pos)

        ledsBH.setColor(lane, configBH.HIT_LINE, ledsBH.COLOR_WHITE)


def onKeyPress(lane, now_ms):
    if held[lane].note is not None:
        scoreBH.update(scoreBH.SCORE_MISS)
        return

    for note in active_notes[lane]:
        if not note.active:
            continue

        elapsed_ms = now_ms - note.start_time_ms
        head = int(elapsed_ms * configBH.NOTE_SPEED + 0.5)
        if head not in (configBH.HIT_LINE, configBH.HIT_LINE - 1):
            continue

        scoreBH.update(scoreBH.SCORE_PERFECT if head == configBH.HIT_LINE else scoreBH.SCORE_GOOD)

        if note.length_leds == 1:
            note.active = False
        else:
            held[lane].note = note
            held[lane].start_head = configBH.HIT_LINE

        return

    scoreBH.update(scoreBH.SCORE_MISS)

def onKeyRelease(lane):
    if held[lane].note is not None:
        scoreBH.update(scoreBH.SCORE_MISS)

pressed = [False]*configBH.NUM_LANES
def updateInput(now_ms):
    for i in range(configBH.NUM_LANES):
        # inverte input se estiver no estado invertido
        lane = configBH.NUM_LANES - 1 - i if stateBH.sideSwitch else i

        if inputBH.buttons[i] and not pressed[i]:
            onKeyPress(lane, now_ms)
            pressed[i] = True

        elif not inputBH.buttons[i] and pressed[i]:
            onKeyRelease(lane)
            pressed[i] = False
