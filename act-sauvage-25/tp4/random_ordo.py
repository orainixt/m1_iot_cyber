import sys
import random
from pathlib import Path

def read_instance(instance_path): 

    """
    read the instance in instance_path and returns it's list of tasks (p_i,w_i,d_i) for all i E n 
    """

    DATA_DIR = Path("SMTWP")
    FILE_DIR = DATA_DIR / instance_path
    
    with open(FILE_DIR,'r') as input_file: 
        data = input_file.readlines() 

    n = int(data[0])

    res = []

    for i in range(1,n+1): 
        stripped = data[i].strip()
        (p_i,w_i,d_i) = map(int, stripped.split())
        res.append([p_i,w_i,d_i])

    return (res,n) 


def computes_for_ordo(instance_data, ordo): 
    """
    returns the total delay for the instance described in instance_data with ordo the fixed scheduele 
    """
    time = 0
    delay = 0 
    for p in ordo:
        index = int(p)
        (p_i,w_i,d_i) = instance_data[index - 1]
        time += p_i 
        delay += (max(time - d_i, 0) * w_i)
    return delay

        

def generate_random_ordo(n): 
    """
    returns a random fixed scheduele for instance described in instance_path 
    """
    ordo = [x for x in range(1,n+1)]
    random.shuffle(ordo)
    return ordo




if __name__ == "__main__": 

    while (len(sys.argv) < 2): 
        print("Usage : python3 ordo.py <instance_file>\n--<instance_file> must be only the name of the file (e.g. 'n*_k_b.txt')")
        args = input("Please enter the instance file :\n") 
        sys.argv = sys.argv[0] + args

    instance_path = sys.argv[1]
    (instance_data,n) = read_instance(instance_path)

    random_ordo = generate_random_ordo(n) 

    delay = computes_for_ordo(instance_data,random_ordo) 
    print(f"Ordo : {random_ordo}\nInstance data : {instance_data}\n")
    print(f"Delay for this instance and this random ordo is : {delay} secondes.")



