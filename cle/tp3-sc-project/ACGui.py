import sys
import argparse

import tkinter as tk
import ACSimulator as ac
import room_temp as room

class App(tk.Frame):
    def __init__(self, master, sm):
        super().__init__(master)

        self.is_on_1 = False
        self.is_on_2 = False

        self.machine = sm
        self.machine.interpreter.bind(self.event_handler)
        self.machine.room1.set_display(self)
        self.machine.room2.set_display(self)

        self.des_temp_1 = self.machine.room1.getTemp()
        self.des_temp_2 = self.machine.room2.getTemp()

        self.init_widgets()



    def init_widgets(self) :
        self.PAD = 2
        self.grid()
        
        ###
        ### AC Living Room
        ###
        #self.label_room = tk.Label(self, text="Living Room")
        self.lf_room = tk.LabelFrame(self, text='Living Room')
        
        self.button_on_off = tk.Button(self.lf_room, text="On/Off", command=self.on_off_fun)
        self.button_next = tk.Button(self.lf_room, text="Next", command=self.next_fun)
        self.button_plus = tk.Button(self.lf_room, text="+", command=self.plus_fun)
        self.button_minus = tk.Button(self.lf_room, text="-", command=self.minus_fun)
        self.label_on_off = tk.Label(self.lf_room, text="Off")
        self.label_next = tk.Label(self.lf_room, text="---")
        self.label_state = tk.Label(self.lf_room, text="State: ")
        self.label_state_value = tk.Label(self.lf_room, text="---")
        self.label_desired_temp = tk.Label(self.lf_room, text="Desired Temp:")
        self.label_desired_temp_value = tk.Label(self.lf_room, text=str(self.des_temp_1))
        self.label_current_temp = tk.Label(self.lf_room, text="Current Temp:")
        self.label_current_temp_value = tk.Label(self.lf_room, text="20")

        ###
        ### AC Bedroom
        ###
        self.bf_room = tk.LabelFrame(self, text='Bedroom')
        
        self.button_on_off_2 = tk.Button(self.bf_room, text="On/Off", command=self.on_off_fun_2)
        self.button_next_2 = tk.Button(self.bf_room, text="Next", command=self.next_fun_2)
        self.button_plus_2 = tk.Button(self.bf_room, text="+", command=self.plus_fun_2)
        self.button_minus_2 = tk.Button(self.bf_room, text="-", command=self.minus_fun_2)
        self.label_on_off_2 = tk.Label(self.bf_room, text=f"{str(self.is_on_1)}")
        self.label_next_2 = tk.Label(self.bf_room, text="---")
        self.label_state_2 = tk.Label(self.bf_room, text="State: ")
        self.label_state_value_2 = tk.Label(self.bf_room, text="---")
        self.label_desired_temp_2 = tk.Label(self.bf_room, text="Desired Temp:")
        self.label_desired_temp_value_2 = tk.Label(self.bf_room, text=str(self.des_temp_2))
        self.label_current_temp_2 = tk.Label(self.bf_room, text="Current Temp:")
        self.label_current_temp_value_2 = tk.Label(self.bf_room, text="20")

        self.ex_frame = tk.Label(self, text='Extern')
        
        self.label_ext_temp = tk.Label(self.ex_frame, text="Ext. temp:")
        self.change_temp = tk.Entry(self.ex_frame)
        self.ext_temp = tk.StringVar()
        self.ext_temp.set('20')
        self.change_temp["textvariable"] = self.ext_temp
        self.change_temp.bind('<Key-Return>', self.change_temp_fun)

        # Positions
        self.lf_room.grid        (row=0, column=0, padx=self.PAD, pady=self.PAD)
        self.bf_room.grid        (row=0, column=1, padx=self.PAD, pady=self.PAD)
        self.ex_frame.grid       (row=1, column=0, padx=self.PAD, pady=self.PAD)
        
        self.button_on_off.grid       (row=0, column=0, padx=self.PAD, pady=self.PAD)
        self.label_on_off.grid        (row=0,column=1, padx=self.PAD, pady=self.PAD)        
        self.button_next.grid         (row=1, column=0, padx=self.PAD, pady=self.PAD)
        self.label_next.grid          (row=1, column=1, padx=self.PAD, pady=self.PAD)
        self.label_state.grid         (row=2, column=0, padx=self.PAD, pady=self.PAD)
        self.label_state_value.grid   (row=2, column=1, padx=self.PAD, pady=self.PAD)
        self.button_plus.grid         (row=3, column=0, padx=self.PAD, pady=self.PAD)
        self.button_minus.grid        (row=3, column=1, padx=self.PAD, pady=self.PAD)
        self.label_desired_temp.grid      (row=4, column=0, padx=self.PAD, pady=self.PAD)    
        self.label_desired_temp_value.grid(row=4, column=1, padx=self.PAD, pady=self.PAD)    
        self.label_current_temp.grid      (row=5, column=0, padx=self.PAD, pady=self.PAD)    
        self.label_current_temp_value.grid(row=5, column=1, padx=self.PAD, pady=self.PAD)    

        self.button_on_off_2.grid       (row=0, column=0, padx=self.PAD, pady=self.PAD)
        self.label_on_off_2.grid        (row=0, column=1, padx=self.PAD, pady=self.PAD)        
        self.button_next_2.grid         (row=1, column=0, padx=self.PAD, pady=self.PAD)
        self.label_next_2.grid          (row=1, column=1, padx=self.PAD, pady=self.PAD)
        self.label_state_2.grid         (row=2, column=0, padx=self.PAD, pady=self.PAD)
        self.label_state_value_2.grid   (row=2, column=1, padx=self.PAD, pady=self.PAD)
        self.button_plus_2.grid         (row=3, column=0, padx=self.PAD, pady=self.PAD)
        self.button_minus_2.grid        (row=3, column=1, padx=self.PAD, pady=self.PAD)
        self.label_desired_temp_2.grid      (row=4, column=0, padx=self.PAD, pady=self.PAD)    
        self.label_desired_temp_value_2.grid(row=4, column=1, padx=self.PAD, pady=self.PAD)    
        self.label_current_temp_2.grid      (row=5, column=0, padx=self.PAD, pady=self.PAD)    
        self.label_current_temp_value_2.grid(row=5, column=1, padx=self.PAD, pady=self.PAD)    


        self.label_ext_temp.grid          (row=0, column=0, padx=self.PAD, pady=self.PAD)
        self.change_temp.grid             (row=0, column=1, padx=self.PAD, pady=self.PAD)        

    def on_off_fun(self) :
        print("Button on/off_1 pressed")
        self.machine.send_and_execute('on_off_1')
        self.is_on_1 = not self.is_on_1
        self.label_on_off.configure(text="On" if self.is_on_1 else "Off")
        

    def on_off_fun_2(self) :
        print("Button on/off_2 pressed")
        self.machine.send_and_execute('on_off_2')
        self.is_on_2 = not self.is_on_2
        self.label_on_off_2.configure(text="On" if self.is_on_2 else "Off")
        
    def next_fun(self) :
        print("Button next_1 pressed")
        self.machine.send_and_execute('next_1')


    def next_fun_2(self) :
        print("Button next_2 pressed")
        self.machine.send_and_execute('next_2')
        
    def plus_fun(self):
        print("Button plus_1 pressed")
        self.machine.send_and_execute('plus_1')
        self.des_temp_1 += 1 
        self.label_desired_temp_value.configure(text=str(self.des_temp_1))
        self.machine.room1.setDesiredTemp(self.des_temp_1)

    def plus_fun_2(self) :
        print("Button plus_2 pressed")
        self.machine.send_and_execute('plus_2')
        self.des_temp_2 += 1 
        self.label_desired_temp_value_2.configure(text=str(self.des_temp_2))
        self.machine.room2.setDesiredTemp(self.des_temp_2)

    def minus_fun(self) :
        print("Button minus_1 pressed")
        self.machine.send_and_execute('minus_1')
        self.des_temp_1 -= 1
        self.label_desired_temp_value.configure(text=str(self.des_temp_1))
        self.machine.room1.setDesiredTemp(self.des_temp_1)

    def minus_fun_2(self) :
        print("Button minus_2 pressed")
        self.machine.send_and_execute('minus_2')
        self.des_temp_2 -= 1
        self.label_desired_temp_value_2.configure(text=str(self.des_temp_2))
        self.machine.room2.setDesiredTemp(self.des_temp_2)


        
    def change_temp_fun(self, evt) :
        print("The current external temperature is now:", self.ext_temp.get())
        room.Room.change_ext_temp(float(self.ext_temp.get()))
        
    def display_curr_temp(self, n, t) :
        if n == "Living room" : self.label_current_temp_value["text"]   = str(t)
        if n == "Bedroom" :     self.label_current_temp_value_2["text"] = str(t)
        
    def on_closing(self) :
        print('Exiting')
        self.machine.timer.cancel()
        self.machine.room1.stop()
        self.machine.room2.stop()
        sys.exit(0)

    def event_handler(self, event):
        print('Event {} received from the state machine !'.format(event))
        if event.name == 'display_on' :
            self.label_on_off["text"] = event.value
        if event.name == 'display_des_temp' :
            self.label_desired_temp_value["text"] = event.value
        
    def updateTempLabel(self): 
         self.label_desired_temp.config(text=str(self.des_temp_1))
            
parser = argparse.ArgumentParser(
    prog='AC GUI simulator',
    description='Simulates a StateChart specified in a YAML. See https://sismic.readthedocs.io/')
      
parser.add_argument('filename')
parser.add_argument('-v', '--verbose', action='store_true')

args = parser.parse_args()
verbose = args.verbose
sm = ac.StateMachineWithTick(args.filename)


root = tk.Tk()
myapp = App(root, sm)
myapp.master.title("AC GUI")
myapp.master.maxsize(1200, 720)
root.protocol("WM_DELETE_WINDOW", myapp.on_closing)

myapp.mainloop()



    
    
#    sm.simulate()




        

