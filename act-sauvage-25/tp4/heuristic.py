import sys
from random_ordo import read_instance, computes_for_ordo 

def minmax(instance): 

    temps = 0 
    ordo = []
    instance_indexed = [[p,w,d,i+1] for i,(p,w,d) in enumerate(instance)]

    while (len(instance_indexed) > 0): 

        best = float('inf')

        for p,w,d,i in instance_indexed:
 
            best_choice = max(temps+p,d)
            weighted = best_choice / w 
            if weighted < best : 
                best = weighted  
                best_task = [p,w,d,i]



        p,w,d,i = best_task
        temps += p 
        ordo.append(i)
        instance_indexed.remove(best_task)

    delay = computes_for_ordo(instance,ordo) 
    return (delay,ordo)  

        


if __name__ == "__main__": 
    while (len(sys.argv) < 2): 
        print("Usage : python3 ordo.py <instance_file>\n--<instance_file> must be only the name of the file (e.g. 'n*_k_b.txt')")
        args = input("Please enter the instance file :\n") 
        sys.argv = sys.argv[0] + args

    instance_path = sys.argv[1]
    
    instance_data  = read_instance(instance_path)
    print(minmax((instance_data))) 

