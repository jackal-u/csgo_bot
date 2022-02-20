from random import randint
from time import clock

# 打算用状态机来设置AI， 目前还在学习中。该文件夹为为无用代码
State = type("State", (object,), {})


# states and states code
class LightOn(State):
    def execute(self):
        print("light is on")


class LightOff(State):
    def execute(self):
        print("light is off")


# transition
class Transition(object):
    def __init__(self, to_state):
        self.to_state = to_state

    def execute(self):
        print("Transitioning to {}".format(self.to_state))


# SM
class FSM(object):
    def __init__(self, char):
        self.char = char
        self.states = {}
        self.transitions = {}

        self.cur_state = None
        self.trans = None

    def set_state(self, name):
        self.cur_state = self.states[name]

    def set_transition(self, name):
        self.trans = self.transitions[name]

    def execute(self):
        # 默认执行状态代码， 如果设置了tran,切换状态，执行trans代码
        if self.trans:
            self.trans.execute()
            self.set_state(self.trans.to_state)

            self.trans = None
        self.cur_state.execute()


class Bubble(object):
    def __init__(self):
        self.FSM = FSM(self)
        self.light_on = True


if __name__ == '__main__':
    bubble = Bubble()
    bubble.FSM.states["on"] = LightOn()
    bubble.FSM.states["off"] = LightOff()
    bubble.FSM.transitions["turn_on"] = Transition("on")
    bubble.FSM.transitions["turn_off"] = Transition("off")
    bubble.FSM.set_state("on")

    import time

    for i in range(20):
        time.sleep(0.1)
        if randint(0, 2):
            if bubble.light_on:
                bubble.FSM.set_transition("turn_off")

                bubble.light_on = False
            else:
                bubble.FSM.set_transition("turn_on")

                bubble.light_on = True
        bubble.FSM.execute()
