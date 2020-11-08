from FSM.ClassStateMachine import StateMachine

def StartState(text):
    text = text.lower()
    if 'food' in text:
        newState = 'Food'
    else:
        newState = 'Finish'
    return (newState, text)

def FoodState(text):
    text = text.lower()
    if 'food' in text:
        newState = 'ChoiceFood'
    else:
        newState = 'error'
    return (newState, text)

def ChoiceFood(text):
    text = text.lower()
    if 'pasta' in text:
        print(f'Your pasta please')
        newState = 'Finish'
    else:
        print(f'Your {text} please')
        newState = 'Finish'
    return (newState, text)

if __name__== "__main__":
    m = StateMachine()
    m.add_state("Start", StartState)
    m.add_state("Food", FoodState)
    m.add_state("ChoiceFood", ChoiceFood)
    m.add_state("Finish", None, end_state=1)
    m.add_state("error", None, end_state=1)
    m.add_state("no food", None, end_state=1)
    m.set_start("Start")
    m.run("start")
    m.run("food is my life")
    m.run("pasta")

