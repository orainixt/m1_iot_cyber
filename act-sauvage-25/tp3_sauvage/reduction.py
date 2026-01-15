def partition_to_binpack(litem):
    """_summary_

    Args:
        litem (list[int]): list of the item weights 

    Returns:
        _type_: _description_
    """
    S = sum(litem) 
    c = S // 2 
    return (litem, c, 2)

def sum_to_partition(litem,c):
    """same as above

    Args:
        litem (_type_): _description_
    """
    S = sum(litem) 
    new_item = 2 * c - S
    if new_item > 0:
        litem.append(new_item)

def sum_to_partition(litem,c): 
    """I didn't know if we should add the item if it's null 

    Args:
        litem (_type_): _description_
        c (_type_): _description_
    """
    S = sum(litem)
    litem.append(2*c - S) 
    return litem,c 

def sum_to_binpack(liste, c):
    liste, n = sum_to_partition(liste, c) 
    liste, capacite, k = partition_to_binpack(liste)
    return liste, capacite, k

def binpackopt1_to_binpack(litem,c):
    k = 1
    while not binpack(litem,k,c):  # we assume that binpack's implemented
        k+=1 
    return k