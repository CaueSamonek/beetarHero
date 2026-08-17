from gpiozero import Button

# flag de 'modo facil', faz com que erros nao sejam contados
countingErrors = True

# caso o jogador morra por ser ruim de mais
runLost = False

def reset():
    global runLost, endGame
    runLost = False
    endGame = False

# setup de botao e estado especial
# se estiver no menu, permite trocar o lado das cores (modo canhoto)
# se estiver in game, mata a run, retornando ao menu
onMenu = True
endGame = False
sideSwitch = False
sideSwitchChanged = False

def sideSwitchPressed():
    global sideSwitch, sideSwitchChanged, endGame

    # se apertou o botao e nao esta no menu
    if not onMenu:
        endGame = True
        return

    # atualiza estado
    sideSwitch = not sideSwitch
    sideSwitchChanged = True 

# setup de pinagem (gpio1) e callback
button = Button(1, pull_up=True, bounce_time=0.1)
button.when_pressed = sideSwitchPressed
