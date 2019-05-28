"""
Here we do the hashing and update, search the """
from modules.NERD.dict_based_nerd import Nerd

from modules.basic_modules.basic import run_query
import solr
import copy
from modules.basic_modules.myOrm import Reference
from modules.basic_modules.basic import get_block_key

NOTARY_OFFSET_old = 4000000
NOTARY_OFFSET = 30000000


class Hashing():
    def __init__(self):
        """
        initializes the Solr connection
        :return:
        """
        self.s = solr.SolrConnection('http://localhost:8983/solr')
        self.commit_counter = 0
        self.commit_number = 0
        self.current_document_id = 0

    def add_key(self, ref_list, document_id):
        """

        :param ref_list: list of references that should be indexed
        :param document_id: document id
        :return:
        """
        if document_id and ref_list:
            feature_list = []  # features based on exact names
            block_keys = []  # blocking keys based on hossein's key
            for i1, key1 in enumerate(ref_list):
                for i2, key2 in enumerate(ref_list):
                    if i1 < i2:
                        # TODO: Don't add pairs for child and father, child and mother, bride and father of groom, etc.

                        feature = sorted(['_'.join(key1), '_'.join(key2)])
                        blocks = sorted([get_block_key(key1[0], key1[1]), get_block_key(key2[0], key2[1])])
                        feature_list.append(feature[0] + '_' + feature[1])
                        block_keys.append('_'.join(blocks))

            if feature_list:
                self.s.add(features=feature_list, blockKeys=block_keys, id=document_id)

            self.commit_counter += 1
            if self.commit_counter > 5000:
                self.s.commit()
                self.commit_counter = 0

                print self.commit_number
                self.commit_number += 1

    def update_all_persons(self):
        print "wait for 350"
        query = "select first_name, last_name, register_id from all_persons_2014"  # where register_type='death'"

        cur = run_query(query)
        self.commit_number = 0

        ref_list = []
        for c in cur:
            d_id = c[2]
            if len(c[0].split()) > 0:
                first_name = c[0].split()[0].decode('utf-8', 'ignore')
            else:
                first_name = None
            if len(c[1].split()) > 0:
                last_name = c[1].split()[-1].decode('utf-8', 'ignore')
            else:
                last_name = None

            if first_name and last_name:

                if d_id == self.current_document_id:
                    # if we're still selecting references from current_document_id
                    ref_list.append([first_name, last_name])

                else:
                    # if we have moved to references of a new document_id let's first commit the previous Solr
                    # features and then we make a new reference list
                    self.add_key(ref_list, self.current_document_id)
                    self.current_document_id = copy.copy(d_id)
                    ref_list = [[first_name, last_name]]

    def update_notaries(self):
        print "wait for 39"

        query = """
                SELECT row_id, text1, text2, text3, place, date from notary_acts
                """
        cur = run_query(query)
        for c in cur.fetchall():
            notary_id = c[0] + NOTARY_OFFSET
            doc_id = 'n' + str(c[0])
            text = c[1] + ' ' + c[2] + ' ' + c[3]

            nerd = Nerd(text)
            relations = nerd.get_relations()
            ref_list = []
            for index, rel in enumerate(relations):
                ref_list.append(Reference(str(doc_id) + str(2 * index), rel['ref1'][1]))
                ref_list.append(Reference(str(doc_id) + str(2 * index + 1), rel['ref2'][1]))

            if ref_list:
                feature_list = []
                block_keys = []
                for index in xrange(len(ref_list) / 2):
                    person_1_name = ref_list[2 * index].get_compact_name()
                    person_2_name = ref_list[2 * index + 1].get_compact_name()
                    if person_1_name and person_2_name:
                        sorted_keys = sorted([person_1_name, person_2_name])
                        blocks = sorted([get_block_key(person_1_name.split('_')[0], person_1_name.split('_')[-1]),
                                         get_block_key(person_2_name.split('_')[0], person_2_name.split('_')[-1])])
                        feature_list.append('_'.join(sorted_keys).decode('utf-8', 'ignore'))
                        block_keys.append('_'.join(blocks).decode('utf-8', 'ignore'))

                if feature_list and block_keys:
                    self.s.add(features=feature_list, blockKeys=block_keys, id=notary_id)

            self.commit_counter += 1
            if self.commit_counter > 5000:
                self.s.commit()
                self.commit_counter = 0

                print self.commit_number
                self.commit_number += 1

    def search(self, features_list=[], block_keys=[]):
        query_results = ''

        if block_keys:
            query = 'blockKeys:('
            for block in block_keys:
                query += block + '~ AND '
                # query += block + ' OR '


            query = query[:-5] + ')'
            query_results = self.s.query(query, rows=50, highlight=True, fields="blockKeys, features, id")
            return query_results

        if features_list:
            query = 'features:'
            for feature in features_list:
                query += feature + '~.01 OR '

            query = query[:-4]

            query_results = self.s.query(query, rows=200, highlight=True, fields="blockKeys, features, id")
        return query_results

    def block_to_name(self, blocking_key):
        """
        Here we have a blocking_key and we want to find the feature name for it!!
        """
        query = "blockKeys:%s" % blocking_key
        results = self.s.query(query, rows=1, fields="features").results
        names = "ERROR"
        for feature in results[0]['features']:
            # Here, I want to see which feature of this document corresponds to this blocking key!

            a = get_block_key('_'.join(feature.split('_')[:2]), '_'.join(feature.split('_')[-2:]),
                              "DOCUMENT")

            b = blocking_key

            if a == b:
                names = feature.split('_')

        return [' '.join(names[:2]), ' '.join(names[-2:])]


if __name__ == '__main__':
    my_hash = Hashing()
    my_hash.update_all_persons()
    # my_hash.update_notaries()
    my_hash.s.commit()
