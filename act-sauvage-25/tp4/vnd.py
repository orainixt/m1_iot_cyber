import copy

from heuristic import minmax  
from random_ordo import computes_for_ordo 

def neighbours_swap(solution): 
    """
    return neighbours list using swap  
    solution is an ordo (same for function below) 
    """ 
    neighbours = [] 
    for i in range(len(solution)):
        for j in range(len(solution)): 
            if i == j: continue # lets save 1 picosecond 
            solution_new = copy.deepcopy(solution) #no aliasing 
            temp = solution_new[i]
            solution_new[i] = solution_new[j]
            solution_new[j] = temp 
            neighbours.append(solution_new) 
    return neighbours

def neighbours_insertion(solution): 
    """
    returns neighbours list using insertion 
    """
    neighbours = []
    for i in range(len(solution)):
        for j in range(len(solution)): 
            if i== j: continue
            solution_new = copy.deepcopy(solution) 
            i_index = solution_new.pop(i) 
            solution_new.insert(j,i_index)

            neighbours.append(solution_new)

    return neighbours


    


def vnd(instance,ordo=None): 
    if (ordo is None) :
        delay, ordo  = minmax(instance) 
    else:
        ordo = copy.deepcopy(ordo) 
        delay = computes_for_ordo(instance,ordo) 

    f_list = [neighbours_swap,neighbours_insertion]

    k = 0 # if k == 2 then both function are blocked || end of the algorithm 
    while (k < 2) :  # if there's more function to test replace that by len(f_list) 
        changed = False 
        f = f_list[k] 
        neighbours = f(ordo) 
        for neighbour in neighbours: 
            new_delay = computes_for_ordo(instance,neighbour) 
            if new_delay < delay :
                delay = new_delay
                ordo = neighbour
                changed = True 
                k = 0 # change alg as soon as there is an amelioration cuz O(swap) < O(insertion)
                break 
        if changed == False: 
            k+=1 # if k == 1 before, end the alg, otherwise check insertion  
    
    delay = computes_for_ordo(instance, ordo ) 
    return delay, ordo  



