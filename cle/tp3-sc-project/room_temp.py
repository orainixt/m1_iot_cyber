import time
import threading



class Room() :
    global_ext_temp = 0
    
    def __init__(self, name, init_temp) :
        self.curr_temp = init_temp
        self.desired_temp = init_temp
        self.name = name
        
        self.ac_power = 0
        self.k1 = 0.02
        self.k2 = 0.25
        self.timer = threading.Timer(1, self.run)
        self.timer.start()
        self.display = None

        

    def run(self) :
        self.curr_temp = self.curr_temp - (self.curr_temp - Room.global_ext_temp) * self.k1 + self.ac_power * self.k2
        self.timer = threading.Timer(1, self.run)
        self.timer.start()
             
    def ac_on(self, power) :
        self.ac_power = power
        
    def ac_off(self) :
        self.ac_power = 0

    @staticmethod
    def change_ext_temp(ext_temp) :
        Room.global_ext_temp = ext_temp

    def stop(self) :
        self.timer.cancel()

    def print(self) :
        print('{} temp: {:.2f} \t| External temp : {}'.format(self.name, self.curr_temp,
                                                              Room.global_ext_temp))
        if self.display :
            self.display.display_curr_temp(self.name, '{:.2f}'.format(self.curr_temp))

    def set_display(self, d) :
        self.display = d

    def setDesiredTemp(self, temp): 
        self.desired_temp = temp

    def getDesiredTemp(self):
        return self.desired_temp 
    
    def getTemp(self): 
        return self.curr_temp
        
