'''
Created on Mar 8, 2012

@author: Rafa
'''

from database import PwdDb
from taggers import SemanticTagger
from root.tagset_conversion import TagsetConverter
from time import time
import csv

def main():
    """ Tags the dataset by semantic categories,
        assuming it's already pos and sentiment-tagged. """
    
    db = PwdDb()
    tagger = SemanticTagger()
    tg = TagsetConverter()
    
    print "tagging process initialized..."
    start = time()
    
#    csv_writer = csv.writer(open("../results/test1.csv","wb"), dialect='excel')
    
#    while (db.hasNext()):
    for i in range(1,30001):
        words = db.nextPwd() # list of Words
        for w in words:
            t = None
            
            if w.synsets is not None:
                wn_pos = tg.brownToWordNet(w.pos)
                t = tagger.tag(w.word, wn_pos, w.synsets)
            else:
                t = tagger.tag(w.word, w.pos)
        
            w.category = t
            db.saveCategory(w)
#            csv_writer.writerow([i, w.word, w.category, w.senti, w.pos])

    db.finish() 
    
    print "tagging process took " + str(time()-start) + " seconds."      
    return 0;
    
if __name__ == "__main__":
    main()