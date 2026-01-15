import matplotlib.pyplot as plt
import numpy as np
import sys
import time 

from random_ordo import read_instance, generate_random_ordo, computes_for_ordo
from heuristic import minmax 
from vnd import vnd 
from ils import ILS 

optimums = {
    'n100_15_b.txt' : 172995,
    'n100_16_b.txt' : 407703,
    'n100_17_b.txt' : 332804,
    'n100_18_b.txt' : 544838,
    'n100_19_b.txt' : 477684,
    'n100_35_b.txt' : 19114,
    'n100_36_b.txt' : 108293,
    'n100_37_b.txt' : 181850,
    'n100_38_b.txt' : 90440,
    'n100_39_b.txt' : 151701,
    'n100_40_b.txt' : 129728,
    'n100_41_b.txt' : 462324,
    'n100_42_b.txt' : 425875,
    'n100_43_b_txt' : 320537,
    'n100_44_b.txt' : 360193,
    'n100_85_b.txt' : 284,
    'n100_86_b.txt' : 66850,
    'n100_87_b.txt' : 84229,
    'n100_88_b.txt' : 55544,
    'n100_89_b.txt' : 54612,

    'n1000_1_b.txt' : 661265390,
    'n1000_2_b.txt' : 684518705
}


def test_one_file_ils(filename,lower_n,higher_n): 

    (instance,n) = read_instance(filename) 

    l_n = [3,5,10]
    l_k = [3,5,10] 

    matrix = [[0 for _ in range(len(l_k))] for _ in range(len(l_n))]
    matrix_results = [[0 for _ in range(len(l_k))] for _ in range(len(l_n))]

    for i,n in enumerate(l_n): 
        for j,k in enumerate(l_k): 
            print(f"Testing : n={n}, k={k}")  
            best_ordo,delay = ILS(instance,n,True,k,False) 
            matrix[i][j] = delay 
            matrix_results[i][j] = (delay, n,k) 

    plt.figure(figsize=(10,8))

    plt.imshow(matrix, cmap= 'RdYlGn_r', aspect='auto')

    cbar = plt.colorbar()
    cbar.set_label('Total Delay', rotation=270, labelpad=15)
    
    plt.xticks(ticks=range(len(l_k)), labels=l_k)
    plt.xlabel('Perturbation k')
    
    plt.yticks(ticks=range(len(l_n)), labels=l_n)
    plt.ylabel('Iterations number n')
    
    plt.title(f'ILS results for n and k (Instance: {filename})')

    plt.tight_layout()
    plt.savefig(f"ils_for_{filename}.png")
    plt.close()

    return matrix_results


def test_all_algs(filename):

    logs_algo = []

    t_start = time.time()
    instance, n = read_instance(filename) 
    t_end = time.time() 
    t_read = t_end - t_start
   
    print("read instance ok") 


    t_start = time.time() 

    random_ordo = generate_random_ordo(n) 
    random_delay = computes_for_ordo(instance, random_ordo) 

    t_end = time.time() 
    t_random = t_end - t_start

    logs_algo.append({  
        'algo' : 'random', 
        'time' : t_random, 
        'delay' : random_delay
    })

    print("random_ordo ok") 

    t_start = time.time() 
    delay_minmax, ordo_minmax = minmax(instance) 
    t_end = time.time() 
    t_minmax = t_end - t_start

    logs_algo.append({
        'algo' : 'minmax', 
        'time' : t_minmax, 
        'delay': delay_minmax
    })

    print("minmax ok") 
    
    t_start = time.time() 

    delay_vnd, ordo_vnd = vnd(instance) 

    t_end = time.time() 
    t_vnd = t_end - t_start

    logs_algo.append({
        'algo' : 'vnd', 
        'time' : t_vnd, 
        'delay': delay_vnd
    })

    print("vnd ok") 

    t_start = time.time()  

    ils_delay, ils_ordo = ILS(instance,5,True,10,False) 

    t_end = time.time() 
    t_ils = t_end - t_start
                
    logs_algo.append({
        'algo' : 'ils', 
        'time' : t_ils, 
        'delay': ils_delay
    })

    print("ils test ok") 

    print("*-------------------------------------------*")

    print(f"Delay value for random ordo : {random_delay}")

    print("*-------------------------------------------*")

    print(f"Delay value for minmax (heuristic) : {delay_minmax}")

    print("*-------------------------------------------*")

    print(f"Delay value for VND : {delay_vnd}") 

    print("*-------------------------------------------*")
    

    print(f"Final best value for ILS : {ils_delay}")

    print("*-------------------------------------------*")

    return logs_algo 



if __name__ == "__main__": 

    mes_fichiers = [
        'n100_15_b.txt', 
        'n100_35_b.txt', 
        'n100_85_b.txt'
    ]

    data_for_plot = []

    for fichier in mes_fichiers:
        if fichier not in optimums:
            continue      

    # I quit the loop to save time here
    # what's below should be for all 3 files. 
        

    fichier = 'n100_15_b.txt' 

    opt_val = optimums[fichier]
    print(f"Traitement de {fichier} (Optimum: {opt_val})...")


    logs_algo = test_all_algs(fichier) 


    for log in logs_algo:
        valeur_trouvee = log['delay']
        

        gap = ((valeur_trouvee - opt_val) / opt_val) * 100
        

        entry = {
            'algo': log['algo'],
            'time': log['time'],
            'gap': gap,
            'file': fichier
        }
        data_for_plot.append(entry)
        
        print(f"> {log['algo'].ljust(7)} : Gap = {gap:.2f}% | Temps = {log['time']:.4f}s")
            

    
    
