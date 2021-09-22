# scrabble cheater SQL database

import sqlite3
from sqlite3 import Error
import re

def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

def create_connection(path):
    connection = None
    
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successfull")
    except Error as e:
        print(f"The error '{e} has occured")
        
    return connection 


def execute_query(connection, query):
    cursor = connection.cursor()
    try: 
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' has occured")
              
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' has occured")
        
# SCRABBLE WORD TABLE
create_scrabble_library_table = """
CREATE TABLE library (
   word TEXT PRIMARY KEY,
   points INTEGER NOT NULL,
   length INTEGER NOT NULL
   );
"""

# WORD DICTIONARY TABLE
create_scrabble_dictonary_table = """
CREATE TABLE dictionary (
   word TEXT PRIMARY KEY,
   definition TEXT
   );   
"""

# ADDING TO COLLECTION 

tile_dict = {
    "A" : 1,"B" : 3,"C" : 3,"D" : 2,
    "E" : 1,"F" : 4,"G" : 2,"H" : 4,
    "I" : 1,"J" : 8,"K" : 5,"L" : 1,
    "M" : 3,"N" : 1,"O" : 1,"P" : 3,
    "Q" : 10,"R" : 1,"S" : 1,"T" : 1,
    "U" : 1,"V" : 4,"W" : 4,"X" : 8,
    "Y" : 4, "Z" : 10
}

def add_scrabble_word(word :str):
    
    points = 0
    for i in word:
        points += tile_dict[i]
    
    out = f"""
    INSERT INTO
      library (word, points, length)
    VALUES ('{word}', {points}, {len(word)});
    
    """
    return out

def add_scrabble_definition(word : str, definition : str) -> str:
    
    out = f"""
    INSERT INTO 
      definitions (word, definition)
    VALUES IF NOT EXIST
      ('{word}', {definition});
    """
    return out


def get_word(word : str) -> str:
    select_word =  f"SELECT * FROM library WHERE library.word = {word};"
    return select_word

def get_word_def(word : str) -> str:
    select_def = f"SELECT * FROM definitions WHERE definition.word = {word};"
    return select_def


def get_words_excluding(table : str, letters : str) -> str:
    letter_and_count = {}
    for i in letters:
        if i in letter_and_count:
            letter_and_count.update({i : letter_and_count[i] + 1})
        else:
            letter_and_count.update({i : 1})

    excluding = ""
    for i in tile_dict.keys():
        if i not in letter_and_count:
            excluding += i    
    regex_excluding = f"(^(?!.*[{excluding}]).*)"
    
    exludes = f"""
    SELECT * FROM ({table_insert(table)})
    WHERE 
    library.word REGEXP '{regex_excluding}';
    """
    return excludes    
def get_words_containing(table : str, letters : str) -> str: 

    letter_regex = f"(\\b[{letters.upper()}]+\\b(?![ ]))" # containing letters (no individual character limit)
    
    print(letter_regex)
    containing = f"""
    SELECT * FROM ({table_insert(table)}) 
    WHERE library.length <= {len(letters)} 
    AND
    library.word REGEXP '{letter_regex}';
    """
    return containing
# TABLE INPUT FUNCTIONS
def get_words_by_length(table : str, length : int) -> str:
    out = f"""
    SELECT * FROM ({table_insert(table)}) 
    WHERE {table}.length = {length};
    """
    return out 

def sort_by_points(table : str) -> str:
    out = f"""
    SELECT * FROM ({table_insert(table)})
    ORDER BY points DESC;
    """
    return out

def sort_by_length(table : str) -> str:
    out = f"""
    SELECT * FROM ({table_insert(table)})
    ORDER BY length DESC;
    """
    return out

def table_insert(table: str):
    """
    Allows a clean insert from one table into another by eliminating the close statement
    """
    return table.replace(";", "")

def get_all_possible_words(table : str, letters):
    
    letter_and_count = {}
    for i in letters:
        if i in letter_and_count:
            letter_and_count.update({i : letter_and_count[i] + 1})
        else:
            letter_and_count.update({i : 1})
    regex = ""
    
    words_with_letters = get_words_containing(table,"BIITEHZ")
    for i in letter_and_count.keys():
        
        regex += f"(\\b(?=(?:\w*{i})"+"{"+f"{letter_and_count[i]+1}"+",})(\w+))|"
    regex = regex[:-1]
    print(regex)
    #out_table = 
    out = f"""
    SELECT * FROM ({table_insert(words_with_letters)})
    WHERE 
    word NOT REGEXP '{regex}';
    """
    
    return out
with open('Collins Scrabble Words (2019) with definitions.txt') as f:
    definitions = f.readlines()
f.close()
    
    

# MAIN / TESTING

# Database
scrabbleDb = create_connection('scrabble_cheater.db')
scrabbleDb.create_function("REGEXP", 2, regexp)

# create trables
#execute_query(scrabbleDb, create_scrabble_library_table)
#execute_query(scrabbleDb, create_scrabble_dictonary_table)

# populate table 
#with open ('Collins Scrabble Words (2019).txt') as f:
#   words = f.readlines()
# DONE
#for i in words:
    #if i != words[0] or i == "\n":
        #execute_query(scrabbleDb, add_scrabble_word(i.strip()))
#f.close()

# print table 
test_output = execute_read_query(scrabbleDb, get_all_possible_words("library","BIITEHZ"))
#sort_by_length(get_words_containing("library","BIITEHZ")))
print(test_output)