import random
import sys 
import ast 

def verif(x,c,k,aff): 
    """
    returns True if the items affectation respect maximum capacity
    Args:
        x (list): list of items weight 
        c (int): capacity of a bag (same for each here)
        k (int): the number of bags
        aff (func): function used to affect item i into bag j 
    """
    for j in range(1,k+1): 
        total = sum(x[i] for i in range(len(x)) if aff[i] == j)
        if total > c: 
            return False
    return True

def generate_random_certif(n,k): 
    aff = []
    for _ in range(n): 
        random_bag = random.randint(1,k) 
        aff.append(random_bag)
    return aff

def generate_via_lists(n,k): 
    return [random.randint(1,k) for _ in range(n)]



def verif_all_certif(x,c,k): 

    n = len(x)

    certif = [1] * n 
    certif_max = [k] * n 

    while certif != certif_max: 

        if verif(x,c,k,certif): return (True,certif) 

        i = 0
        while i < n : 
            if certif[i] < k : 
                certif[i] += 1
                break 
            else: 
                certif[i] = 1 
                i+=1 

    if verif(x,c,k,certif): return (True,certif) 
    return (False,None) 



def main(x,c, mode, k): 

    if mode == "-ver": 

        usr_in = input(f"Please enter a certificate : \n--HELP--\n[4,3,2] puts item1 in bag4, item2 in bag 3 etc.\nThere's {len(x)} items, therefore :\nMinimal certificate's {[1]*len(x)} || Maximum's {[k] * len(x)}\n")
        usr_certif = ast.literal_eval(usr_in)

        print(f"The user certificate {"is valid." if verif(x,c,k,usr_certif) else "is not valid."}")

    if mode == "-nd": 

        certif = generate_via_lists(len(x),k) 
        print(f"The random certif was {certif} and {"is valid." if verif(x,c,k,certif) else "is not valid."}")

    if mode == "-exh": 

        if (len(x) > 15) : 
            print("I can't let you test with that amount of items (you'll be dead before it computes !)")
            return 
        
        if (len(x) > 10) :
            ok_if_slow = input("Are you sure you want to test ? It might take minutes/hours (y/n):\n")
            if (ok_if_slow == "n"): 
                return 
        
        (_,certif) = verif_all_certif(x,c,k) 

        print(f"Certificate found ! : {certif}" if certif else "No certificate found :(")

    



if __name__ == "__main__":

    
    while (len(sys.argv)) <= 1 :
        print('Usage : python3 <py_file> <file> <mode> <nb_bag>')
        print('Available files to test :\nbinpackinstance.txt && fastbinpackinstance.txt (for exhaustive exploration)')

        args = input("Please enter parameters (Separeted)\n").split() 
        sys.argv = [sys.argv[0]] + args 

    files = sys.argv[1] 
    mode = sys.argv[2] 
    k = int(sys.argv[3]) 

    with open(files, 'r', encoding='utf-8') as input_file: 
        n = int(input_file.readline().strip()  )
        x = input_file.readline().strip() 
        c = int(input_file.readline().strip()) 

        x = list(map(int,x.split())) 

    main(x,c,mode,k)







