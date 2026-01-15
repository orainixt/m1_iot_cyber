from tools.csv_tools import prepare_db, find_tweet_and_grade_columns, iter_csv
import matplotlib.pyplot as plt
import numpy as np
import io
from PyQt5.QtGui import QImage, QPixmap
import csv 
import os 
from pathlib import Path

def naive_distance(tweet1,tweet2):
    """get the naive distance between tweet1 & tweet2 

    Args:
        tweet1 (_type_): _description_
        tweet2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    tweet1 = tweet1.lower()
    tweet2 = tweet2.lower()
    total,common = 0,0
    for mot1 in tweet1: 
        for mot2 in tweet2: 
            if mot1 == mot2: 
                common += 1
            total += 1
    return (total - common) / total

def jaccard_distance(tweet1,tweet2): 
    """jaccard distance between tweet1 and tweet2

    Args:
        tweet1 (_type_): _description_
        tweet2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    tweet1_set = set(tweet1.lower().split()) 
    tweet2_set = set(tweet2.lower().split()) 

    union = tweet1_set | tweet2_set
    intersection = tweet1_set & tweet2_set
    if len(union) == 0:
        return 0
    return (len(union) - len(intersection)) / len(union)

def find_furthest_neighbour(neighbour_list): 
    """find the index and the distance of the last element in neighbour_list 

    Args:
        neighbour_list (_type_): _description_

    Returns:
        _type_: _description_
    """
    maxi = 0
    index_to_return = 0
    for index,(_,_,distance) in enumerate(neighbour_list):
        if distance > maxi: 
            index_to_return = index 
            maxi = distance
    return (index_to_return,maxi)

# TESTS DU NOMBRE DE K 

def weighted_knn(tweet_to_label,k,base): 
    close_neighbours = [] 
    for grade,tweet in base :
        distance = jaccard_distance(tweet_to_label, tweet) 
        (furthsest_index,furthsest_distance) = find_furthest_neighbour(close_neighbours)

        if len(close_neighbours) < k: 
            close_neighbours.append((grade,tweet,distance))
        elif distance < furthsest_distance: 
            close_neighbours[furthsest_index] = (grade,tweet,distance) 
        
    class_score = {} 
    for grade,tweet,distance in close_neighbours: 
        epsilon = 1e-5 
        weight = 1 / (distance + epsilon) 
        class_score[grade] = class_score.get(grade,0) + weight

    predicted_class = max(class_score, key=class_score.get)

    return predicted_class


def knn(tweet_to_label,k,base): 
    """KNN Algorithm : Classify tweet_to_label with the database base 

    Args:
        tweet_to_label (_type_): _description_
        k (_type_): _description_
        base (_type_): Must be a list of tuple (grade,tweet)

    Returns:
        _type_: _description_
    """

    close_neighbours = [] 

    for grade,tweet in base:  

        distance = jaccard_distance(tweet_to_label,tweet)
        (furthsest_index,furthsest_distance) = find_furthest_neighbour(close_neighbours)

        if len(close_neighbours) < k:
            close_neighbours.append((grade,tweet,distance))
        
        elif distance < furthsest_distance:
            close_neighbours[furthsest_index] = (grade,tweet,distance)

    def get_average_grade(close_neighbours): 
        grade_dic = {}
        for (grade,_,_) in close_neighbours:
            grade_dic[grade] = grade_dic.get(grade,0) +1
        return max(grade_dic, key=grade_dic.get)

    average_grade = get_average_grade(close_neighbours)

    return average_grade



def test_database(filename, k, knn_function=knn): 
    """test the database `filename` with k neigbours and with any function (that returns a 0or2or4 grade) but knn default 

    Args:
        filename (_type_): _description_
        k (_type_): _description_
        knn_function (_type_, optional): _description_. Defaults to knn.

    Returns:
        _type_: _description_
    """
    learn_db, test_db = prepare_db(filename)

    confusion_matrix = {
        "0": {"true": 0, "but_p": 0, "but_neu": 0},
        "2": {"true": 0, "but_p": 0, "but_neg": 0},
        "4": {"true": 0, "but_neu": 0, "but_neg": 0},
    }

    for grade, tweet in test_db:
        estimate_grade = str(knn_function(tweet, k, learn_db))

        if grade == "0": 
            if estimate_grade == "0":
                confusion_matrix["0"]["true"] += 1
            elif estimate_grade == "2":
                confusion_matrix["0"]["but_neu"] += 1
            elif estimate_grade == "4":
                confusion_matrix["0"]["but_p"] += 1

        elif grade == "2": 
            if estimate_grade == "2":
                confusion_matrix["2"]["true"] += 1
            elif estimate_grade == "0":
                confusion_matrix["2"]["but_neg"] += 1
            elif estimate_grade == "4":
                confusion_matrix["2"]["but_p"] += 1

        elif grade == "4": 
            if estimate_grade == "4":
                confusion_matrix["4"]["true"] += 1
            elif estimate_grade == "0":
                confusion_matrix["4"]["but_neg"] += 1
            elif estimate_grade == "2":
                confusion_matrix["4"]["but_neu"] += 1

    return confusion_matrix

def get_matrix_pixmap(matrix):

    row_0 = [matrix["0"]["true"], matrix["0"]["but_neu"], matrix["0"]["but_p"]]
    row_2 = [matrix["2"]["but_neg"], matrix["2"]["true"], matrix["2"]["but_p"]]
    row_4 = [matrix["4"]["but_neg"], matrix["4"]["but_neu"], matrix["4"]["true"]]
    data = np.array([row_0, row_2, row_4])

    fig, ax = plt.subplots(figsize=(5, 4)) 
    cax = ax.imshow(data, cmap='Blues')
    fig.colorbar(cax)

    classes = ['Negatives (0)', 'Neutrals (2)', 'Positives (4)']
    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(classes)))
    ax.set_xticklabels(classes)
    ax.set_yticklabels(classes)
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    
    ax.set_title('Confusion Matrix')

    for i in range(len(classes)):
        for j in range(len(classes)):
            valeur = data[i, j]
            color = "white" if valeur > data.max()/2 else "black"
            ax.text(j, i, str(valeur), ha="center", va="center", color=color, fontweight='bold')

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    image = QImage.fromData(buf.getvalue())
    pixmap = QPixmap.fromImage(image)
    plt.close(fig)
    
    return pixmap


def get_graph_pixmap(list_of_correctness):
    """
    Crée le graphique d'évolution des précisions et retourne une QPixmap.
    """
    pos_list = []
    neu_list = []
    neg_list = []
    index_list = []

    for ((pos, neu, neg), index) in list_of_correctness:
        pos_list.append(pos)
        neu_list.append(neu)
        neg_list.append(neg)
        index_list.append(index)

    
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(index_list, pos_list, marker='.', label="Positives")
    ax.plot(index_list, neu_list, marker='.', label="Neutrals")
    ax.plot(index_list, neg_list, marker='.', label="Negatives")

    ax.set_xlabel("k (neighbors number)")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("KNN Accuracy depending on k")
    ax.grid(True)
    ax.legend()
    
    fig.tight_layout()


    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    image = QImage.fromData(buf.getvalue())
    pixmap = QPixmap.fromImage(image)
    

    plt.close(fig)
    
    return pixmap

def get_correctness_pourcent(matrix):
    """returns the correct ness pourcent of each grade for the matrix matrix

    Args:
        matrix (_type_): _description_

    Returns:
        _type_: _description_
    """
    neg_correct = (matrix["0"].get("true", 0) / sum(matrix["0"].values())) * 100
    neu_correct = (matrix["2"].get("true", 0) / sum(matrix["2"].values())) * 100
    pos_correct = (matrix["4"].get("true", 0) / sum(matrix["4"].values())) * 100
    return pos_correct, neu_correct, neg_correct

def get_correctness(matrix):
    neg_correct = (matrix["0"].get("true", 0) / sum(matrix["0"].values()))  
    neu_correct = (matrix["2"].get("true", 0) / sum(matrix["2"].values()))
    pos_correct = (matrix["4"].get("true", 0) / sum(matrix["4"].values())) 
    return pos_correct, neu_correct, neg_correct


def get_higher_correctness(list_of_correctness): 
    """return the higher pourcent and index of each grade in list_of_correctness

    Args:
        list_of_correctness (_type_): _description_

    Returns:
        _type_: _description_
    """

    max_p, max_neu, max_neg = 0.0,0.0,0.0

    for index,(p,neu,neg) in enumerate(list_of_correctness): 
        if p > max_p : 
            max_p = p 
            p_index = index
        if neu > max_neu: 
            max_neu = neu
            neu_index = index
        if neg > max_neg: 
            max_neg = neg
            neg_index = index

    return [(max_p,p_index), (max_neu, neu_index), (max_neg, neg_index)]

def print_matrix_graph(list_of_correctness): 
    """
    prints the graphic associated to the list_of_correctness
    """
    pos_list = []
    neu_list = []
    neg_list = []
    index_list = []

    for ((pos,neu,neg),index) in list_of_correctness: 
        pos_list.append(pos) 
        neu_list.append(neu) 
        neg_list.append(neg) 
        index_list.append(index)

    fig, ax = plt.subplots(figsize=(6,4)) 

    ax.plot(index_list, pos_list, marker='+', label="Positives")
    ax.plot(index_list, neu_list, marker='+', label="Neutrals")
    ax.plot(index_list, neg_list, marker='+', label="Negatives")

    ax.set_xlabel("k (neighbors number)")
    ax.set_ylabel("Pourcent of accurate estimation")
    ax.set_title("KNN accuracy depending on k")
    ax.grid(True)
    ax.legend()
    
    fig.tight_layout()
    return fig


def matrix_to_text(matrix):
    text = ""
    for real_class, predictions in matrix.items():
        if real_class == "0": real_class_str = "Negative"
        elif real_class == "2": real_class_str = "Neutral"
        elif real_class == "4": real_class_str = "Positive"
        total = sum(predictions.values())
        text += f"{real_class_str}:\n"
        for pred_class, count in predictions.items():
            pourcent = (count / total) * 100
            text += f"  {pred_class} = {count} ({pourcent:.2f}%)\n"
    return text



def print_confusion_matrix(matrix):
    """
    prints on the shell the matrix matrix 
    """
    
    for real_class, predictions in matrix.items(): 

        if (real_class == "0"): real_class_str = "Negative" 
        elif (real_class == "2"): real_class_str = "Neutral" 
        elif (real_class == "4"): real_class_str = "Positive" 

        print(f"Predictions for {real_class_str}:")
        total = sum(predictions.values()) 

        for pred_class, count in predictions.items(): 
            pourcent = (count / total) * 100 
            print(f" {pred_class} = {count} ({pourcent: .2f}%)")
        print()



def test_distance(filename,lower_k,higher_k,step=2): 
    """
    used to test distances 
    """
    correctness_pourcent = []

    best_pos = 0 
    best_neu = 0 
    best_neg = 0

    best_pos_k = 0 
    best_neu_k = 0 
    best_neg_k = 0

    best_pos_matrix = None 
    best_neu_matrix = None
    best_neg_matrix = None 

    for i in range(lower_k,higher_k+1,step): 
        matrix = test_database(filename,i) 

        (i_pos,i_neu,i_neg) = get_correctness(matrix)

        if i_pos > best_pos : 
            best_pos = i_pos
            best_pos_k = i
            best_pos_matrix = matrix
        if i_neu > best_neu : 
            best_neu = i_neu
            best_neu_k = i
            best_neu_matrix = matrix 
        if i_neg > best_neg : 
            best_neg = i_neg
            best_neg_k = i
            best_neg_matrix = matrix

        correctness_pourcent.append(((i_pos,i_neu,i_neg),i))

    return (
        correctness_pourcent,
        (best_pos_k, best_pos_matrix),
        (best_neu_k, best_neu_matrix),
        (best_neg_k, best_neg_matrix),
    )

def auto_grade_database_to_csv_knn(filename_to_grade, reference_filename, k=3):

    print(f"Loading reference base: {reference_filename}...")
    reference_base = []
    try:
        (ref_t_col, ref_g_col) = find_tweet_and_grade_columns(reference_filename)
    except:
        ref_g_col, ref_t_col = 0, 1

    for row in iter_csv(reference_filename):
        if len(row) > max(ref_t_col, ref_g_col):
            grade = str(row[ref_g_col]).strip()
            tweet = row[ref_t_col]
            

            if grade in ["0", "2", "4"]:
                reference_base.append((grade, tweet))

    if not reference_base:
        print("Error: Reference database is empty or has no valid grades (0, 2, 4).")
        return

    print(f"Loading target file: {filename_to_grade}...")
    target_data = []
    
    try:
        (tgt_t_col, tgt_g_col) = find_tweet_and_grade_columns(filename_to_grade)
    except:
        tgt_g_col, tgt_t_col = 0, 1

    for row in iter_csv(filename_to_grade):
        if len(row) > max(tgt_t_col, tgt_g_col):

            tweet = row[tgt_t_col]
            target_data.append(tweet)

    if not target_data:
        print("Error: Target file is empty.")
        return


    base_path = Path(os.getcwd()) / "data"
    
    output_filename = f"graded_knn_{filename_to_grade}"
    output_path = base_path / output_filename


    print(f"Grading {len(target_data)} tweets using {len(reference_base)} references...")
    
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            for i, tweet_to_grade in enumerate(target_data):

                predicted_grade = knn(tweet_to_grade, k, reference_base)
                writer.writerow([predicted_grade, tweet_to_grade])
                
                if i % 100 == 0 and i > 0:
                    print(f"Processed {i}/{len(target_data)}...")

        print(f"Success! Saved to {output_filename}")
        
    except Exception as e:
        print(f"Error writing file: {e}")
