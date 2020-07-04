# configuration for UMLS-EDA
import os 
class Config():
    
    QuickUMLS_git_dir = "tools/QuickUMLS-master"
    QuickUMLS_dir = "tools/QuickUMLS" # where your QuickUMLS data is intalled
    
    apikey = ""             # your api key from NLM UMLS API service
    threshold = 0.8

    # set soft link to QuickUMLS
    if not os.path.exists("QuickUMLS"):
        command = "ln -s "+ QuickUMLS_git_dir + " QuickUMLS"
        os.system (command)
    
    
