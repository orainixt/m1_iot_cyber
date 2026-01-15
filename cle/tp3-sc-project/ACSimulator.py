import sys
import argparse
import time
import threading
from sismic.interpreter import Interpreter
from sismic.io import import_from_yaml
from room_temp import Room 

from curses import wrapper

verbose = False

class StateMachineWithTick() :
    """

    This class simulates a statechart in which a periodic "tick" event
    is raised. This is one way to model the time that must be handled
    directly in the state chart.

    """
    def __init__(self, filename, tick_interval=1) :    
        # Load statechart from yaml file
        self.TICK_INTERVAL = tick_interval
        self.machine = import_from_yaml(filepath=filename)

        self.room1 = Room("Living room", 20); 
        self.room2 = Room("Bedroom", 20);
        Room.global_ext_temp = 20
        
        self.interpreter = Interpreter(self.machine, initial_context={ 'r1' : self.room1, 'r2' : self.room2 })
        # starts the internal clock of the interpreter
        self.interpreter.clock.time = 0
        self.interpreter.clock.start()

        # executes the machine
        self.steps = self.interpreter.execute()

        # starts a timer in the simulation that sends a tick event every TICK_INTERVAL second. 
        self.timer = threading.Timer(self.TICK_INTERVAL, self.tick_handler)
        self.timer.start()
        
        
    def print_machine_state(self) :
        # prints the statechart configuration on screen
        print('@ : --------------------')
        print("@ : Active States:", self.interpreter.configuration)
        
        if verbose : 
            for step in self.steps :
                for attribute in ['event', 'exited_states', 'transitions', 'entered_states', 'sent_events']:
                    print('@ :     {}: {}'.format(attribute, getattr(step, attribute)))
        print('@ : --------------------')


    def tick_handler(self) :
        self.send_and_execute('tick')
        self.timer = threading.Timer(self.TICK_INTERVAL, self.tick_handler)
        self.timer.start()


    def send_and_execute(self, evt) :
        self.interpreter.queue(evt)
        conf_before = self.interpreter.configuration
        self.steps = self.interpreter.execute()
        conf_after = self.interpreter.configuration
        if conf_before != conf_after :
            print('')
            for s in self.steps :
                if getattr(s, 'event') != None and 'tick' in str(getattr(s, 'event')) :
                    print("Tick event processed, time is now :", int(self.interpreter.clock.time))
            self.print_machine_state()

        self.interpreter.context['currTempLR'] = self.room1.getTemp()
        self.interpreter.context['currTempB']  = self.room2.getTemp()

        # Synchroniser la température désirée

        # I didn't saw that line so I made my own system to get desTemp 
        self.room1.setDesiredTemp(self.interpreter.context.get('desTempLR', self.room1.getDesiredTemp()))
        self.room2.setDesiredTemp(self.interpreter.context.get('desTempB', self.room2.getDesiredTemp()))
        self.room1.print()
        self.room2.print()

        
    def simulate(self) :
        # # Load statechart from yaml file
        # machine = import_from_yaml(filepath=filename)

        # # Create an interpreter for this statechart
        # interpreter = Interpreter(machine)
        
        # # Initialize the statechart, the machine goes into the initial state
        # steps = interpreter.execute() 

        # tick_handler(interpreter)

        while True :
            print('@ : accepted events', self.machine.events_for())
            # asks for input
            try :
                trigger = input ("@ : which event? (ctrl-c to exit, change <num> to change external temp) ").strip()
            except KeyboardInterrupt:
                self.timer.cancel()
                self.room1.stop()
                self.room2.stop()
                sys.exit(0)

            if trigger.startswith('change') :
                temp = int(trigger.split()[1])
                Room.change_ext_temp(temp)
            else :
                if trigger not in self.machine.events_for() :
                    print("@ {t} is not an accepted event".format(t=trigger))
                else:
                    # puts the event in the event queue
                    self.interpreter.queue(trigger)
                    # processes the event
                    self.steps = self.interpreter.execute()
                    self.print_machine_state()

