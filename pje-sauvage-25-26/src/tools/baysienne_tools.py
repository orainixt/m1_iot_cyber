import re
import math
import random
from collections import defaultdict
from tools.csv_tools import iter_csv
import matplotlib.pyplot as plt
from tools.distance import get_correctness
from pathlib import Path
import os 
import csv  

def lower_tweet(tweet):
    tweet = tweet.lower()
    tweet = re.sub(r'[^a-z0-9\s]', '', tweet)
    return tweet.split()

def train_classifier(filename):
       
    n_mc = defaultdict(lambda: defaultdict(int)) 
    n_c = defaultdict(int)                       
    tweets_per_class = defaultdict(list)        
    vocabulary = set()                           
    total_tweets = 0

    (tweet_col,grade_col) = find_tweet_and_grade_columns(filename)
    

    for row in iter_csv(filename):
        tweet_text, grade = row[tweet_col], row[grade_col]
        total_tweets += 1
        
        mots = lower_tweet(tweet_text)
        tweets_per_class[grade].append(mots)

        n_c[grade] += len(mots)
        for mot in mots:
            n_mc[grade][mot] += 1
            vocabulary.add(mot)

    N = len(vocabulary)
    p_c = {} 

    for c in n_c.keys():
        num_tweets_c = len(tweets_per_class[c])
        p_c[c] = num_tweets_c / total_tweets
    
    return {
        'p_c': p_c,
        'n_c': n_c,
        'n_mc': n_mc,
        'N': N
    }



def predict_grade(tweet_text, model):
    
    tweet_mots = clean_tweet(tweet_text)
    scores = {}
    
    p_c = model['p_c']
    n_c = model['n_c']
    n_mc = model['n_mc']
    N = model['N']

    for classe in p_c.keys():
        
        log_prob = math.log(p_c[classe])
        n_c_classe = n_c[classe]

        for mot in tweet_mots:
            n_mc_count = n_mc[classe].get(mot, 0)
            p_m_c = (n_mc_count + 1) / (n_c_classe + N)
            
            log_prob += math.log(p_m_c)
            
        scores[classe] = log_prob

    return max(scores, key=scores.get)

def bayesien_naive(filename,tweet): 
    bayes_model = train_classifier(filename)
    prediction = predict_grade(tweet,bayes_model)
    return prediction 



def preprocess_tweet(tweet, ngram_mode):
    """
    Cleans tweet, filters short words, and generates tokens based on mode.
    ngram_mode: 'uni', 'bi', or 'uni_bi'
    """

    text = re.sub(r'[^a-z0-9\s]', '', tweet.lower())
    words = text.split()

    words = [w for w in words if len(w) > 3]
    
    tokens = []

    if ngram_mode == 'uni' or ngram_mode == 'uni_bi':
        tokens.extend(words)

    if ngram_mode == 'bi' or ngram_mode == 'uni_bi':
        bigrams = [words[i] + " " + words[i+1] for i in range(len(words)-1)]
        tokens.extend(bigrams)
        
    return tokens

def train(dataset, ngram_mode):
    """
    Builds the model: counts words and class probabilities.
    """

    n_mc = defaultdict(lambda: defaultdict(int)) 
    n_c = defaultdict(int)                       
    p_c = defaultdict(int)                      
    vocab = set()
    total_tweets = len(dataset)

    for tweet, label in dataset:
        tokens = preprocess_tweet(tweet, ngram_mode)
        p_c[label] += 1
        n_c[label] += len(tokens)
        
        for t in tokens:
            n_mc[label][t] += 1
            vocab.add(t)
            

    for c in p_c:
        p_c[c] = p_c[c] / total_tweets
        
    return p_c, n_c, n_mc, len(vocab)


def predict(tweet, model, ngram_mode, use_frequency):
    """
    Predicts the class of a new tweet.
    use_frequency=False
    use_frequency=True     
    """
    p_c, n_c, n_mc, N = model
    tokens = preprocess_tweet(tweet, ngram_mode)

    if not use_frequency:
        tokens = list(set(tokens))
        
    scores = {}
    for label in p_c:

        score = math.log(p_c[label]) if p_c[label] > 0 else -9999
        
        for t in tokens:

            count = n_mc[label][t]
            proba = (count + 1) / (n_c[label] + N)
            score += math.log(proba)
            
        scores[label] = score
        

    return max(scores, key=scores.get)


def cross_validation(data, k=3):
    print(f"\n--- Cross-Validation (k={k}) ---")
    random.shuffle(data)
    fold_size = len(data) // k
    

    configs = [
        ("Presence, Uni", 'uni', False),
        ("Presence, Bi", 'bi', False),
        ("Presence, Uni+Bi", 'uni_bi', False),
        ("Frequency, Uni", 'uni', True),
        ("Frequency, Bi", 'bi', True),
        ("Frequency, Uni+Bi", 'uni_bi', True)
    ]
    

    print(f"{'Configuration':<25} | {'Error Rate':<10}")
    print("-" * 40)
    
    for name, mode_ng, mode_fr in configs:
        total_error = 0
        
        for i in range(k):

            start = i * fold_size
            end = start + fold_size
            test_set = data[start:end]
            train_set = data[:start] + data[end:]
            

            model = train(train_set, mode_ng)
            

            nb_errors = 0
            for tweet, true_label in test_set:
                pred = predict(tweet, model, mode_ng, mode_fr)
                if pred != true_label:
                    nb_errors += 1
            

            if len(test_set) > 0:
                total_error += nb_errors / len(test_set)
        

        avg_error = total_error / k
        print(f"{name:<25} | {avg_error:.4f}")




def get_bayes_confusion_matrix(train_data, test_data, ngram_mode, use_frequency):
    """
    Trains a Bayes model and generates a confusion matrix specifically formatted 
    for the student GUI (using keys like 'but_p', 'but_neg', etc.).
    """

    model = train(train_data, ngram_mode)


    matrix = {
        "0": {"true": 0, "but_p": 0, "but_neu": 0},
        "2": {"true": 0, "but_p": 0, "but_neg": 0},
        "4": {"true": 0, "but_neu": 0, "but_neg": 0}, 
    }


    for tweet, grade in test_data:

        prediction = predict(tweet, model, ngram_mode, use_frequency)
        

        grade = str(grade)
        prediction = str(prediction)

        if grade == "0": 
            if prediction == "0": matrix["0"]["true"] += 1
            elif prediction == "2": matrix["0"]["but_neu"] += 1
            elif prediction == "4": matrix["0"]["but_p"] += 1
            
        elif grade == "2": 
            if prediction == "2": matrix["2"]["true"] += 1
            elif prediction == "0": matrix["2"]["but_neg"] += 1
            elif prediction == "4": matrix["2"]["but_p"] += 1
            
        elif grade == "4": 
            if prediction == "4": matrix["4"]["true"] += 1
            elif prediction == "0": matrix["4"]["but_neg"] += 1
            elif prediction == "2": matrix["4"]["but_neu"] += 1

    return matrix


def compare_bayes_configs(data, k=3):
    """
    Performs k-fold cross-validation based on your snippet.
    Returns results formatted for the GUI graph (Accuracy per class).
    """
    print(f"\n--- Cross-Validation (k={k}) ---")
    

    random.shuffle(data)
    fold_size = len(data) // k

    configs = [
        ("Presence, Uni", 'uni', False),
        ("Presence, Bi", 'bi', False),
        ("Presence, Uni+Bi", 'uni_bi', False),
        ("Frequency, Uni", 'uni', True),
        ("Frequency, Bi", 'bi', True),
        ("Frequency, Uni+Bi", 'uni_bi', True)
    ]

    results = []
    config_names = []

    print(f"{'Configuration':<25} | {'Global Error':<10}")
    print("-" * 40)

    for name, mode_ng, mode_fr in configs:
        

        total_pos = 0
        total_neu = 0
        total_neg = 0
        total_global_error = 0 

        for i in range(k):

            start = i * fold_size
            end = start + fold_size
            test_set = data[start:end]
            train_set = data[:start] + data[end:]

            matrix = get_bayes_confusion_matrix(train_set, test_set, mode_ng, mode_fr)

            pos, neu, neg = get_correctness(matrix)

            total_pos += pos
            total_neu += neu
            total_neg += neg
            

            avg_acc = (pos + neu + neg) / 3 
            total_global_error += (1.0 - avg_acc)


        avg_pos = (total_pos / k) * 100
        avg_neu = (total_neu / k) * 100
        avg_neg = (total_neg / k) * 100
        
        avg_global_error = total_global_error / k


        results.append((avg_pos, avg_neu, avg_neg))
        config_names.append(name)

        print(f"{name:<25} | {avg_global_error:.4f}")

    return results, config_names

def print_bayes_graph(list_of_results, config_names): 
    """
    Plots the performance of different Bayes configurations.
    """
    pos_list = [res[0] for res in list_of_results] 
    neu_list = [res[1] for res in list_of_results] 
    neg_list = [res[2] for res in list_of_results] 

    fig, ax = plt.subplots(figsize=(10, 6)) 

    # X axis indices
    x_indices = range(len(config_names))

    # Plot lines
    ax.plot(x_indices, pos_list, marker='o', linestyle='-', label="Positives", color='green')
    ax.plot(x_indices, neu_list, marker='s', linestyle='-', label="Neutrals", color='blue')
    ax.plot(x_indices, neg_list, marker='x', linestyle='-', label="Negatives", color='red')

    # Set labels
    ax.set_xticks(x_indices)
    ax.set_xticklabels(config_names, rotation=45, ha="right") 

    ax.set_xlabel("Configuration")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Naive Bayes Performance by Configuration")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
      
    fig.tight_layout()
    return fig


def auto_grade_database_to_csv_baysienne(filename_to_grade, reference_filename, ngram_mode='uni', use_frequency=False):
    """
    Uses a database (reference_filename) to train a Bayes model, 
    then predicts grades for a database (filename_to_grade).
    """

    print(f"Loading reference base for training: {reference_filename}...")
    training_data = []
    
    try:
        (ref_t_col, ref_g_col) = find_tweet_and_grade_columns(reference_filename)
    except:
        ref_g_col, ref_t_col = 0, 1 

    for row in iter_csv(reference_filename):
        if len(row) > max(ref_t_col, ref_g_col):
            grade = str(row[ref_g_col]).strip()
            tweet = row[ref_t_col]

            if grade in ["0", "2", "4"]:
                training_data.append((tweet, grade))

    if not training_data:
        print("Error: Reference database is empty or has no valid grades (0, 2, 4).")
        return
    print(f"Training Bayes model on {len(training_data)} tweets...")
    model = train(training_data, ngram_mode)

    print(f"Loading target file to grade: {filename_to_grade}...")
    target_data = []
    
    try:
        (tgt_t_col, tgt_g_col) = find_tweet_and_grade_columns(filename_to_grade)
    except:
        tgt_g_col, tgt_t_col = 0, 1

    for row in iter_csv(filename_to_grade):
        if len(row) > max(tgt_t_col, tgt_g_col):
            tweet = row[tgt_t_col]
            current_grade = str(row[tgt_g_col]).strip()

            if current_grade.lstrip('-').isdigit() or current_grade == "":
                target_data.append(tweet)

    if not target_data:
        print("Error: Target file is empty or contains only headers.")
        return

    base_path = Path(os.getcwd()) / "data"
    output_filename = f"graded_bayes_{filename_to_grade}"
    output_path = base_path / output_filename

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Predicting grades for {len(target_data)} tweets...")
    
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            for tweet in target_data:

                predicted_grade = predict(tweet, model, ngram_mode, use_frequency)

                writer.writerow([predicted_grade, tweet])
                
        print(f"Success! Saved to: {output_path}")
        
    except Exception as e:
        print(f"Error writing file: {e}")
