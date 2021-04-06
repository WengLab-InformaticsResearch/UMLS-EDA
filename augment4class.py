# Easy data augmentation techniques for text classification
# Jason Wei and Kai Zou

from src.eda import *

#arguments to be parsed from command line
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, type=str, help="input file of unaugmented data")
ap.add_argument("--output", required=False, type=str, help="output file of unaugmented data")
ap.add_argument("--num_aug", required=False, type=int, help="number of augmented sentences per original sentence")
ap.add_argument("--alpha", required=False, type=float, help="percent of words in each sentence to be changed")
args = ap.parse_args()
from config import Config
config = Config()
apikey=config.apikey
#the output file
output = None
if args.output:
    output = args.output
else:
    from os.path import dirname, basename, join
    output = join(dirname(args.input), 'eda_' + basename(args.input))

#number of augmented sentences to generate per original sentence
num_aug = 9 #default
if args.num_aug:
    num_aug = args.num_aug

#how much to change each sentence
alpha = 0.3#default
if args.alpha:
    alpha = args.alpha
import re,time
#generate more data with standard augmentation
def gen_eda(train_orig, output_file, alpha, num_aug=9):

    writer = open(output_file, 'w')
    lines = open(train_orig, 'r').readlines()
    cur_time= time.time()
    for i, line in enumerate(lines):
        if re.search("^##|^\s+$",line):
            writer.write(line)
            continue
        parts = line.rstrip().split('|')
        label = parts[1]
        sentence = parts[2]
        aug_sentences = eda(sentence, apikey=apikey, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha,alpha_umls=alpha, num_aug=num_aug)
        for aug_sentence in aug_sentences:
            writer.write(parts[0]+"|"+label + "|" + aug_sentence + '\n')
        if i%10 ==0:
            cost = time.time()-cur_time
            minute=cost//60
            print ("......10 instance cost:",minute,"min, or",cost,"sec.\n")
            cur_time = time.time()
    writer.close()
    print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))


# generate augmentation for bert relation extraction data
def gen_eda_for_re(train_orig, output_file, alpha, num_aug=9):  
    writer = open(output_file, 'w')
    lines = open(train_orig, 'r').readlines()
    cur_time= time.time()
    for i, line in enumerate(lines):
       
        if re.search("^index",line):
            writer.write(line)
            continue

        parts = line.rstrip().split('\t')
        index = parts[0]
        sentence = parts[1]
        label= parts[2]
        aug_sentences = eda(sentence, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha,alpha_umls=alpha, num_aug=num_aug,task = "re")
        for aug_sentence in aug_sentences:
        
            writer.write(index+"\t"+aug_sentence + "\t" + label + '\n')
        if i%10 ==0:
            cost = time.time()-cur_time
            minute=cost//60
            cur_time = time.time()
    writer.close()
    print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))

    
#main function
if __name__ == "__main__":

    #generate augmented sentences and output into a new file
    gen_eda(args.input, output, alpha=alpha, num_aug=num_aug)
