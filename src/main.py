'''
Created on Feb 7, 2014

@author: Bijan

# PYTHONPATH=~/sandbox/stigmergic-robot-coverage python main.py
'''
import logging

from modules.basic_modules import basic
from modules.record_linkage import featureExtraction


def check_a_random_pair():
    ref1 = basic.get_person()
    ref2 = basic.get_person()

    score_0 = basic.get_match_score(ref1, ref2, 0)
    print ref1, '\n', ref2, '\nscore_0 is ', score_0
    score_1 = basic.get_match_score(ref1, ref2, 1)
    print 'score_1 is ', score_1
    score_2 = basic.get_match_score(ref1, ref2, 2)
    print 'score_2 is', score_2


def do_matching():
    from modules.basic_modules import basic

    basic.do_matching()


def feature_set_construct():
    """
        constructs the feature sets for all standard dutch names and inserts that into the feature table
    """
    from modules.basic_modules import basic

    records = basic.get_dutch_names()
    for record in records:
        id = record[0]
        name = record[1]
        standard = record[2]
        document_type = record[3]
        f_list = featureExtraction.extract_feature(name, standard)
        #print name, standard, f_list
        basic.insert_features(id, name, standard, document_type, f_list)


if __name__ == '__main__':
    logging.basicConfig(filename='logging.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.info('________________new________________')

    import sys

    sys.path.append("/Users/bijan/sandbox/stigmergic-robot-coverage")

    from interface import main_Interface

    main_Interface.main()

