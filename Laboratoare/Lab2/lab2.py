#--------------------------------------Import libraries------------------------------------------------
import os
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk
import json
import shutil
from datetime import datetime
from multiprocessing import Manager,Pool
import multiprocessing
import time
#-------------------------------------Global Variables-----------------------------------------------
stop_words_path = r'stopwords'
exceptions_words_path = r'exceptions'
main_path = r'structura'
exception_words = []
stop_words = []
words = {}
indirect_index_pozitional = {}
indirect_index_cantitativ = {}
paths_direct_index = {}
lemmatizer = WordNetLemmatizer()
#------------------------------------Functions-------------------------------------------------------
def create_subdirectories():
    queue = [main_path]
    for dir in queue:
        for current in os.listdir(dir):
            if os.path.isdir(os.path.join(dir,current)):
                queue.append(os.path.join(dir,current))
            elif os.path.isfile(os.path.join(dir,current)):
                try:

                    file_path = os.path.join(dir,current)
                    words[file_path] = {}
                    count_words_lab2(words[file_path],file_path)
                except Exception as e:
                    #print(e)
                    pass
                #Aici o sa prelucrez fisierul

def read_stopwords_or_exceptions(file_path,list_of_words):
    with open(file_path,'r',encoding="utf-8",errors='ignore') as file:
        word = ''
        letter = file.read(1)
        while letter != '':
            if letter != '\n':
                word += letter.lower()
            else:
                list_of_words.append(word)
                word = ''
            letter = file.read(1)

def count_words_lab2(dict,path):
    with open(path, 'r', encoding="utf8") as file:
        letter = file.read(1).lower()
        word = ''
        while letter != '':
            if (letter >='a' and letter <='z') or (letter.isdigit()):# or letter == "'" or letter == '/' :
                word += letter
            else:
                if word in exception_words:
                    if word not in dict:
                        dict[word] = 1
                    else:
                        dict[word] += 1
                else:
                    if word != '' and word not in stop_words and len(word)>1:
                        if word not in dict:
                            dict[word] = 1
                        else:
                            dict[word] += 1
                        #Aici o sa trebuiasca sa aduc cuvantul la forma canonica
                word = ''
            letter = file.read(1).lower()


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

#--------------------------------------------Main Function-----------------------------------------------
if __name__ == "__main__":
    time_start = datetime.now()
    read_stopwords_or_exceptions(exceptions_words_path, exception_words)
    read_stopwords_or_exceptions(stop_words_path, stop_words)
    check_if_directory_exists('Direct_Index')
    check_if_directory_exists('Indirect_Index')
    create_subdirectories() # Parse the entire structure of directories
    for key in words:
        print(key)
    print(words[key])
    stop_time = datetime.now()
    print(stop_time-time_start)




