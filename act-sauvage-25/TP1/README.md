# Submission for the TP1 of ACT - SOYAH Amin - SAUVAGE Lucas

## Answers to questions 

### Q1.1
    1 : False
    2 : False
    3 : True    
    4 : False
    5 : False

### Q1.2
There is a few conditions needed for a polyline to be a skyline : 

    First rule : The height of the first and the last point should be 0 

    Second rule : For a given building A and the right next building B, if A x-axis equals B x-axis   then A height must be different from B height.
    
    Third rule : If A x-axis > B x-axis, then A height must be equals to B height
    
    Fourth and last rule : We cannot have three consecutive points with the same x-coordinate. 
    
    
### Q1.3
The line ```(1, 1)(5, 13)(9, 20)(12, 27)(16, 3)(19, 0)(22, 3)(25, 0)``` is represented by : 
```(1,0)(1,1)(5,1)(5,13)(9,13)(9,20)(12,20)(12,27)(16,27)(16,3)(19,3)(19,0)(22,0)(22,3)(25,3)(25,0)```

The transformation of the longer represantation into the smaller one is done by removing the first tuple and then every other one. 


### Q2  

This first pseudo-code only draw the skylines. 
```
entrée :(n,l) 
n : le nombre d''immeubles 
l : liste de triplets(gi,hi,di)
pour a allant de 0 à n :  
    pour i allant de 0 à l[a][1] : 
        tab[l[a][0]][i] = 1 
    pour j allant de l[0] à l[a][2] : 
        tab[j][l[a][1]] = 1 
    pour k allant de l[a][1] à 0 : 
        tab[l[a][2]][k] = 1 
return tab
```

This second draw the skyline and fill the tab with the actual buildings 

```
entrée :(n,l) 
n : le nombre d''immeubles 
l : liste de triplets(gi,hi,di)
pour a allant de 0 à n :  
    pour i allant de 0 à l[a][1] : 
        pour j allant de l[a][0] à l[a][2] :  
            tab[j][i]=1
```

The drawback of this method is the space because it requires to fill a tab with a lots of zeroes

The exact worst-case complexity for the first code his ```h*(d-g)``` which is equivalent to O(n²)
The worst-case complexity for the second is 0(n³+n²) which's equivalent to O(n³)

In conclusion, the first algorithm is better than the second.

### Q3

    For the complexity :

    Sorting: O(n log n) , where n = number of buildings
    Building skyline: O(n)
    Total: O(n log n) per insertion

    Correctness arguments:

    Sorting ensures we process buildings left to right
    Height descending order handles overlapping correctly
    End points closure ensures skyline ends at ground level
    2-by-2 comparison captures height changes between buildings

### Q4 

To analyse complexity, we need to examinate the recursive calls. 
Indeed, the comparaisons and affectations are in O(1) so we can let them beside.

Regarding of the situation, we have two possible recursive calls 

The less complex one : ```fusion_rec(l1,l2,h1,h2,last_h,i,j)```. 
Here the complexity is (O(1) + O(0)) * O(recursive).

The other one is : ```[(abs1,h)] + fusion_rec(l1,l2,h1,h2,h,i,j)```. 
There's just one difference : We add a new point to the list. That's also in O(1). 
As a result, the complexity here is (O(1) + O(1)) * O(recursive). 

The O(recursive) is quite simple, it's just the total number of points, which is O(len(l1) + len(l2)) which is equivalent to O(n) 

Finnaly, this recursive algorithm is in O(n) Proof : (O(1) * O(n) = O(n)).  


### Q5
we can deduce the expression of the complexity of the recurrence in order to use the master theorem. 
We have : 2*C(n/2) + O(n). Here a equals b equals 2 and d equals 1. 
As log_b(a) = 1 = d so we can use the second case of the master theorem which is : 
    C(n) = O(n^d * log(n)) = O(n*log(n))
