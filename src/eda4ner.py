# Easy data augmentation techniques for text classification
# Jason Wei and Kai Zou

import random
from random import shuffle
random.seed(1)

#stop words list
stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 
            'ours', 'ourselves', 'you', 'your', 'yours', 
            'yourself', 'yourselves', 'he', 'him', 'his', 
            'himself', 'she', 'her', 'hers', 'herself', 
            'it', 'its', 'itself', 'they', 'them', 'their', 
            'theirs', 'themselves', 'what', 'which', 'who', 
            'whom', 'this', 'that', 'these', 'those', 'am', 
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 
            'have', 'has', 'had', 'having', 'do', 'does', 'did',
            'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
            'because', 'as', 'until', 'while', 'of', 'at', 
            'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 
            'above', 'below', 'to', 'from', 'up', 'down', 'in',
            'out', 'on', 'off', 'over', 'under', 'again', 
            'further', 'then', 'once', 'here', 'there', 'when', 
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 
            'very', 's', 't', 'can', 'will', 'just', 'don', 
            'should', 'now', '']

#cleaning up text
import re
def get_only_chars(line):

    clean_line = ""

    line = line.replace("’", "")
    line = line.replace("'", "")
    line = line.replace("-", " ") #replace hyphens with spaces
    line = line.replace("\t", " ")
    line = line.replace("\n", " ")
    line = line.lower()

    for char in line:
        if char in 'qwertyuiopasdfghjklzxcvbnm ':
            clean_line += char
        else:
            clean_line += ' '

    clean_line = re.sub(' +',' ',clean_line) #delete extra spaces
    if clean_line[0] == ' ':
        clean_line = clean_line[1:]
    return clean_line

#*****************************
# UMLS Synonyms replacement  #
#*****************************


#from QuickUMLS.quickumls import QuickUMLS
import nltk
matcher = None#QuickUMLS("/home/tk2624/tools/QuickUMLS",threshold=0.8,similarity_name ='cosine',overlapping_criteria='length')

def ngram_index(words, ngram):
    return list(nltk.ngrams(words, len(ngram))).index(tuple(ngram))

def isSubstring(s1, s2): 
    M = len(s1) 
    N = len(s2) 
  
    # A loop to slide pat[] one by one  
    for i in range(N - M + 1): 
  
        # For current index i, 
        # check for pattern match  
        for j in range(M): 
            if (s2[i + j] != s1[j]): 
                break
              
        if j + 1 == M : 
            return i 
  
    return False

def get_umls_tagging(text,matcher):
    info = matcher.match(text, best_match=True, ignore_syntax=False)
    taggings=[]
    if len(info) == 0:
        return None
    for one_c in info:

        one_c = one_c[0]
    
        result = {"cui":one_c["cui"],"term":one_c["term"]}
        taggings.append(one_c)
    return taggings

from src.Authentication import *
import requests
import json

def get_atoms(apikey,cui):
    AuthClient = Authentication(apikey)
    tgt = AuthClient.gettgt()
    uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = "/rest/content/2019AB"+"/CUI/"+str(cui)+"/atoms"
    query = {'ticket':AuthClient.getst(tgt),'language':'ENG','pageSize':200}
    headers = {"Range": "bytes=0-1"}
    r = requests.get(uri+content_endpoint,params=query,headers=headers)
    r.encoding = 'utf-8'
    items  = json.loads(r.text)
    jsonData = items["result"]
    atoms =[i["name"] for i in jsonData if not re.search("[,;\-\(\)\.\/]",i['name']) and not re.search("NOS",i['name'])  ]# remove sysnonyms with punctuations, or NOS    
    atoms = list(set(atoms))    
    return atoms
#get_atoms(apikey,'C0006142')

def umls_replacement(words,labels,n, apikey):
    sent = " ".join(words)
    #new_labels = labels.copy()
    
    augumented_sents = []
    taggings = get_umls_tagging(sent, matcher)
    num_replaced = 0
    total_num = 1
    if taggings is None:
        return augumented_sents
    atoms_set = []
    cui_set = []
    for i in taggings:
        cui = i["cui"]
        if cui in cui_set:
            continue
        cui_set.append(cui)
        try:
            atoms_raw = get_atoms(apikey,cui)
        except:
            continue

        #remove synnonyms with only case differences
        atoms = [a for a in atoms_raw if not a.lower() == i['term'].lower() and not a.lower()+"s" ==i['term'].lower() and not a.lower() == i['term'].lower()+"s" ]
        if i['term'] in atoms:
            atoms.remove(i['term'])
        
        #print(len(atoms),i['term'],"-------- atoms:",atoms,"\n")
        if len(atoms)>0:
            atoms_set.append({i['term']:atoms})
            total_num=total_num*len(atoms)

    max_num = min(n, total_num)
    
    for _ in range(max_num):
        new_sent = sent
        new_label = labels.copy()

        for i in range(len(atoms_set)):
            
            atom = atoms_set[i]
            term = list(atom.keys())[0]
            atoms = atom[term]        
            synonym = random.choice(atoms)
            
            try:
                a = re.search(synonym.lower(),term.lower())
                b = re.search(term.lower(),synonym.lower())
            except:
                a = True
                b = True
            if re.search("[\^\[\]\(\)\{\}]",synonym) or set(synonym.lower().split(" ")) == set(term.lower().split(" ")) or a == True or b == True or set(synonym.lower().split(" ")).issubset(set(term.lower().split(" "))) or set(term.lower().split(" ")).issubset(set(synonym.lower().split(" "))):
                continue
            #print (":",term)
            try:
                term_index = ngram_index(new_sent.split(" "),term.split(" ") )
            except:
                continue
            
            before_index = term_index
            after_index = term_index+len(term.split(" "))
            syn_label = new_label[before_index:after_index]
            '''
            print (len(new_label),len(new_sent.split(" ")))
            print (new_label)
            print (new_sent)
            print (term,"==",synonym,"===",len(new_sent.split(" ")),term_index,syn_label)
            '''
            if before_index == 0:
                before=["TEMP"]
            else:
                before = new_label[:before_index].copy()
            #print(term,synonym,syn_label)
            if re.search("O\s+.*\-"," ".join(syn_label)) or re.search("\-.*\s+O"," ".join(syn_label)):
                continue # syn span over both O and entities, skip
            elif re.search("^O+$","".join(syn_label)): # non entity span
                before.extend(["O"]*len(synonym.split(" ")))
                before.extend(new_label[after_index:])
            elif len(set(syn_label)) == 1 and re.search("^I\-",syn_label[0]):
                before.extend([syn_label[0]]*len(synonym.split(" ")))
                before.extend(new_label[after_index:])
            else: # both B- and I- or only B-
                if len(syn_label)>1:
                    before.extend([syn_label[0]])
                    before.extend([syn_label[1]]*(len(synonym.split(" "))-1))
                    before.extend(new_label[after_index:])

                else:
                    #print (new_sent)
                    #print (before)
                    #print(syn_label[0])
                    before.extend([syn_label[0]])
                    before.extend([re.sub("^B","I",syn_label[0])]*(len(synonym.split(" "))-1))
                    before.extend(new_label[after_index:])
            if before_index == 0:
                del before[0]
            words= new_sent.split(" ")                 
            new_label = before.copy()
            if before_index >0:
                new_sent = " ".join(words[:before_index])+" "+synonym+" " + " ".join(words[after_index:])
            else:
                new_sent = synonym+" " + " ".join(words[after_index:])
        augumented_sents.append([(new_sent).split(" "),new_label])
    return augumented_sents

     
##########################################################################



########################################################################
# Synonym replacement
# Replace n words in the sentence with synonyms from wordnet
########################################################################

#for the first time you use wordnet
#import nltk
#nltk.download('wordnet')
from nltk.corpus import wordnet 

def synonym_replacement(words,labels,n):
    new_words = words.copy()
    new_labels = labels.copy()
    random_word_list = list(set([word for word in words if word not in stop_words]))
    #print (random_word_list,"***")
    random.shuffle(random_word_list)
    num_replaced = 0
    
    for random_word in random_word_list:
        synonyms = get_synonyms(random_word)
        #print (synonyms,"~~~~~~")
        if len(synonyms) >= 1:
            synonym = random.choice(list(synonyms))
            if len(synonym.split(" "))>1 or  re.search(synonym,random_word) or re.search(random_word,synonym):
                continue
            new_words = [synonym if word.lower() == random_word.lower() else word for word in new_words]
            #print("replaced", "==="+random_word+"===", "with", "==="+synonym+"===")
            num_replaced += 1
        if num_replaced >= n: #only replace up to n words
            break

    #this is stupid but we need it, trust me
    if new_words == words:
        return None,None

    sentence = ' '.join(new_words)
    #sentence = "1---"+sentence
    new_words =( sentence).split(' ')
    
    return new_words,new_labels

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word): 
        for l in syn.lemmas(): 
            synonym = l.name().replace("_", " ").replace("-", " ").lower()
            synonym = "".join([char for char in synonym if char in ' qwertyuiopasdfghjklzxcvbnm'])
            synonyms.add(synonym) 
    if word in synonyms:
        synonyms.remove(word)
    #print("\n==",word,"===", synonyms) 

    return list(synonyms)


########################################################################
# Random deletion
# Randomly delete words from the sentence with probability p
########################################################################

def random_deletion(words,labels, p):

    #obviously, if there's only one word, don't delete it
    if len(words) == 1:
        return words,labels

    #randomly delete words with probability p
    new_words = []
    new_labels=[]
    # dont delete the words which is the begining of an entity(B-tag)
    for i, word in enumerate(words):
        r = random.uniform(0, 1)
        if re.search("^B-",labels[i]):
            new_words.append(word)
            new_labels.append(labels[i])
            continue
        if r > p :
            new_words.append(word)
            new_labels.append(labels[i])
    #if you end up deleting all words, just return a random word
    if len(new_words) == 0:
        rand_int = random.randint(0, len(words)-1)
        return words[rand_int],labels[rand_int]
    sentence = ' '.join(new_words)
    #sentence = "2---"+sentence
    new_words =( sentence).split(' ')
    return new_words,new_labels

########################################################################
# Random swap
# Randomly swap two words in the sentence n times
########################################################################

def random_swap(words,labels, n):
    new_words = words.copy()
    new_labels = labels.copy()
    for _ in range(n):
        new_words = swap_word(new_words)
    sentence = ' '.join(new_words)
    #sentence = "3---"+sentence
    new_words = (sentence).split(' ')
    return new_words,new_labels

def swap_word(new_words):
    random_idx_1 = random.randint(0, len(new_words)-1)
    random_idx_2 = random_idx_1
    counter = 0
    while random_idx_2 == random_idx_1:
        random_idx_2 = random.randint(0, len(new_words)-1)
        counter += 1
        if counter > 3:
            return new_words
    new_words[random_idx_1], new_words[random_idx_2] = new_words[random_idx_2], new_words[random_idx_1] 
    
    return new_words

########################################################################
# Random insertion
# Randomly insert n words into the sentence
########################################################################

def random_insertion(words,labels, n):
    new_words = words.copy()
    new_labels = labels.copy()
    for _ in range(n):
        add_word(new_words,new_labels)
    sentence = ' '.join(new_words)
    #sentence = "4---"+sentence
    new_words = (sentence).split(' ')
    return new_words, new_labels

def add_word(new_words,new_labels):
    synonyms = []
    counter = 0
    while len(synonyms) < 1:
        #generate a random index thats not in the beginning in entities
          
        random_word = new_words[random.randint(0, len(new_words)-1) ]
        synonyms = get_synonyms(random_word)
        counter += 1
        if counter >= 10:
            return
    random_synonym = synonyms[0]
    seed = 1
    random.seed(seed)
    while re.search("B\-",new_labels[random.randint(0, len(new_words)-1)]) :
        seed += 1
        random.seed(seed) 
        if seed > len(new_words):
            break
    random_idx = random.randint(0, len(new_words)-1)
    new_words.insert(random_idx, random_synonym)
    if random_idx==len(new_labels)-1: # insert in the end
        new_labels.insert(random_idx, "O")
    elif new_labels[random_idx+1] == "O":
        new_labels.insert(random_idx, "O")
    else:
        new_labels.insert(random_idx,new_labels[random_idx-1])
    

########################################################################
# main data augmentation function
########################################################################

#0:ori
#1:sr-wordnet
#2:rd
#3:rw
#4:ri
#5:sr-umls

def eda(sentence, label, apikey, alpha_umls = 0.5, alpha_sr=0.5, alpha_ri=0.5, alpha_rs=0.5, p_rd=0.5, num_aug=10):
    
    #sentence = get_only_chars(sentence)
    words = sentence.split(' ')
    
    words = [word for word in words if word != '']
    num_words = len(words)
    
    augmented_sentences = []
    num_new_per_technique = int(num_aug/4)+1
    n_umls = max(1, int(alpha_umls*num_words))
    n_sr = max(1, int(alpha_sr*num_words))
    n_ri = max(1, int(alpha_ri*num_words))
    n_rs = max(1, int(alpha_rs*num_words))
    
    #umls
    new_sents = umls_replacement(words,label,4,apikey)
    if len(new_sents) >0:
        augmented_sentences.extend(new_sents)
    
    #sr
    for _ in range(num_new_per_technique):
        
        a_words,new_label = synonym_replacement(words,label, n_sr)

        if a_words is None:
            continue
        augmented_sentences.append([a_words,new_label])

    #ri
    for _ in range(num_new_per_technique):
        a_words,new_label = random_insertion(words,label, n_ri)
        
        if a_words == words:
            continue
        #print(" ".join(a_words))
        #print(" ".join(new_label))
        augmented_sentences.append([a_words,new_label])
        #augmented_sentences.append(' '.join(a_words))
    
    #rs
    for _ in range(num_new_per_technique):
        a_words,new_label = random_swap(words,label, n_rs)
        if a_words == words:
            continue
        augmented_sentences.append([a_words,new_label])


    #rd
    for _ in range(num_new_per_technique):
        a_words,new_label = random_deletion(words,label, p_rd)
        if a_words == words:
            continue
        augmented_sentences.append([a_words,new_label])
       
    shuffle(augmented_sentences)
    
    #trim so that we have the desired number of augmented sentences
    if num_aug >= 1 :#and len(augmented_sentences)>num_aug:
        augmented_sentences = augmented_sentences[:num_aug]
    else:
        keep_prob = num_aug / len(augmented_sentences)
        augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]
    
    #append the original sentence
    augmented_sentences.append([words,label])#"0---"+sentence)

    return augmented_sentences

