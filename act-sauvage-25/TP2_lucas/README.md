# Dynamic Programming -- ACT 2025-2026 -- Lucas Sauvage

## Answers to question 

### Q1 

It needs 4 coordinates :

    m : nb of columns 
    n : nb of rows 
    x : x-coordinate of the deadly case 
    y : y-coordinate of the deadly case



### Q2 

        +4
       / \
      /\  \
    +2 -3 +2

        -3
       / \
      +2  +2


        +2
       / \
      -1  +2 
        

### Q3

From a configuration the player has 2 choices. Either he cut vertically (columns trim) or horizontally (rows trim). The dead cell must be in the trimmed chocolate bar.

To have the list of all successors, we need to compute all the possible action of the player. 

To do so, we can loop over the number of columns and the number of row (in 2 distincts loops). Each step we need to add the successor config to the successors list. 

In each loop there's a condition that checks if the dead cell is still in the chocolate bar.

### Q4 

$\forall value \in \mathbb{successors\_list}$, on définit :

$$
best\_value =
\begin{cases}
(max(list) +1) * (-1) & \text{if } \forall value, value \ge 0, \\
(max(list) -1) * (-1) & \text{else.}
\end{cases}
$$

### Q5

### Q6

```bash
lucas@gerard:~/Desktop/m1/act-soyah-sauvage-2025/TP2_lucas$ python3 script.py 
3
For (3, 2, 0, 2) it took : 0.00010014700001192978 seconds
11
For (10, 7, 7, 3) it took : 182.83371382400014 seconds
15
For (10, 7, 5, 3) it took : 355.20465524299993 seconds
lucas@gerard:~/Desktop/m1/act-soyah-sauvage-2025/TP2_lucas$ 
```

### Q7 

The difference is what makes the algorithm ineffective. At each step we need to compute all the different configuration relative to the config given in parameters. 

This grows exponetially, which lead the function compute a lot and a lot of different config, which makes it extremly slow for non-trivial configs.

The algorithm's complexity is exponential. For a config with m columns and n rows the maximum complexity's O(2^(m+n)). 

First we need to find the recurrence equation, which is : 

$$
T(c,r) = \sum_{i=1}^{c} T(i) + \sum_{j=1}^r T(j) + O(1)
$$

With : 
  - c : Column number 
  - r : Row number 
  - O(1) : The function used to get the config value

We can assume that c = r and transform it to: 

$$
T(c,r) = 2\sum_{k=1}^nT(k) + O(1)
$$

We can represent all the calls on a tree. Each step we divide the tree in 2 recursive calls. 

As the tree has a size of n, the complexity for this algorithm's exponential with 

$$T(c,r) = 2^{c+r}$$

### Q8 

A dictionnary would be a great data structure 

### Q9 

(100,100,50,50) computes ```-198```

(100, 100, 48, 52) computes ```191```

### Q10 

All the i and j couples such that (127,127,i,j) is equals to 127 are : 
  - (0,63) 
  - (63,0) 
  - (63,126)
  - (126,63)


### Q11

Let's first look at ```get_successeurs``` function. 
Each step we iterate (c-1) + (r-1) which make the complexity equals to O(c + r). 

For ```config_value```, the recursive call iterate on all the successors. As the config are stocked, we need to compute only one for each config. The number of differents configurations is : 

$$
T(c,r) = \sum_{i=1}^c\sum_{j=1}^ri.j <=> c².r²
$$

The final complexity is 
$$O(c².r²(c+r))$$

Let's assume c = r = n. The complexity is now: 

$$
T(n) = O(n⁴.n) = O(n⁵)
$$

Which is polynomial, and faster than the naive version.

### Q12

All configurations are symmetrical which allows them to be related to a single config. 

With appropriate axial/mirror/transposed-symmetry each configuration can be the same as the other, that's why we can compute only one of them and return this value for each symmetrical config. 

### Q13 

As I previously said, we can compute only one value for a config and then affect the given value for all symetrics. 

For the non-symmetric algorithm it took : 
```bash
lucas@gerard:~/Desktop/m1/act-soyah-sauvage-2025/TP2_lucas$ python3 script.py 
-198
368.70908179499975
```

For the symmetric it was : 

```bash
lucas@gerard:~/Desktop/m1/act-soyah-sauvage-2025/TP2_lucas$ python3 script.py 
-198
354.0156058759994
lucas@gerard:~/Desktop/m1/act-soyah-sauvage-2025/TP2_lucas$
``` 

It computes 14 seconds faster !