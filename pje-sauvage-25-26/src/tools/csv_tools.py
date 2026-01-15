from pathlib import Path
import os, sys, csv
import pandas as pd  
import re
from random import shuffle
import statistics 

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 


# THIS FUNCTION DON'T WORKS (ONLY RETURNS ERROR NO DIALECT) 
def find_delimiter(filename, additionals_delimiters=None): 
    """
    used to find delimiter in the filename filename 
    """
    csv_path = DATA_DIR / filename
    delimiters = [',',';','/t','|'] if additionals_delimiters is None else [',',';','/t','|'].append(additionals_delimiters) 
    with open(csv_path, 'r',newline='') as input_file:
        sample = input_file.read(4096)
        print(sample)
        try: 
            dialect = csv.Sniffer().sniff(sample, delimiters) 
            return dialect.delimiter
        except csv.Error: # weird file 

            first_line = sample.split('\n')[0] 

            semicolon_count = first_line.count(';') 
            comma_count = first_line.count(',')

            return ';' if semicolon_count > comma_count else ','

#this one checks which delimiter is the most stable (i.e. standard deviation ~= 0)
#dont work either 
def naive_find_delimiter(filename, additionals_delimiters=None, lines_to_read=100):

    csv_path = DATA_DIR / filename

    delimiters = [',',';','/t','|'] if additionals_delimiters is None else [',',';','/t','|'].append(additionals_delimiters) 
    compteurs = {deli: [] for deli in delimiters} 
    best_sd, best_deli = None, None

    with open(csv_path,'r',newline='') as f:   
        for _ in range(lines_to_read): 
            line = f.readline()
            if not line: break 
            for deli in delimiters: 
                compteurs[deli].append(line.count(deli))
    
    for deli, cpts in compteurs.items(): 
        
        if sum(cpts) == 0: break 
        avg = statistics.mean(cpts) # avg occurence per line 
        try: 
            standard_deviation = statistics.stdev(cpts) 
        except Exception as e: 
            print('probably just one line') 
            standard_deviation = 0 
        if  best_sd is None or standard_deviation < best_sd : 
            best_sd = standard_deviation 
            best_deli = deli 

    return best_deli 
            


def iter_csv(filename,file_delimiter=','): 
    """_summary_
    Args:
        filename (csv): The CSV file to iter on 

    Yields:
        readr: A generator with all the tweets from filename
    """
    csv_path = DATA_DIR / filename
    absolute_csv_path = os.path.abspath(csv_path)
    #file_delimiter = naive_find_delimiter(filename)
    with open(absolute_csv_path,'r', newline='') as input_file: 
        readr = csv.reader(input_file, delimiter=file_delimiter) 
        for row in readr: 
            yield row

def open_csv(filename): 
    """_summary_
    /! THIS FUNCTION NEED THE FILE DIRECTORY TO BE CLOSED
    Args:
        filename (_type_): _description_

    Returns:
        (file, csv.reader): _description_
    """
    csv_path = DATA_DIR / filename
    input_file = open(csv_path, newline='')
    reader = csv.reader(input_file) 
    return (input_file, reader)


def transform_csv_into_dataframe(filename,clean): 
    """
    read the CSV file related to path and transform it into a list
    Args:
        filename (csv): The CSV file
        clean (boolean): True if the CSV file is cleaned, False otherwise

    Returns:
        dataframe (pandas.dataframe): A more usuable list than classic lists 
    """

    csv_path = DATA_DIR / filename

    if not csv_path.exists():
        print("csv file does not exists") 
        return None
    
    if clean : 

        dataframe = pd.read_csv(
            csv_path, 
            header=None, 
            names=["target","texte"]
        )

    else :
        dataframe = pd.read_csv(
        csv_path, 
        header=None,
        names=["target","ids","date","flag","utilisateur","texte"]
        ) 

    return dataframe




def find_tweet_and_grade_columns(filename,delimiter=',',row_to_check=50,tweet_patterns=None,grade_patterns=None): 
    """
    find, with any given DataBase, the index of the tweet column 
    if there's no tweet, returns -1 
    patterns is an additional file to check (in case user add one (see graphic.pages.handle_tweets))  
    """

    tweet_pattern = re.compile(r"^(?=(?:.*[A-Za-z]){20,})(?=(?:.*\b\w+\b){3,}).*$")
    grade_pattern = re.compile(r"^(-1|[024])$") 
    
    potentials_tweet_col, potentials_grad_col = [], []

   

    for i, row in enumerate(iter_csv(filename,delimiter)): 
        if i>= row_to_check:
            break
        for col, elt in enumerate(row):
            if tweet_pattern.fullmatch(elt): 
                potentials_tweet_col.append(col) 
            if grade_pattern.fullmatch(elt): 
                potentials_grad_col.append(col)
            else:
                if (tweet_patterns != None): 
                    for pattern in tweet_patterns: 
                        potentials_tweet_col.append(col if pattern.fullmatch(elt) else None)
                if (grade_patterns != None): 
                    for pattern in grade_patterns:  
                        potentials_grad_col.append(col if pattern.fullmatch(elt) else None) 
   
    # division by 0 (if 0 potential match) 
    tweet_column = 0 if len(potentials_tweet_col) == 0 else int(sum(potentials_tweet_col) / len(potentials_tweet_col)) 
    # same 
    grade_column = 0 if len(potentials_grad_col) == 0 else  int(sum(potentials_grad_col) / len(potentials_grad_col))
    
    return (tweet_column,grade_column)
                


def clean_csv(filename,delimiter=','): 
    """
    Clean filename 
    Args:
        filename (csv): File to clean

    Raises:
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
    """
    try :
        url_pattern = re.compile(r"http\S+") 
        username_pattern = re.compile(r"@\S+") 
        rt_pattern = re.compile(r"\bRT\b")
        hastag_pattern = re.compile(r"#\S+") 
        emote_pattern = re.compile(r":\)|:\(")
        date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}") 
        patterns = [
            url_pattern,
            username_pattern, 
            rt_pattern, 
            hastag_pattern,
            emote_pattern
        ]

    except re.error as e: 
        print(f"--regex syntax error : {e}--")

    csv_path = DATA_DIR / filename
    output_filename = f"cleaned_{filename}" 
    output_path = DATA_DIR / output_filename

    if output_path.exists(): 
        print(f"Hey! {output_filename} already cleaned -- Change this with Message Box")
        return 
 

    tweets_index, grade_index = find_tweet_and_grade_columns(filename,delimiter)


    with open(csv_path,'r', newline='') as input_file, open(output_path, 'w', newline='') as output_file:
        if (tweets_index == -1 or grade_index == -1): raise ValueError("--tweets or grades index not found--\n--find_tweet_and_grade_column() returned -1 for either tweets index or grade index--")

        row_readr = csv.reader(input_file,delimiter=delimiter)
        row_writr = csv.writer(output_file,delimiter=',')             

        for row in row_readr: 

            if (tweets_index > len(row) -1): raise ValueError(f"--tweets index can't be greater than the len of a row of the metadata of a tweet--\n--len(row) = {len(row)}, tweets_index = {tweets_index}\n")
            if (tweets_index > len(row) -1): raise ValueError(f"--grades index can't be greater than the len of a row of the metadata of a tweet--\n--len(row) = {len(row)}, grades_index = {grade_index}\n")

            cleaned_row = [] 

            actual_tweet = row[tweets_index]
            actual_grade = row[grade_index]

            for pat in patterns: 
                actual_tweet = re.sub(pat,"",actual_tweet)

            cleaned_row.append(actual_grade.strip())
            cleaned_row.append(actual_tweet.strip())
            row_writr.writerow(cleaned_row)

def fetch_csv_filenames(): 
    return [
        f.name
        for f in DATA_DIR.glob("*.csv")
    ]

def fetch_csv_cleaned_filenames(): 
    return [
        f.name 
        for f in DATA_DIR.glob("*cleaned*.csv")
    ]

def fetch_csv_files(clean):
    """
    Fetch all the CSV files in ./data/
    Args:
        clean (boolean): 

    Returns:
        _type_: _description_
    """
    cleaned_pattern = re.compile(r"^cleaned_.*\.csv$")

    return [
        transform_csv_into_dataframe(f.name, clean)
        for f in DATA_DIR.glob("*.csv")
        if bool(cleaned_pattern.fullmatch(f.name)) == clean
    ]


def check_if_all_cleaned(): 
    csv_files = [csv_file.name for csv_file in DATA_DIR.glob("*.csv")]
    for csv_file in csv_files:
        if not csv_file.startswith("cleaned"):
            name = f"cleaned_{csv_file}"
            if name not in csv_files:
                clean_csv(csv_file)



def create_patterns(filename):
    """_summary_
    Pre-cond : filename must be CSV formatted (data1,data2,...,data_n)
    Args:
        filename (_type_): _description_
    """
    patterns = []

    for line in iter_csv(filename): 
        words = [p.strip() for p in line.strip().split(",") if p.strip()]
        for word in words: 
            patterns.append(re.compile(re.escape(word))) 

    return patterns


        
def get_tweet_grade(tweet,positive_patterns,negative_patterns): 

    pos_nb, neg_nb = 0,0
    for pattern in positive_patterns: 
        if pattern.search(tweet): 
            pos_nb += 1
    for pattern in negative_patterns:
        if pattern.search(tweet):
            neg_nb += 1
    
    if (pos_nb > neg_nb): 
        return 4 
    if (pos_nb < neg_nb): 
        return 0
    else: 
        return 2


def get_algo_accuracy(filename,function): 

    """_summary_
    Precond : filename must be a cleaned csv 
    """
    positive_patterns = create_patterns("positive.txt")
    negative_patterns = create_patterns("negative.txt")

    well_graded, bad_graded = 0,0 

    for line in iter_csv(filename): 
        (real_grade,tweet) = line[0], line[1]
        algo_grade = function(tweet,positive_patterns,negative_patterns)
        if (algo_grade == int(real_grade)):
            well_graded += 1 
        else : 
            bad_graded += 1

    return ((well_graded / (well_graded + bad_graded))*100)



def get_algo_matrix(filename,function): 
    """_summary_
    returns a matrice with 
    [0][0] = pourcentage of correct positive 
    [0][1] = pourcentage of incorrect postitive 
    [1][0] = pourcentage of correct negative 
    [1][1] = pourcentage of incorrect negative 
    Args:
        filename (_type_): _description_
        function (_type_): _description_
    """
    positive_patterns = create_patterns("positive.txt")
    negative_patterns = create_patterns("negative.txt")

    matrice = [[0 for _ in range(3)] for _ in range(3)]
    tot_p,tot_n = 0,0

    for line in iter_csv(filename): 
        (real_grade,tweet) = line.split(",",1)
        real_grade = int(real_grade)
        algo_grade = function(tweet,positive_patterns,negative_patterns) 

        if real_grade == 0 and algo_grade == real_grade: 
            matrice[1][0] += 1 
            tot_n +=1
        if real_grade == 0 and algo_grade!= real_grade: 
            matrice[1][1] += 1
            tot_n+=1 
        if real_grade == 4 and algo_grade == real_grade: 
            matrice[0][0] += 1 
            tot_p+=1
        if real_grade == 4 and algo_grade != real_grade: 
            matrice[0][1] += 1
            tot_p+=1

    matrice[0][0] = (matrice[0][0] / tot_p) * 100 
    matrice[0][1] = (matrice[0][1] / tot_p) * 100 
    matrice[1][0] = (matrice[1][0] / tot_n) * 100
    matrice[1][1] = (matrice[1][1] /tot_n) * 100 

    return matrice


def prepare_db(filename, train_ratio=2/3): 
    """
    Divide the database into two list : the learning db and the testing one
    Args:
        filename (_type_): _description_
        train_ratio (_type_, optional): _description_. Defaults to 2/3.

    Returns:
        _type_: _description_
    """

    pos_rows, neu_rows, neg_rows = [], [], []

    for row in iter_csv(filename):
        if len(row) < 2:
            continue  
        grade, tweet = row[0], row[1]
        if grade == "4":
            pos_rows.append((grade, tweet))
        elif grade == "2":
            neu_rows.append((grade, tweet))
        elif grade == "0":
            neg_rows.append((grade, tweet))
    
    shuffle(pos_rows) 
    shuffle(neu_rows)
    shuffle(neg_rows) 

    def split_rows(rows): 
        split_index = int(len(rows) * train_ratio) 
        return rows[:split_index], rows[split_index:] 

    learn_pos, test_pos = split_rows(pos_rows) 
    learn_neu, test_neu = split_rows(neu_rows) 
    learn_neg, test_neg = split_rows(neg_rows) 

    learning_db = learn_pos + learn_neu + learn_neg
    testing_db = test_pos + test_neu + test_neg 

    shuffle(learning_db) 
    shuffle(testing_db)

    return learning_db, testing_db

def get_tweets(cleaned_filename):
    tweet_index, _ = find_tweet_and_grade_columns(cleaned_filename)
    if tweet_index == -1:
        raise ValueError("Impossible de trouver la colonne des tweets")
    
    tweets = []
    for row in iter_csv(cleaned_filename):
        if len(row) > tweet_index:
            tweets.append(row[tweet_index])
    return tweets




