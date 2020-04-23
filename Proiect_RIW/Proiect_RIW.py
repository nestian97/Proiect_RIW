#------------------------------------Import libraries-------------------------------------------------
import os
import sys
# from nltk.stem import WordNetLemmatizer
# from nltk.tokenize import word_tokenize
from nltk import PorterStemmer
import json
import shutil
from datetime import datetime
import time
import multiprocessing
from multiprocessing import Pool
import pymongo
from copy import copy
import math
import operator
import collections
from tkinter import *

#-------------------------------------Global Variables-----------------------------------------------
words_counter = {}
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
indirect_index_pozitional["term"] = {}
indirect_index_cantitativ = []
#indirect_index_cantitativ["term"] = {}
paths_direct_index = {}
#lemmatizer = WordNetLemmatizer()
operators, operands = [], []
operands_dict = {}
ps = PorterStemmer() #
result = set()
direct_index_coll = None
paths_direct_index_coll = None
indirect_index_cantitativ_coll = None
indirect_index_pozitional_coll = None
myclient = None
mydb = None
direct_index_coll = None
indirect_index_cantitativ_coll = None
indirect_index_pozitional_coll = None
info_collection = None
documents = []
number_of_files = 0
tf = {}
idf = {}
asoc_vector = {}
asoc_vector_query = {}
eucl = {}
root = Tk()
root.title('Proiect RIW')
info_from_mongo = {}
#------------------------------------Functions-------------------------------------------------------
def connect_to_db():
    global myclient
    global mydb
    global direct_index_coll
    global indirect_index_pozitional_coll
    global indirect_index_cantitativ_coll
    global info_collection
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]
    for collection in mydb.list_collection_names():
        mydb[collection].drop()
    direct_index_coll = mydb["direct_index"]
    indirect_index_cantitativ_coll = mydb['indirect_index_cantitativ']
    indirect_index_pozitional_coll = mydb['indirect_index_pozitional']
    info_collection = mydb['info_collection']
def create_subdirectories():
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
                    file_path = os.path.join(dir,current)
                    if counter%4 == 0:
                        id_document+=1
                        words['ID'+str(id_document)] = {}
                    paths_direct_index[file_path.replace('.txt','')] = 'ID'+str(id_document)
                    words['ID'+str(id_document)][file_path.replace('.txt','')] = {}
                    counter+=1
                except Exception as e:
                    print(e)
                    pass
    print(len(queue))
def Count_Words(args):
    file_path = args[0] + '.txt'
    words_v2 = {}
    print (file_path)
    with open(file_path, 'r', encoding="utf-8",errors='ignore') as file:
        letter = file.read(1).lower()
        word = ''
        while letter != '':
            if (letter >= 'a' and letter <= 'z') or letter.isdigit():  # or letter == "'" or letter == '/' :
                word += letter
            else:
                if word in args[3]:
                    if word not in words_v2:
                        words_v2[word] = 1
                    else:
                        words_v2[word] += 1
                else:
                    if word != '' and word not in args[2] and len(word) > 1:
                        word = ps.stem(word)
                        # Aici o sa aduc cuvantul la forma canonica
                        if word not in words_v2:
                            words_v2[word] = 1
                        else:
                            words_v2[word] += 1
                word = ''
            letter = file.read(1).lower()
    return words_v2,args[1],args[0]

def Create_Direct_Index():
    no_of_proc = multiprocessing.cpu_count() - 1
    pool_obj = Pool(no_of_proc)
    args = []
    paths_for_args = [path for path in words.keys()]
    for current_path_for_args in paths_for_args:
        for second_level_key in words[current_path_for_args].keys():
            args.append([second_level_key,current_path_for_args, stop_words,exception_words])

    #args = [(words[key],key)for x in y]
    result = pool_obj.map_async(Count_Words, args)
    while True:
        if result.ready():
            print(len(result.get()))
            for job_result in result.get():
                #print(job_result)
                words[job_result[1]][job_result[2].replace('.txt','')] = {}
                words[job_result[1]][job_result[2].replace('.txt','')].update(job_result[0])
                #words
            print("Done")
            break
        else:
            time.sleep(0.1)


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


# def create_indirect_index(dict,key):
#     for word in dict:
#         if word not in indirect_index_cantitativ:
#
#             indirect_index_cantitativ[word] = {}
#             indirect_index_cantitativ[word][key] = dict[word]
#             indirect_index_pozitional[word] = []
#             indirect_index_pozitional[word].append(key)
#         else:
#             indirect_index_cantitativ[word][key] = dict[word]
#             if(key not in indirect_index_pozitional[word] ):
#                 indirect_index_pozitional[word].append(key)


def create_indirect_index_new(dict,key):
    for word in dict:
        gasit = False
        for index,value in enumerate(indirect_index_cantitativ):
            if word != value['term']:
                continue
            else:
                gasit = True
                to_insert = {}
                to_insert['d'] = key
                to_insert['count'] = dict[word]
                indirect_index_cantitativ[index]['docs'].append(to_insert)
                break
        if gasit is False:
            #print("Odata")
            to_insert = {}
            to_insert['term'] = word
            to_insert['docs'] = []
            doc_to_insert = {}
            doc_to_insert['d'] = key
            doc_to_insert['count'] = dict[word]
            to_insert['docs'].append(doc_to_insert)
            indirect_index_cantitativ.append(to_insert)

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
    #print(stop_words)
    #sentence = input("Sentence: ")
    global operators
    global operands
    operands,operators = [], []
    sentence = textBox.get("1.0","end-1c")
    textBox.delete(END)
    textBox2.delete("1.0","end-1c")
    print (sentence)
    word = ''
    for char in sentence:
        char = char.lower()
        if (char >='a' and char <='z') or (char >='A' and char <= 'Z') or (char>='0' and char <='9'):
            word += char
        else:
            if (char == "!" or char == "&" or char == "|") and word !='':
                operators.append(char)
                if word in exception_words:
                    operands.append(word.lower())
                else:
                    if word not in stop_words:
                    # Aduc cuvantul la forma canonica
                        word = ps.stem(word)
                        operands.append(word.lower())
                    else:
                        del operators[len(operators) - 2]
                word = ''
            else:
                sys.exit('Sirul introdus este gresit')

    if word in exception_words:
        operands.append(word.lower())
        word = ''
    else:
        if word not in stop_words:
            # Aduc cuvantul la forma canonica
            word = ps.stem(word)
            operands.append(word)
            word = ''
    if len(operands) == len(operators) and len(operators)!=0:
        del operators[-1]

def check_for_words():
    for operand in operands:
        for elem in indirect_index_cantitativ:
            if operand == elem['term']:
                operands_dict[operand] = set()
                for doc in elem['docs']:
                    operands_dict[operand].add(doc['d'])
                break

def boolean_search():
    readSentence()
    check_for_words()
    global result
    parser = 1
    try:
        result = result.union(operands_dict[operands[0]])
    except:
        print("Cuvantul nu se gaseste in indexul indirect")
    #print(operands_dict[operands[0]])
    for operator in operators:
        if operator == '|':
            try:
                result = result.union(operands_dict[operands[parser]])
            except:
                print("Cuvantul nu se gaseste in indexul indirect")
            print ('Sau')
        elif operator == '!':
            try:
                #interm_result = set(files).difference(operands_dict[operands[parser]])
                if len(result) == 0:
                    pass
                else:
                    result = result.difference(operands_dict[operands[parser]])
            except:
                print("Cuvantul nu se gaseste in indexul indirect")
            print("Negat")
        else:
            pass
            try:
                if len(result) == 0:
                    result = result.union(operands_dict[operands[parser]])
                else:
                    result = result.intersection(operands_dict[operands[parser]])
            except:
                print("Cuvantul nu se gaseste in indexul indirect")
            print("AND")
        parser += 1
    print(result)

def boolean_search_mongo():
    readSentence()
    result2 = None
    print (operands)
    global result
    list_of_docs = []
    words_to_found = {}
    not_words = []

    for index,elem in enumerate(operands):
        words_to_found["term"] = elem
        if operators != []:
            if(operators[index-1] == '!') and index > 0 :
                not_words.append(words_to_found)
                continue
        list_of_docs.append(copy(words_to_found))
    #print (list_of_docs)
    result_not = None
    query = indirect_index_cantitativ_coll.aggregate([{"$match": {"$or": list_of_docs}},
                                                  {"$group": {"_id": "ss", "documents":{"$push":"$docs.d"}}},
                                                  {"$unwind": "$documents"},
                                                  {"$unwind": "$documents"},
                                                  {"$group": {"_id":"$_id","docs":{"$addToSet":"$documents"}}},
                                                  {"$project": {"_id": 0}}])

    if (len(not_words)>0):
        result_not = indirect_index_cantitativ_coll.aggregate([{"$match": {"$or": not_words}},
                                                      {"$group": {"_id": "ss", "documents":{"$push":"$docs.d"}}},
                                                      {"$unwind": "$documents"},
                                                      {"$unwind": "$documents"},
                                                      {"$group": {"_id":"$_id","docs":{"$addToSet":"$documents"}}},
                                                      {"$project": {"_id": 0}}])
    for res in query:
        if result_not is not None:
            for not_res in result_not:
                res = set(res['docs'])
                not_res = set(not_res['docs'])
                print(res)
                print(not_res)
                result = res.difference(not_res)
                #return result
        else:
            result = set(res['docs'])
            #return res
    #print(result)

    #return result
def calculate_tf_and_idf():

    for cuvant in indirect_index_cantitativ:
        tf[cuvant["term"]] = {}
        for doc in cuvant["docs"]:
            tf[cuvant["term"]][doc["d"]] = float(doc["count"])/words_counter[doc["d"]]
        idf[cuvant["term"]] = math.log(number_of_files/(len(cuvant["docs"])))
def calculate_asoc_vector(dict,doc):

    asoc_vector[doc] = {}
    for word in dict:
        asoc_vector[doc][word] = tf[word][doc] * idf[word]
    #print(asoc_vector)


def calculate_tf_idf_query():
    global info_from_mongo
    temp = {}
    for word in operands:
        if word not in temp:
            temp[word] = 1
        else:
            temp[word] += 1
    tf_query = {}
    global asoc_vector_query
    for word in temp:
        print (word)
        tf_query[word] = float(temp[word])/len(operands)
        try:
            idf_query = info_from_mongo['idf'][word]
            asoc_vector_query[word] = tf_query[word] * idf_query
        except:
            print("Cuvantul nu este in tf")

    calc_norma_euclidiana(temp,'query')
def vectorial_search():
    global info_from_mongo
    boolean_search_mongo()
    calculate_tf_idf_query()
    cos_doc = {}
    for doc in result:
        cos_doc[doc] = 0
        for word in asoc_vector_query:
            try:
                cos_doc[doc] += (asoc_vector_query[word] * info_from_mongo['asoc_vector'][doc][word])
                cos_doc[doc] /= (eucl[doc] * eucl['query'])
            except:
                #print("Cuvantul din interogare nu se gaseste in document")
                pass

    sorted_dict = sorted(cos_doc.items(), key=lambda x: x[1],reverse = True)
    #print(sorted_dict)
    #print(eucl)
    #print(idf)
    #print(tf)
    text_to_print = ''
    for item in sorted_dict:
        text_to_print +=str(item) + "\n"
    textBox2.insert(END,text_to_print)
    #textBox2.insert("\n")
def calc_norma_euclidiana(dict,key):
    global info_from_mongo
    suma = 0.0
    global eucl
    for word in dict:
        suma += dict[word] * dict[word]
    eucl[key] = math.sqrt(suma)



#--------------------------------------------Main Function-----------------------------------------------
if __name__ == "__main__":
    connect_to_db()
    time_start = datetime.now()
    read_stopwords_or_exceptions(exceptions_words_path, exception_words)
    read_stopwords_or_exceptions(stop_words_path, stop_words)
    create_subdirectories() # Parse the entire structure of directories
    Create_Direct_Index()  # Call the multiprocess function that will make the direct index

    for key in words:
        temp_index = mydb['{}'.format(key)]
        temp_index.insert(words[key])

    direct_index_coll.insert(paths_direct_index)
    cursor = direct_index_coll.find()
    for doc in cursor:
        direct_index = dict(doc)
        del direct_index['_id']

    for key in direct_index:
        cursor_mongo = mydb[direct_index[key]].find({key: {"$exists": True}}, {key: 1})
        for temp_dict in cursor_mongo:
            temp_dict = dict(temp_dict)
            del temp_dict['_id']
            for working_key in temp_dict:
                create_indirect_index_new(temp_dict[working_key],working_key)
                words_counter[working_key] = len(temp_dict[working_key])
                print(working_key)
                number_of_files += 1

    calculate_tf_and_idf()
    for key in direct_index:
        cursor_mongo = mydb[direct_index[key]].find({key: {"$exists": True}}, {key: 1})
        for temp_dict in cursor_mongo:
            temp_dict = dict(temp_dict)
            del temp_dict['_id']
            for working_key in temp_dict:
                calculate_asoc_vector(temp_dict[working_key],working_key)
                calc_norma_euclidiana(temp_dict[working_key],working_key)
    info_to_mongo = {}
    info_to_mongo['tf'] = tf
    info_to_mongo['idf'] = idf
    info_to_mongo['asoc_vector'] = asoc_vector
    info_collection.insert(info_to_mongo)
    for key in ['tf','idf','asoc_vector']:
        cursor_mongo = info_collection.find({key: {"$exists": True}}, {key: 1,"_id":0})
        for temp_dict in cursor_mongo:
            temp_dict = dict(temp_dict)
            info_from_mongo.update( temp_dict)

    #json_dump(indirect_index_cantitativ,'xxx.json')
    indirect_index_cantitativ_coll.insert_many(indirect_index_cantitativ)
    #indirect_index_pozitional_coll.insert_many(indirect_index_pozitional)
    #User Interface

    textBox = Text(root, height=3, width=40)
    textBox2 = Text(root, height=10, width=90)
    var = StringVar()
    var2=StringVar()
    label = Label(root, textvariable=var, relief=RAISED,height = 1, width = 40)
    label2 = Label(root, textvariable=var2, relief=RAISED,height = 1, width = 40)
    var.set("Text to be found")
    #label.pack()
    textBox.pack()
    var2.set("Result")
    #label2.pack()
    textBox2.pack()
    buttonCommit = Button(root, height=1, width=10, text="Search",
                          command=lambda: vectorial_search())
    # command=lambda: retrieve_input() >>> just means do this when i press the button
    buttonCommit.pack()

    mainloop()

    #/User interface
    #vectorial_search()
    print(operators)
    stop_time = datetime.now()
    print(stop_time-time_start)
