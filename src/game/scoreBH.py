import stateBH

# valores default de cada pontuacao
SCORE_MISS = 0
SCORE_GOOD = 1
SCORE_PERFECT = 2
SCORE_SUSTAIN = 1

lastJudgement = "Prepare-se !!!"
errorCount = 0
totalScore = 0
MAX_ERROR_COUNT = 15

def reset():
    global totalScore, errorCount, lastJudgement
    lastJudgement = "Prepare-se !!!"
    totalScore = 0
    errorCount = 0

def update(newScore):
    global lastJudgement, totalScore, errorCount
    
    # se errou e a contagem de erros esta ativada, incrementa
    if stateBH.countingErrors:
        if newScore == SCORE_MISS:
            errorCount += 1
        elif errorCount > 0:
            errorCount += -1

    scoreStr = ""
    if newScore == SCORE_MISS:
        scoreStr = "Errou"
        if stateBH.countingErrors:
            print(f"{errorCount}/{MAX_ERROR_COUNT}", flush=True)

    elif newScore == SCORE_GOOD:
        scoreStr = 'Bom'
    else: # if new_score == SCORE_PERFECT:
        scoreStr = 'Perfeito'

    totalScore += newScore
    lastJudgement = f"{scoreStr}\nScore: {totalScore}"

    if stateBH.countingErrors and errorCount >= MAX_ERROR_COUNT:
        stateBH.runLost = True
