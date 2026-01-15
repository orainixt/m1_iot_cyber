def question3(tab): 
    tab = sorted(tab, key=lambda t: (t[0],-t[1],t[2]))
    res= []
    doublons = []
    for g,h,d in tab:
        if doublons and doublons[-1][0] == g and doublons[-1][1] == h:
            lg,lh,ld = doublons[-1]
            doublons[-1] = (lg,lh,max(ld,d)) 
        else:
            doublons.append((g,h,d))
    tab = doublons


    res.append((tab[0][0],0))
    res.append((tab[0][0],tab[0][1]))
    for i in range(len(tab) - 1): 
        ((x,y,z), (a,b,c)) = (tab[i],tab[i+1]) 
        if (z<a):
            res.append((z,y)) 
            res.append((z,0))
            res.append((a,0))
            res.append((a,b))
        else:
            if( z > a ): 
                if(y>b):
                    res.append((z,y))
                else :
                    res.append((a,y))
                    res.append((a,b))

            else:
                if(y<b):
                    res.append((a,b))
                else :
                    res.append((z,y))
    R = max(i for (_,_, i) in tab)
    last_x, last_h = res[-1] 
    if last_x < R:
        res.append((R, last_h))
        res.append((R,0))
    else:
        if last_h != 0:
            res.append((R,0))
    return res
         
        

def fusion_rec(l1,l2,h1=0,h2=0,last_h=0,i=0,j=0):

    if (i >= len(l1)): 
        return l2[j:]
    if (j >= len(l2)): 
        return l1[i:]

    abs1,y1 = l1[i]
    abs2,y2 = l2[j]

    if (abs1 < abs2) : 

        h1 = y1
        i+=1
        
        h = max(h1,h2)
        
        if (h == last_h) : 
            return fusion_rec(l1,l2,h1,h2,last_h,i,j) 
        else : 
            return [(abs1,h)] + fusion_rec(l1,l2,h1,h2,h,i,j)

    elif (abs1 > abs2): 

        h2 = y2
        j+=1 

        h = max(h1,h2)

        if (h == last_h) : 
            return fusion_rec(l1,l2,h1,h2,last_h,i,j) 
        else : 
            return [(abs2, h)] + fusion_rec(l1,l2,h1,h2,h,i,j)
    
    else : 

        h1 = y1
        h2 = y2
        
        i+=1
        j+=1

        h = max(h1,h2)

        return [(abs1, h)] + fusion_rec(l1,l2,h1,h2,h,i,j)

def transformBuildingIntoList(building):
    (g,h,d)= building
    return [(g,h),(d,0)] 


def skyline(buildings):
    if (len(buildings) == 0): 
        return [] 
    elif (len(buildings) == 1): 
        return transformBuildingIntoList(buildings[0]) 
    elif (len(buildings) == 2):
        l1,l2 = transformBuildingIntoList(buildings[0]),transformBuildingIntoList(buildings[1])
        return fusion_rec(l1,l2)
    else: 
        mid = len(buildings) // 2
        return fusion_rec(q5(buildings[mid:]),q5(buildings[:mid]))


def main(): 
    tab = [(98,41, 127) , (154, 16, 176), (195, 89, 231), (201,22,215), (167, 34,191)] 
    tab2= [(10, 6, 15),(10, 6, 18),(10, 6, 15),(10, 6, 20)]
    tab3= [(73 ,2 ,111),
    (86 ,83 ,122),
    (88 ,109, 123),
    (198, 97, 228),
    (133 ,60 ,163),
    (22, 71, 53),
    (83, 93, 93),
    (51 ,96 ,70),
    (100 ,20, 140),
    (69 ,70 ,87)]
    tab4=[(3,13,9), (1,11,5), (19,18,22), (3,6,7), (16,3,25), (12,7,16)]

    l1 = [(1,10), (5,6), (8,0), (10,8), (12,0)]
    l2 = [(2,12),(7,0), (9,4), (11,2), (14,0)] 

    l3 = l1+l2
    # l_final = skyline(l3)

    print(skyline(tab4))

    # print(question3(tab4))


if __name__ == "__main__":
    main() 


