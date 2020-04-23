#--------------------------------------Import libraries------------------------------------------------
import os
import sys
# from nltk.stem import WordNetLemmatizer
# from nltk.tokenize import word_tokenize
import nltk
from nltk import PorterStemmer
import json
import shutil
from datetime import datetime
import pymongo
import pickle
import collections
ps = PorterStemmer()
#-------------------------------------Global Variables-----------------------------------------------
stop_words_path = r'stopwords'
exceptions_words_path = r'exceptions'
main_path = r'dummy_struct'
direct_index_dir = r'Direct_Index'
indirect_index_dir = r'Indirect_Index'
direct_index_path = os.path.join(direct_index_dir,r'direct_index.json')
indirect_index_pozitional_path = r'Indirect_Index/indirect_index_pozitional.json'
indirect_index_cantitativ_path = r'Indirect_Index/indirect_index_cantitativ.json'
exception_words = []
stop_words = []
words = {}
indirect_index_pozitional = {}
indirect_index_cantitativ = {}
paths_direct_index = {}
operands,operators,operands_dict = [], [], {}
files = []
result = set()
#lemmatizer = WordNetLemmatizer()
#------------------------------------Functions-------------------------------------------------------
def create_subdirectories():
    global files
    counter = 0
    id_document = 0
    queue = [main_path]
    for dir in queue:
        dir = os.path.abspath(dir)
        for current in os.listdir(dir):
            if os.path.isdir(os.path.join(dir,current)):
                queue.append(os.path.join(dir,current))
            elif os.path.isfile(os.path.join(dir,current)):
                try:

                    print (os.path.join(dir,current))
                    file_path = os.path.join(dir,current)
                    files.append(file_path)
                    if counter%4 == 0:
                        id_document+=1
                        words['ID'+str(id_document)] = {}
                    paths_direct_index[file_path] = os.path.join(direct_index_dir, 'ID' + str(id_document) + '.json')
                    words['ID'+str(id_document)][file_path] = {}
                    create_direct_index_v2(words['ID'+str(id_document)][file_path],file_path)
                    counter+=1
                except Exception as e:
                    print(e)
                    pass
                #Aici o sa prelucrez fisierul

def read_stopwords_or_exceptions(file_path,list_of_words):
    with open(file_path,'r') as file:
        word = ''
        letter = file.read(1)
        while letter != '':
            if letter != '\n':
                word += letter.lower()
            else:
                list_of_words.append(word)
                word = ''
            letter = file.read(1)

def create_direct_index_v2(words_v2, file_path):
    with open(file_path, 'r', encoding="utf-8",errors='ignore') as file:
        letter = file.read(1).lower()
        word = ''
        while letter != '':
            if (letter >= 'a' and letter <= 'z') or letter.isdigit():  # or letter == "'" or letter == '/' :
                word += letter
            else:
                if word in exception_words:
                    if word not in words_v2:
                        words_v2[word] = 1
                    else:
                        words_v2[word] += 1
                else:
                    if word != '' and word not in stop_words and len(word) > 1 :
                        word = ps.stem(word)
                        # Aici o sa trebuiasca sa aduc cuvantul la forma canonica
                        if word not in words_v2:
                            words_v2[word] = 1
                        else:
                            words_v2[word] += 1
                word = ''
            letter = file.read(1).lower()

def json_dump(data, path, sort_keys=False, indent=4):
    """
    Dump data to json file in path
    :param data: data to be dumped
    :param path: path to save the dumped file
    :param sort_keys: if you want sorting, default is False
    :param indent: indentation to be used, default is 4 spaces
    :return: None
    """
    with open(path, 'w') as dump_file:
        json.dump(data, dump_file, sort_keys=sort_keys, indent=indent)

def json_load(json_file,key):
    """
    Function to load json dumped file
    :param json_file:
    :return:
    """
    with open(json_file) as json_loaded_file:
        try:
            if key is None:
                data = json.load(json_loaded_file)
            else:
                data = json.load(json_loaded_file)[key]
            json_loaded_file.close()
            return data
        except Exception as e:
            print(e)
            return None

def create_indirect_index(dict,key):
    for word in dict:
        if word not in indirect_index_cantitativ:
            indirect_index_cantitativ[word] = {}
            indirect_index_cantitativ[word][key] = dict[word]
            indirect_index_pozitional[word] =[]
            indirect_index_pozitional[word].append(key)
        else:
            indirect_index_cantitativ[word][key] = dict[word]
            indirect_index_pozitional[word].append(key)


def check_if_directory_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        for thing in  os.listdir(path):
            file_path = os.path.join(path,thing)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
def readSentence():
    print(stop_words)
    sentence = input("Sentence: ")
    word = ''
    for char in sentence:
        char = char.lower()
        if (char >='a' and char <='z') or (char >='A' and char <= 'Z') or (char>='0' and char <='9'):
            word += char
        else:
            if (char == "!" or char == "&" or char == "|") and word !='':
                operators.append(char)
                if word not in stop_words:
                    if word in exception_words:
                        operands.append(word.lower())
                    else:
                        # Aduc cuvantul la forma canonica
                        word = ps.stem(word)
                        operands.append(word.lower())

                else:
                    del operators[len(operators) - 2]
                word = ''
            else:
                sys.exit('Sirul introdus este gresit')
    if word not in stop_words:
        if word in exception_words:
            operands.append(word.lower())
            word = ''
        else:
            # Aduc cuvantul la forma canonica
            word = ps.stem(word)
            operands.append(word)
            word = ''
    if len(operands) == len(operators) and len(operators)!=0:
        del operators[-1]

def check_for_words():
    for operand in operands:
        if operand in indirect_index_pozitional:
            operands_dict[operand] = set()
            operands_dict[operand] = set(indirect_index_pozitional[operand])

def boolean_search():
    readSentence()
    check_for_words()
    global result
    parser = 1
    try:
        result = result.union(operands_dict[operands[0]])
    except:
        print("Cuvantul nu se gaseste in indexul indirect")
    for operator in operators:
        if operator == '|':
            try:
                result = result.union(operands_dict[operands[parser]])
            except:
                print("Cuvantul nu se gaseste in indexul indirect")
            print (operands[parser])
        elif operator == '!':
            try:
                #interm_result = set(files).difference(operands_dict[operands[parser]])
                if len(result) == 0:
                    result = result.union(operands_dict[operands[parser]])
                else:
                    result = result.difference(operands_dict[operands[parser]])
            except:
                print("Cuvantul nu se gaseste in indexul indirect")
            print("Negat")
        else:
            try:
                if len(result) == 0:
                    result = result.union(operands_dict[operands[parser]])
                else:
                    result = result.intersection(operands_dict[operands[parser]])
            except:
                print("Cuvantul nu se gaseste in indexul indirect")
            print("AND")
        parser+=1





#--------------------------------------------Main Function-----------------------------------------------
if __name__ == "__main__":
    time_start = datetime.now()
    #connect_to_db()
    read_stopwords_or_exceptions(exceptions_words_path, exception_words)
    read_stopwords_or_exceptions(stop_words_path, stop_words)
    check_if_directory_exists(direct_index_dir)
    check_if_directory_exists(indirect_index_dir)
    create_subdirectories() # Parse the entire structure of directories
    #connect_to_db()
    for key in words:
        json_dump(words[key],os.path.join(direct_index_dir,key +'.json')) #Dump the direct index dictionary into a json
        json_dump(paths_direct_index,direct_index_path) #Dump the direct index paths into a json
    direct_index = json_load(direct_index_path,None)
    for key in direct_index:
        temp_dict = json_load(direct_index[key],key)
        create_indirect_index(temp_dict,key)
    json_dump(indirect_index_pozitional,indirect_index_pozitional_path)
    json_dump(indirect_index_cantitativ,indirect_index_cantitativ_path)
    print (operands)
    print (operators)
    boolean_search()
    print(result)

    stop_time = datetime.now()
    print(stop_time-time_start)
