# UMLS-EDA :octocat: 
**:tada: A light-weighted UMLS-based data augmentation for biomedical NLP tasks including Named Entity Recognition and sentence classification :tada:**  

* Citation: [Kang, T., Perotte, A., Tang, Y., Ta, C., & Weng, C. (2020). *UMLS-based data augmentation for natural language processing of clinical research literature*. Journal of the American Medical Informatics Association.](https://academic.oup.com/jamia/advance-article/doi/10.1093/jamia/ocaa309/6046153)
* Author: [Tian Kang](http://www.tiankangnlp.com)  (tk2624@cumc.columbia.edu)  
* Affiliation: Department of Biomedical Informatics, Columbia Univerisity ([Dr. Chunhua Weng](http://people.dbmi.columbia.edu/~chw7007/)'s lab)   
* Built upon [EDA-Easy Data Augmentation](https://arxiv.org/abs/1901.11196) 


## User Guide  
  
### 0. Before start  
  1) Install ['UMLS'](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html) and ['QuickUMLS'](https://github.com/Georgetown-IR-Lab/QuickUMLS) locally 
  2) Get your **UMLS SOAP API Key** from the UTS ‘My Profile’ area after signing in [UMLS Terminology service](https://uts.nlm.nih.gov/home.html) 
  3) Add your API Key and QuickUMLS directory to the `config.py`.   
  4) Costomzie other variables in the `config.py`   
  
### 1. Named Entity Recognition  

 * **Input**: CoNLL format file  
 * **Usage**: 	 
 ```
     python augment4ner.py [-h] --input INPUT [--output OUTPUT] [--num_aug NUM_AUG] [--alpha ALPHA]
 ```
     
### 2. Sentence Classification 

 * **Input**: "|" seperated file (`index|label|sentence text`)  
 * **Usage**: 
 ```
     python augment4class.py [-h] --input INPUT [--output OUTPUT] [--num_aug NUM_AUG] [--alpha ALPHA]
 ```
 
 See `examples/example4ner.conll` and `example/example4class.txt`  
 
 
 ## Reference
 * Wei, J. and Zou, K., 2019. [Eda: Easy data augmentation techniques for boosting performance on text classification tasks](https://arxiv.org/abs/1901.11196). arXiv preprint arXiv:1901.11196. ([Github repo](https://github.com/jasonwei20/eda_nlp.git))
