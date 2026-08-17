import stateBH
import servoBH

# valores default de cada pontuacao
SCORE_MISS = 0
SCORE_GOOD = 1
SCORE_PERFECT = 2
SCORE_SUSTAIN = 1 # pra fazer o sustain dar ponto constante // ainda n feito

MAX_ERROR_COUNT = 30
DEFAULT_ERROR_COUNT = MAX_ERROR_COUNT//2 # vida comeca no meio e pode subir ou descer <<< servo

# inicia sem valor, valores default setados pela funcao de reset
errorCount = None
totalScore = None
lastJudgement = None

# cria o servo de score com os valores maximo e minimo para normalizacao dos angulos e seta posicao inicial no meio
servoBH.create("score_servo", 0, MAX_ERROR_COUNT)
servoBH.set("score_servo", DEFAULT_ERROR_COUNT)

def reset():
    global totalScore, errorCount, lastJudgement
    lastJudgement = "Prepare-se !!!"
    totalScore = 0
    errorCount = DEFAULT_ERROR_COUNT
    servoBH.set("score_servo", errorCount)

def update(newScore):
    global lastJudgement, totalScore, errorCount
    
    # se errou e a contagem de erros esta ativada, incrementa
    if stateBH.countingErrors:
        if newScore == SCORE_MISS:
            errorCount += 1
        elif errorCount > 0:
            errorCount += -1

        servoBH.set("score_servo", errorCount)

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
