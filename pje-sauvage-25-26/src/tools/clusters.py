from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
import numpy as np 
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import pdist

from tools.csv_tools import get_tweets
from tools.distance import jaccard_distance

def get_D(cleaned_filename):
    ltweet = get_tweets(cleaned_filename)
    N = len(ltweet)
    D = np.zeros((N,N))

    for i in range(N): 
        for j in range(N): 
            D[i,j] = jaccard_distance(ltweet[i],ltweet[j])

    return D 


def average_complete(cleaned_filename): 

    D = get_D(cleaned_filename)

    # D mat n*n distance between tweets
    D_condensed = squareform(D) 

    # average method 
    Z_avg = linkage(D_condensed, method='average') 

    # complet method 
    Z_com = linkage(D_condensed, method='complete')

    # --- Visualisation des dendrogrammes ---
    plt.figure(figsize=(8,4))
    dendrogram(Z_avg)
    plt.title("Hierarchical Analysis - Average Method")
    plt.xlabel("Tweets")
    plt.ylabel("Distance")
    
    plt.figure(figsize=(8,4))
    dendrogram(Z_com)
    plt.title("Hierarchical Analysis - Complete method")
    plt.xlabel("Tweets")
    plt.ylabel("Distance")

    # --- Visualisation des dendrogrammes ---
    fig_avg = plt.figure(figsize=(8,4)) # Capture de la figure 1
    dendrogram(Z_avg)
    plt.title("Hierarchical Analysis - Average Method")
    
    fig_com = plt.figure(figsize=(8,4)) # Capture de la figure 2
    dendrogram(Z_com)
    plt.title(" Hierarchical Analysis - Complete Method")

    # Découper l'arbre en K clusters (ex. K=3)
    clusters_avg = fcluster(Z_avg, 3, criterion='maxclust')
    clusters_comp = fcluster(Z_com, 3, criterion='maxclust')

    return fig_avg, fig_com, clusters_avg, clusters_comp

def ward(cleaned_filename): 
    # --- TF-IDF + Ward ---
    tweets = get_tweets(cleaned_filename) 
    # tweets = liste de textes nettoyés ou bruts
    vectorizer = TfidfVectorizer(
        lowercase=True,     # mettre en minuscules
        stop_words="english" # ou "french"
    )

    # Matrice TF-IDF
    tfidf = vectorizer.fit_transform(tweets).toarray()

    # Calcul de la distance euclidienne entre les vecteurs TF-IDF
    D2 = pdist(tfidf, metric='euclidean')

    # Clustering avec la méthode Ward (équivalent ward.D2 en R)
    Z_ward = linkage(D2, method='ward')

    # --- Visualisation ---
    fig = plt.figure(figsize=(8,4))
    dendrogram(Z_ward)
    plt.title("Hierarchical Analysis - Ward (TF-IDF + Euclidienne)")
    plt.xlabel("Tweets")
    plt.ylabel("Distance")
 
    # Découpage en K clusters
    clusters_ward = fcluster(Z_ward, 3, criterion='maxclust')
    # here k=3 

    return fig, clusters_ward

