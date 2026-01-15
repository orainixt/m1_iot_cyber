from script import config_value_sym
import sys


def play_one_turn(config,d,which_turn): 

    (c,r,x,y) = config

    actual_value = config_value_sym(config,d)

    turn = 0 if which_turn else 1

    print("*--------------------------------------------------------------------------------*") 
    print(f"Its Player {turn} turn")
    print(f"The config was {config} and it's value was {actual_value}")

    print("*--------------------------------------------------------------------------------*")     
    print("First, please choose if you want to cut a row or a column ?")
    which_side = input("Please enter C for columns and R for rows\n") 

    if which_side != "C" and which_side != "R": 
        print("Please enter an appropriate letter : C or R\n")
        play_one_turn(config)

    if which_side == "C" : 
        print("Please enter the number of columns you want to trim :") 
        col = input()
        col = int(col)

        if x < col:
            new_config = (col,r,x,y)
        else: 
            new_config = (c-col, r,x-col,y) 

        new_value = config_value_sym(new_config,d) 
    
    else: 
        print("Please enter the number of rows you want to trim :") 
        row = input()
        row = int(row)

        if y < row:
            new_config = (c,row,x,y)
        else: 
            new_config = (c, r-row,x,y-row) 

        new_value = config_value_sym(new_config,d)   

    print("*--------------------------------------------------------------------------------*")     
    print(f"Now the configuration is {new_config} and the new value's {new_value}") 
    print("Next turn ...\n")
    print("*--------------------------------------------------------------------------------*") 

    return (new_config,new_value)

def play(starting_config):

    which_turn = True
    d = {}
    (m,n,x,y) = starting_config


    print("*--------------------------------------------------------------------------------*") 
    print("Welcome to the Chocolate Game !")
    print("*--------------------------------------------------------------------------------*") 
    print(f"You choosed to play with {m} columns and {n} rows.\nThe dead cell is at coordinate ({x},{y})") 

    config = starting_config

    while True: 

        (new_c,new_v) = play_one_turn(config,d,which_turn) 
        which_turn = not which_turn 
        config = new_c 

        if new_v == 0: 
            turn = 1 if which_turn else 0
            print("*--------------------------------------------------------------------------------*") 
            print(f"Player {turn} won !!")
            print("*--------------------------------------------------------------------------------*") 
            return 
        
def main():

    if (len(sys.argv) != 5): 
        print("Usage : python3 game.py <m> <n> <x> <y>")
        return

    if (len(sys.argv)>=5): 
        m = int(sys.argv[1])
        n = int(sys.argv[2]) 
        x = int(sys.argv[3]) 
        y = int(sys.argv[4])

    starting_config = (m,n,x,y)

    play(starting_config)

        
if __name__ == "__main__":
    main()



    
        
