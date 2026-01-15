from room_temp import Room

from sismic.io import import_from_yaml
from sismic.interpreter import Interpreter

class Test: 
    def __init__(self,yaml): 
        self.machine = import_from_yaml(filepath=yaml) 
        self.room1 = Room("LivingRoom",20) 
        self.room2 = Room("BedRoom",20) 
        Room.global_ext_temp = 20 

        self.interpreter = Interpreter(self.machine, initial_context={'r1' : self.room1, 'r2' : self.room2}) 


        self.steps = self.interpreter.execute()


    def test_sequence(self):
        all_states = set([
            "ALARM_OFF", "ALARM_ON", "ALARM_DANGER",
            "DAY", "NIGHT",
            "OFF_LR", "OFF_B", "ON_LR", "ON_B",
            "Manuel_LR", "Manuel_B",
            "Pause_M_LR", "Pause_M_B", "Cooling_M_LR", "Cooling_M_B",
            "Heating_M_LR", "Heating_M_B",
            "Automatique_LR", "Automatique_B",
            "Pause_A_LR", "Pause_A_B",
            "Heating_A_LR", "Heating_A_B",
            "Cooling_A_LR", "Cooling_A_B"
        ])

        reached_states = set()

        # BASICS EVENTS
        events = [
            "on_off_1", "on_off_2",
            "next_1","next_1","next_1", 
            "next_2", "next_2","next_2"
            "plus_1", "minus_1", "plus_2", "minus_2",
            "time_10pm", "time_7am"
        ]

        for event in events:
            self.interpreter.queue(event)
            self.steps = self.interpreter.execute()
            for state in self.interpreter.configuration:
                reached_states.add(state)

        # AUTOMATIC MODE
        for _ in range(3):
            for event in ["plus_1","plus_1","plus_1","plus_2","plus_2", "minus_1", "minus_2"]:
                self.interpreter.queue(event)
                self.steps = self.interpreter.execute()
                for _ in range(2):
                    self.interpreter.queue('tick')
                    self.steps = self.interpreter.execute()
                reached_states.update(self.interpreter.configuration)

        #ALARM DANGER
        self.room1.curr_temp = 45
        self.room2.curr_temp = 45
        self.interpreter.queue('alarm_triggered')
        self.steps = self.interpreter.execute()
        for state in self.interpreter.configuration:
            reached_states.add(state)

        for _ in range(6):
            self.interpreter.queue('tick')
            self.steps = self.interpreter.execute()
            for state in self.interpreter.configuration:
                reached_states.add(state)

        self.interpreter.queue('on_off_1')
        self.interpreter.queue('on_off_2')
        self.steps = self.interpreter.execute()
        for state in self.interpreter.configuration:
            reached_states.add(state)
    

        missing = all_states - reached_states
        assert not missing, f"Unreached states: {missing}"
        print("\n\n*----------------------------------------------------*\nTest result :")
        print("\nAll states reached!!\n")
        print("*----------------------------------------------------*")

        return 



if __name__ == "__main__":
    test = Test("cu.yaml")
    test.test_sequence() 
    print("I'm sorry I tried to stop Interpreter clock (or thread ?) but can't find a way\nPlease press Crtl + C to exit testing")


