# Easy data augmentation techniques for text classification
# Jason Wei and Kai Zou

from src.eda4ner import *

#arguments to be parsed from command line
import argparse,codecs
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, type=str, help="input file of unaugmented data")
ap.add_argument("--output", required=False, type=str, help="output file of unaugmented data")
ap.add_argument("--num_aug", required=False, type=int, help="number of augmented sentences per original sentence")
ap.add_argument("--alpha", required=False, type=float, help="percent of words in each sentence to be changed")
args = ap.parse_args()
from config import Config
config = Config()
apikey = config.apikey

#the output file
output = None
if args.output:
    output = args.output
else:
    from os.path import dirname, basename, join
    output = join(dirname(args.input), 'eda_' + basename(args.input))

#number of augmented sentences to generate per original sentence
num_aug = 10 #default
if args.num_aug:
    num_aug = args.num_aug

#how much to change each sentence
alpha = 0.3#default
if args.alpha:
    alpha = args.alpha

# read conll file by sentence    
def delimited(file, delimiter = '\n', bufsize = 4096):
    buf = ''
    while True:
        newbuf= file.read(bufsize)
        if not newbuf:
            yield buf
            return
        buf +=newbuf
        lines =buf.split(delimiter)
        for line in lines[:-1]:
            yield line
        buf = lines[-1]
    
#generate more data with standard augmentation
def gen_eda(train_orig, output_file, alpha, num_aug=9):

    writer = open(output_file, 'w')
    #lines = open(train_orig, 'r').readlines()
    ann_infile = codecs.open(train_orig,'r')
    lines = delimited(ann_infile,"\n\n",bufsize = 1)
    
    for i, line in enumerate(lines):
        #parts = line[:-1].split('\t')
        #label = parts[0]
        if i% 50 == 0:
            print (i,"lines finished...")
        info = line.rstrip().split("\n")
        
        if line.rstrip() =="":
            continue

        sent = [a.split("\t")[0] for a in info]
        label = [a.split("\t")[1] for a in info]
        sentence = " ".join(sent)
        #sentence = line.rstrip()
        aug_sentences = eda(sentence,label,apikey=apikey, alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha,alpha_umls=alpha, num_aug=num_aug)
        #aug_sentences = eda(sentence,label,alpha_sr=alpha, alpha_ri=alpha, alpha_rs=alpha, p_rd=alpha, num_aug=num_aug, task ="re")
        for aug_sentence in aug_sentences:
        
            words = aug_sentence[0]
            labels = aug_sentence[1]
            for w,l in zip(words,labels):
                writer.write(w+"\t"+l+"\n")
            writer.write("\n")
            #writer.write(aug_sentence)
            #writer.write('\n')
        
    writer.close()
    
    print("generated augmented sentences with eda for " + train_orig + " to " + output_file + " with num_aug=" + str(num_aug))

#main function
if __name__ == "__main__":
    import time 
    before = time.time()
    #generate augmented sentences and output into a new file
    gen_eda(args.input, output, alpha=alpha, num_aug=num_aug)
    cost = time.time()-before
    print (cost)
