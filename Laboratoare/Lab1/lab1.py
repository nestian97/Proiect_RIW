words = {}
def count_words(path):
    with open(path, 'r', encoding="utf8") as file:
        letter = file.read(1).lower()
        word = ''
        while letter != '':
            if (letter >='a' and letter <='z') or (letter.isdigit()):# or letter == "'" or letter == '/' :
                word += letter
            else:
                if word != ''  and len(word)>1:
                    if word not in words:
                        words[word] = 1
                    else:
                        words[word] += 1
                        #Aici o sa trebuiasca sa aduc cuvantul la forma canonica
                word = ''
            letter = file.read(1).lower()
if __name__ == "__main__":
    count_words(r'fisiere_alpd/1.txt')
    print (words)

