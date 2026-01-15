# TP 4 - Heuristics
Here is Lucas SAUVAGE ACT-TP4 assignement 

## Answers to questions

### Q 1.0, 1.1, 1.2

See [**random_ordo.py**](./random_ordo.py)

### Q 1.3

The subject suggest to consider delay for this heuristic but I choosed an other way. 
For the heuristic, we can sort the instance data tab by decreasing order of $\frac{w_j}{p_j}$ : 
    - computes instance_data 
    - sort instance_data by decreasing order
    - execute each task sequentially 

I understand now why the subject tells us to sort by delay. 
The method above always returns the task in increasing order. 

Therefore, I'll sort the tab using a little bit more complex formula. 
The goal is to sort by minmaxing (t+p,d) with t the actual time. 
This reduces the total delay by half, as the log below shows. 

```bash
[annick@Iusearchbtw tp4]$ python3 heuristic.py n100_39_b.txt
258056
[annick@Iusearchbtw tp4]$ python3 random_ordo.py n100_39_b.txt
Ordo [Not important for ]
Instance data [Don't care either]:
Delay for this instance and this random ordo is : 509198 secondes.
``` 

Heuristic's code is [**here**](./heuristic.py) 

### Q 1.4 

Let's start from the output of the previous question, i.e. the solution given by the algorithm above.
Then, make a small change in the ordo of the output.
If it's better, i.e. delay's lower, keep the solution. 

There's two way to change the ordo. 
The first one is just a swap, the second one re-organize ordo as the scheme below : 
[A,B,C,D,E] becomes (if we choose B and E) [A,E,B,C,D], all the tasks has been moved. 

I saw online that the second one might be better for delay problem (and minmax overall) 

Therefore, there's two main algorithm to implement those swapping methods.

#### Hill Climbig 

Basic one, look through all possible neighbours of the minmax solution, i.e. all the swaps. 
When there's a better delay time, change the solution and test over all the neighbours of the new solution. 
Whenever there's no better solution, stop. 

There's two possible way about when to change the solution. 
One test all possibles neighbours and take the min delay of all. 
The second one stops whenever a better delay has been found. 

Obviously the first method is better but more complex, as it goes through all the neighbours which is $O(n^2)*O(n) = O(n^3)$. 
The second one is better in the best cases ($O(n)$) but stays the same in the worst case. 

#### VND 

VND is an optimized version of Hill Climbing. It swaps between the two possible swaps. Let's call them swap and insertion. 
It uses Hill Climbing with swap and whenever Hill Climbing's stuck, it tries insertion. 
If it's stuck again, it uses swap. When both methods are stuck, it stops. 

As VND implements Hill Climbing and optimize it, I'll code VND. 

I implemented it [**here**](./vnd.py). The code is documented and explain how I managed to code it.

### Q 1.5 

The ILS algorithm as to follow these steps :

    - Initialisation : Takes an instance and computes minmax on it, n -- number of loop and accept -- True if accept all, False o.w.
    - Perturbation : Switch 2 (resp. 4) randoms items in ordo if more is False (resp. True)
    - Local Base Search : Uses VND to check if there's a better ordo in the neighbours 
    - Acceptation : Chech if the new ordo is better. If check is False it doesn't checks and accept new ordo.
    - Returns the best ordo (and delay for tests) when n is reached 

It's implementation is [**here**](./ils.py).

### Q 1.6

To test ILS, I checked the computed delay for n and k in this list : [3,5,10]
I ran the test all day, got errors three times. 
As the tests needs 2hours to complete, I can't correct the last error I got. 

The function used is in [**test.py**](./test.py). It's 
Please, can you go check quick that the test are implemented, even if I don't have result. 

### Q 1.7 

As the tests are quite long, I'll only test `n100_15_b` and `n100_85_b` 

Here are the logs for `n100_85_b` : 

```bash
Traitement de n100_85_b.txt (Optimum: 284)...
read instance ok
random_ordo ok
minmax ok
vnd ok
ils test ok
*-------------------------------------------*
Delay value for random ordo : 310188
*-------------------------------------------*
Delay value for minmax (heuristic) : 77552
*-------------------------------------------*
Delay value for VND : 341
*-------------------------------------------*
*-------------------------------------------*
Final best value for ILS : 341
> random  : Gap = 109121.13% | Temps = 0.0001s
> minmax  : Gap = 27207.04% | Temps = 0.0007s
> vnd     : Gap = 20.07% | Temps = 76.8019s
> ils     : Gap = 20.07% | Temps = 137.4821s
```

We can notice that the delay value never reaches the optimal delay. 
It's the same for `n100_15_b` : 

```bash
Traitement de n100_15_b.txt (Optimum: 172995)...
read instance ok
random_ordo ok
minmax ok
vnd ok
ils test ok
*-------------------------------------------*
Delay value for random ordo : 493556
*-------------------------------------------*
Delay value for minmax (heuristic) : 254885
*-------------------------------------------*
Delay value for VND : 173075
*-------------------------------------------*
Final best value for ILS : 173075
*-------------------------------------------*
> random  : Gap = 185.30% | Temps = 0.0001s
> minmax  : Gap = 47.34% | Temps = 0.0010s
> vnd     : Gap = 0.05% | Temps = 183.7166s
> ils     : Gap = 0.05% | Temps = 606.6817s
```

It means that the parameter used for ILS are not optimum. 
Because the tests was very long (and because I thought it would be the easy part so I'm doing it late), I ran the test for the different values of k and n in ILS while trying to launch ILS with k = 5 and n = 5. 

I launched the same test for n = 5 and k = 10 and here are the logs 

```bash
Traitement de n100_15_b.txt (Optimum: 172995)...
read instance ok
random_ordo ok
minmax ok
vnd ok
ils test ok
*-------------------------------------------*
Delay value for random ordo : 457953
*-------------------------------------------*
Delay value for minmax (heuristic) : 254885
*-------------------------------------------*
Delay value for VND : 173075
*-------------------------------------------*
Final best value for ILS : 173075
*-------------------------------------------*
> random  : Gap = 164.72% | Temps = 0.0001s
> minmax  : Gap = 47.34% | Temps = 0.0011s
> vnd     : Gap = 0.05% | Temps = 183.4892s
> ils     : Gap = 0.05% | Temps = 908.7839s
```

Well, it seams that it's not `k` the problem. 
However, I don't have enough time to run it again, sorry. 
In any case, all the functions to checks the metrics are in [**test.py**](./test.py). 
I am really sorry I didn't managed to test more. 

