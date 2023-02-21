# scrabble cheater SQL database
import time
import sqlite3
from sqlite3 import Error
import re

# --- Connections and  Read/Execute ---
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

# ------------------------------------------        

# --- Table Creation ---
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
   word TEXT FOREIGN KEY,
   definition TEXT
   );   
"""
# ------------------------------------------        

# ADDING TO COLLECTION 

tile_dict = {
    "A" : 1 ,"B" : 3,"C" : 3,"D" : 2,
    "E" : 1 ,"F" : 4,"G" : 2,"H" : 4,
    "I" : 1 ,"J" : 8,"K" : 5,"L" : 1,
    "M" : 3 ,"N" : 1,"O" : 1,"P" : 3,
    "Q" : 10,"R" : 1,"S" : 1,"T" : 1,
    "U" : 1 ,"V" : 4,"W" : 4,"X" : 8,
    "Y" : 4 ,"Z" : 10
}
# --- Adding to table ---
def add_word_from_list(words : list):
    out = f"""
    INSERT INTO 
        library (word, points, length)
    VALUES
    """    
    for i in words:
        points = 0
        for i in word:
            points += tile_dict[i]        
        adding = f" ('{i}', '{points}', '{len(i)}')" 
    out += adding + ";"
    return out

def add_scrabble_word(word : str):
    
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

# --- Queries ---
def get_word(word : str) -> str:
    select_word =  f"SELECT * FROM library WHERE library.word = {word};"
    return select_word

def get_word_def(word : str) -> str:
    select_def = f"SELECT * FROM definitions WHERE definition.word = {word};"
    return select_def

def table_insert(table: str):
    """
    Allows a clean insert from one table into another by eliminating the close statement
    """
    return table.replace(";", "")

def get_words_excluding(table : str, letters : str) -> str:
    """
    Returns a table containing all words excluding the letters provided 
    """
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
def get_words_containing_unlimited(table : str, letters : str) -> str: 
    """
    Returns a table containing words with all letters provided (exclusive of other letters) 
    without a character limit
    """
    letter_regex = f"(\\b[{letters.upper()}]+\\b(?![ ]))" # containing letters (no individual character limit)
    
    #print(letter_regex)
    containing = f"""
    SELECT * FROM ({table_insert(table)}) 
    WHERE 
    library.word REGEXP '{letter_regex}';
    """
    return containing

def get_words_containing(table : str, letters : str) -> str: 
    """
    Returns a table containing words with all letters provided (exclusive of other letters) 
   
    """
    letter_regex = f"(\\b[{letters.upper()}]+\\b(?![ ]))" # containing letters (no individual character limit)
    
    #print(letter_regex)
    containing = f"""
    SELECT * FROM ({table_insert(table)}) 
    WHERE library.length <= {len(letters)} 
    AND
    library.word REGEXP '{letter_regex}';
    """
    return containing
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


def get_all_words_with_blank(table : str, letters : str) -> str:
    
    out = f"""
    SELECT * FROM ({table_insert(get_all_possible_words(table,letters))}) """
    
    for i in tile_dict.keys():
        #union all together
        #print(letters+i)
        out += f" UNION {table_insert(get_all_possible_words(table, (letters+i) ))}"

    out += ";"
    #print(out)
    return out
    
    
def get_all_possible_words(table : str, letters):
    """
    Returns a table with all possible words  int the scrabble word list containing 
    the letters provided, letter count sensitive*. 
    * Count of letters such as E or EE matter in finding words 
    """
    
    letter_and_count = {}
    for i in letters:
        if i in letter_and_count:
            letter_and_count.update({i : letter_and_count[i] + 1})
        else:
            letter_and_count.update({i : 1})
    regex = ""
    
    words_with_letters = get_words_containing(table, letters)
    for i in letter_and_count.keys():
        
        regex += f"(\\b(?=(?:\w*{i})"+"{"+f"{letter_and_count[i]+1}"+",})(\w+))|"
    regex = regex[:-1]
    #print(regex)
    #out_table = 
    out = f"""
    SELECT * FROM ({table_insert(words_with_letters)})
    WHERE 
    word NOT REGEXP '{regex}';
    """
    
    return out

def get_points_with_blank(table : str, letters : str):
    words_with_blank = execute_read_query(scrabbleDb, get_all_words_with_blank(table, letters)) #get_points_with_blank(table, letters)
    word_list_adjusted = []

    def get_extra_letter(word, letters):
        """ 
        Compares the letter contents of word to given collection of characters and 
        Returns all extra letters within the word, None if no extra letters found
        """
        used_letter_bank = '' 
        original_letters = letters
        extra_letter = None
        
        for letter in word:
            # CHECK IF LETTER IS ALREADY CHECKED
            if letter not in used_letter_bank:
                used_letter_bank += letter
                letter_higher_than_count = (word.count(letter) > original_letters.count(letter))
                new_letter = letter not in original_letters
                
                if letter_higher_than_count or new_letter:
                    extra_letter = letter
                    break  # exit loop when extra letter is found
        
        return extra_letter        
         
                
    def highlight_extra_letter_in_word(word, extra_letter):
        index_of_extra_letter = word.rindex(extra_letter)
        word_with_extra_letter_highlighted = word[:index_of_extra_letter] + f'"{extra_letter}"' + word[index_of_extra_letter + 1:]
        return word_with_extra_letter_highlighted
            
    for word_set in words_with_blank:
        # FIND THE EXTRA LETTER
        just_the_word = word_set[0]
        extra_letter = get_extra_letter(just_the_word, letters)
       
        if extra_letter != None:
            highlighted_word = highlight_extra_letter_in_word(just_the_word, extra_letter) # HIGHLIGHT THE EXTRA LETTER
            new_points = word_set[1] - tile_dict[extra_letter] # POINTS ADJUSTMENT
            word_length = word_set[2]
            
            word_list_adjusted.append( (highlighted_word, new_points, word_length) ) # ADD ADJUSTMENT TO WORD LIST
        else:
            word_list_adjusted.append(word_set)
        
    return word_list_adjusted

'''with open('Collins Scrabble Words (2019) with definitions.txt') as f:
    definitions = f.readlines()
f.close()'''

# CONNECT TO DATABASE  
scrabbleDb = create_connection('scrabble_cheater.db')
scrabbleDb.create_function("REGEXP", 2, regexp)   

# CREATE TABLES
"""
execute_query(scrabbleDb, create_scrabble_library_table)
execute_query(scrabbleDb, create_scrabble_dictonary_table)
"""

# POPULATE TABLE FROM FILE
"""
with open ('Collins Scrabble Words (2019).txt') as f:
   words = f.readlines()
 DONE
for i in words:
    if i != words[0] or i == "\n":
        execute_query(scrabbleDb, add_scrabble_word(i.strip()))
f.close()
"""

# MAIN / TESTING
def main():

    
    test_output = execute_read_query(scrabbleDb, get_all_possible_words("library","DERPA"))
    
    #sort_by_length(get_words_containing("library","BIITEHZ")))
    print("DERPA without blank:",test_output)
    
    test_blank = execute_read_query(scrabbleDb, get_all_words_with_blank("library", "DERPA"))
    print("DERPA with blank:",test_blank)
    
    
    start = time.time()
    print("Starting timer...")
    
    test_blank_with_points_adjusted = get_points_with_blank("library", "DERPA")
    print("DERPA points adjusted for blank:",test_blank_with_points_adjusted)
    
    end = time.time() - start 
    print ("Time taken:",end)



if __name__ == "__main__":
    main()
