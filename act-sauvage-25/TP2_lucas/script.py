import time 

##############################################################################################################
# NAIVE VERSION
##############################################################################################################

def get_config_value(config_list): 
    config_list = sorted(config_list)
    if (all(x>0 for x in config_list)): return (config_list[-1] +1) * (-1)
    if (all(x<0 for x in config_list)): return (config_list[-1]-1) *(-1)
    else: 
        i=0
        while(config_list[i] < 0):
            i+=1
        return (config_list[i-1] -1) * (-1)


def naive_rec_config(config):
    (r,c,x,y) = config
    if (r==0 or c==0):
        return 0
    if (r == 1 and c == 1):
        return 0
    config_values = [] 
    for i in range(1,r): 
        if i > x: 
            config_values.append(naive_rec_config((i,c,x,y))) 
        else: 
            config_values.append(naive_rec_config((r-i, c, x-i, y)))
    for j in range(1,c): 
        if j > y: 
            config_values.append(naive_rec_config((r,j,x,y)))
        else: 
            config_values.append(naive_rec_config((r,c-j,x,y-j)))

    return get_config_value(config_values)



##############################################################################################################
# DYNAMIC VERSION 
##############################################################################################################

def value_config(config,d={}):

    if config in d :
        return d[config] 
    
    successeurs = get_successeurs(config)

    if not successeurs: 
        return 0 
    
    values = [value_config(config_bis,d) for config_bis in successeurs] 


    if all(val>0 for val in values): 
        val = -1 - max(values) 
    else: 
        val = - max(val for val in values if val <= 0) + 1

    d[config] = val 

    return val 

     
    


def get_successeurs(config): 
    (c,r,x,y) = config
    successeurs_list = [] 

    for i in range(1,c): 
        if x < i: 
            successeurs_list.append((i,r,x,y))
        else: 
            if c-i > 0 and x-i >= 0: 
                successeurs_list.append((c-i,r,x-i,y))

    for j in range(1,r): 
        if y < j :
            successeurs_list.append((c,j,x,y))
        else: 
            if r-j > 0 and y-j >= 0: 
                successeurs_list.append((c, r-j, x,y-j))

    return successeurs_list


def get_symmetrics(config): 
    (c,r,x,y) = config
    symmetrics = [] 

    symmetrics.append(config)
    symmetrics.append((r,c,y,c-1-x))
    symmetrics.append((c,r,c-1-x,r-1-y))
    symmetrics.append((r,c,r-1-y,x))
    symmetrics.append((c,r,x,r-1-y))
    symmetrics.append((c,r,x,r-1-y))
    symmetrics.append((r,c,y,x)) 
    symmetrics.append((r,c,r-1-y,c-1-x))

    return symmetrics


def config_value_sym(config,d):

    if config in d: 
        return d[config] 

    for s in get_symmetrics(config): 
        if s in d: 
            return d[s] 
        
    successeurs = get_successeurs(config)

    if not successeurs: 
        return 0 
    
    values = [value_config(config_bis,d) for config_bis in successeurs] 


    if all(val>0 for val in values): 
        val = -1 - max(values) 
    else: 
        val = - max(val for val in values if val <= 0) + 1

    d[config] = val 

    return val 
        
    
    


##############################################################################################################
# MAIN
##############################################################################################################


def main(): 

    # print(valeur_config_dynamic(100,100,50,50))
    start = time.perf_counter()
    print(config_value_sym((100,100,50,50)))
    stop = time.perf_counter()
    print(stop - start)
    # pos_1 = (3,2,0,2)
    # pos_2 = (10,7,7,3) 
    # pos_3 = (10,7,5,3)
    # time1 = time.perf_counter()
    # print(naive_rec_config(pos_1))
    # time2= time.perf_counter()
    # print(f"For {pos_1} it took : {time2 - time1} seconds")
    # time3 = time.perf_counter()
    # print(naive_rec_config(pos_2))
    # time4 = time.perf_counter()
    # print(f"For {pos_2} it took : {time4 - time3} seconds")
    # time5 = time.perf_counter()
    # print(naive_rec_config(pos_3))
    # time6 = time.perf_counter() 
    # print(f"For {pos_3} it took : {time6 - time5} seconds") 


    

if __name__ == "__main__":
    main()