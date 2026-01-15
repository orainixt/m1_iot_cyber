import random 
from random_ordo import computes_for_ordo
from heuristic import minmax
import copy 
from vnd import vnd


def perturbation(ordo,n,more):
    """
    I didn't use an historic parameter 
    """
    ordo_copy = copy.deepcopy(ordo)
    if more : n = n * 2 
    for _ in range(n): 
        i = random.randint(0,len(ordo_copy)-1) 
        j = random.randint(0,len(ordo_copy)-1) 
        ordo_copy[i],ordo_copy[j]=ordo_copy[j],ordo_copy[i]
    return ordo_copy


# not used 
def accept(instance,old_ordo,ordo,accept,best_ordo): 
    if accept: 
        return ordo 
    else: 

        if ordo_delay < (1+epsilon) * old_ordo_delay:
            return ordo 
        return old_ordo
    


def ILS(instance,n,check,k,more):

    # minmax already used in vnd  
    # INIT 
    delay, best_ordo = vnd(instance)

    ordo = copy.deepcopy(best_ordo)
    best_delay = delay 

    for _ in range(n):     
        old_ordo = copy.deepcopy(ordo) 
        old_delay = delay 
        # PERTURBATION 
        ordo = perturbation(ordo,k,more)
        # LOCAL BASE SEARCH
        ordo_delay,ordo = vnd(instance,ordo)
        # ACCEPTATION : Does nothing if true Else  

        if ordo_delay < best_delay: 
            best_ordo = copy.deepcopy(ordo)
            best_delay = ordo_delay

        better = True 

        if check: 
            epsilon = 1e-6
            if ordo_delay > (1+epsilon) * old_delay: 
                better = False 

        if better:   # for the acceptation logic, because if I did it just above it would not work when check == false 
            delay = ordo_delay
        else: 
            ordo = old_ordo 
            delay = old_delay


    return best_delay,best_ordo 





    
