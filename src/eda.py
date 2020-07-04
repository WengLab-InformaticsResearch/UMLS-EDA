# Easy data augmentation techniques for text classification
# Jason Wei and Kai Zou

import random
from random import shuffle
random.seed(1)
from config import Config
config = Config()


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

re_stop_words = []
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
    if clean_line == "":
        return ""
    if clean_line[0] == ' ':
        clean_line = clean_line[1:]
    return clean_line


#*****************************
# UMLS Synonyms replacement  #
#*****************************


from QuickUMLS.quickumls import QuickUMLS
matcher = QuickUMLS(config.QuickUMLS_dir,threshold=config.threshold,similarity_name ='cosine')#,overlapping_criteria='length')

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
apikey = config.apikey

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

def umls_replacement(words,n,task = "sent"):
    sent = " ".join(words)
    apikey = "d6f6cb00-7c3e-412b-83cf-cc3dde4067f1"
    
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
        
        if len(atoms)>0:
            atoms_set.append({i['term']:atoms})
            total_num=total_num*len(atoms)
    max_num = min(n, total_num)
    for _ in range(max_num):
        new_sent = sent
        for i in range(len(atoms_set)):
            atom = atoms_set[i]
            term = list(atom.keys())[0]
            atoms = atom[term]
            synonym = random.choice(atoms)
            new_sent = re.sub("[ |^]"+term+"[ |$]"," "+synonym+" ",new_sent)
            #atoms.remove(synonym)
            #atoms_set[i] = {term:atoms}
        augumented_sents.append(new_sent)
    return list(set(augumented_sents))

########################################################################
# Synonym replacement
# Replace n words in the sentence with synonyms from wordnet
########################################################################

#for the first time you use wordnet
#import nltk
#nltk.download('wordnet')
from nltk.corpus import wordnet 

def synonym_replacement(words, n,task = "sentence"):
    new_words = words.copy()
    random_word_list = list(set([word for word in words if word not in stop_words]))
    
    if task  == "re":
        random_word_list = list(set([word for word in words if not re.search("^@\w+\$$",word)]))
        
    random.shuffle(random_word_list)
    num_replaced = 0
    for random_word in random_word_list:
        synonyms = get_synonyms(random_word)
        if len(synonyms) >= 1:
            synonym = random.choice(list(synonyms))
            new_words = [synonym if word == random_word else word for word in new_words]
            num_replaced += 1
        if num_replaced >= n: #only replace up to n words
            break

    #this is stupid but we need it, trust me
    sentence = ' '.join(new_words)
    new_words = sentence.split(' ')

    return new_words

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word): 
        for l in syn.lemmas(): 
            synonym = l.name().replace("_", " ").replace("-", " ").lower()
            synonym = "".join([char for char in synonym if char in ' qwertyuiopasdfghjklzxcvbnm'])
            synonyms.add(synonym) 
    if word in synonyms:
        synonyms.remove(word)
    return list(synonyms)

########################################################################
# Random deletion
# Randomly delete words from the sentence with probability p
########################################################################

def random_deletion(words, p,task = "sentence"):
    #obviously, if there's only one word, don't delete it
    if len(words) == 1:
        return words

    #randomly delete words with probability p
    new_words = []
    for word in words:
        if task == "re" and re.search("^@\w+\$$",word):
            new_words.append(word)
            continue
            
        r = random.uniform(0, 1)
        if r > p:
            new_words.append(word)

    #if you end up deleting all words, just return a random word
    if len(new_words) == 0:
        if len(words)-1<0:
            return 
        rand_int = random.randint(0, len(words)-1)
        return [words[rand_int]]

    return new_words

########################################################################
# Random swap
# Randomly swap two words in the sentence n times
########################################################################

def random_swap(words, n,task = "sent"):
    new_words = words.copy()
    for _ in range(n):
        new_words = swap_word(new_words)
    return new_words

def swap_word(new_words, task = "sent"):
    if len(new_words)-1<0:
        return
    random_idx_1 = random.randint(0, len(new_words)-1)
    
    if task == "re":
        while re.search("^@\w+\$$",new_words[random_idx_1]):
            random_idx_1 = random.randint(0, len(new_words)-1)
    
    random_idx_2 = random_idx_1
    counter = 0
    while random_idx_2 == random_idx_1 or re.search("^@\w+\$$",new_words[random_idx_2]):
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

def random_insertion(words, n,task = "sent"):
    new_words = words.copy()
    for _ in range(n):
        add_word(new_words)
    return new_words

def add_word(new_words):
    synonyms = []
    counter = 0
    while len(synonyms) < 1:
        if len(new_words)-1<0:
            return
        random_word = new_words[random.randint(0, len(new_words)-1)]

        synonyms = get_synonyms(random_word)
        counter += 1
        if counter >= 10:
            return
    random_synonym = synonyms[0]
    random_idx = random.randint(0, len(new_words)-1)
    new_words.insert(random_idx, random_synonym)

########################################################################
# main data augmentation function
########################################################################

def eda(sentence, alpha_sr=0.2, alpha_ri=0.2, alpha_rs=0.2, p_rd=0.2,alpha_umls=0.5,num_aug=9,task = "sent"):
    #task = "sent" sentence classification
    #task= "re" relation extraction "index sentence label"
    
    #sentence = get_only_chars(sentence)
    words = sentence.split(' ')
    words = [word for word in words if word is not '']
    num_words = len(words)
    
    augmented_sentences = []
    num_new_per_technique = int(num_aug/4)+1
    n_sr = max(1, int(alpha_sr*num_words))
    n_ri = max(1, int(alpha_ri*num_words))
    n_rs = max(1, int(alpha_rs*num_words))
    n_umls = max(1,int(alpha_umls*num_words))

    
    #umls
    try:
        sentences = umls_replacement(words,n_umls,task)
        if len(sentences) > 0:
            augmented_sentences.extend(sentences)
    except:
        augmented_sentences=[]
  
    #sr
    for _ in range(num_new_per_technique):
        a_words = synonym_replacement(words, n_sr,task)
        if  a_words is None or len(a_words)<1:
            continue
        augmented_sentences.append(' '.join(a_words))
    #ri
    for _ in range(num_new_per_technique):
        a_words = random_insertion(words, n_ri,task)
        if  a_words is None or len(a_words)<1:
            continue
        augmented_sentences.append(' '.join(a_words))
    #rs
    for _ in range(num_new_per_technique):
        a_words = random_swap(words, n_rs,task)
        if  a_words is None or len(a_words)<1:
            continue
        augmented_sentences.append(' '.join(a_words))
    #rd
    for _ in range(num_new_per_technique):
        a_words = random_deletion(words, p_rd,task)
        if  a_words is None or len(a_words)<1:
            continue
        augmented_sentences.append(' '.join(a_words))

    
    #augmented_sentences = list(set([get_only_chars(sentence) for sentence in augmented_sentences]))
    shuffle(augmented_sentences)

    #trim so that we have the desired number of augmented sentences
    if num_aug >= 1:
        augmented_sentences = augmented_sentences[:num_aug]
    else:
        keep_prob = num_aug / len(augmented_sentences)
        augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]

    #append the original sentence
    augmented_sentences.append(sentence)

    return augmented_sentences

