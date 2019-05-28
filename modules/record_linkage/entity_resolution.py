"""
A class for different types of entity resolution
"""
import pickle
import time
from modules.NERD.dict_based_nerd import Nerd
from modules.basic_modules.basic import string_compare, run_query, log
from modules.basic_modules.myOrm import Document, Reference


class FullData():
    """
        this loads the complete data which is needed for a task.
        Later this will be integrated with the load_data module.
    """
    def __init__(self):
        self.docs = {}
        self.refs = {}
        self.notaries = {}
        self.matches = {}
        self.blocks = {}
        self.hash_table = {}

    def load_references_all_persons(self, limit=None):
        log("load_references_all_persons started.")
        if limit:
            query = """
                    SELECT id, first_name, last_name, place_1, date_1, register_id, register_type from all_persons_2014 limit %d
                    """ % limit
        else:
            query = """
                    SELECT id, first_name, last_name, place_1, date_1, register_id, register_type from all_persons_2014
                    """

        cur = run_query(query)
        for c in cur.fetchall():
            ref_id = c[0]
            name = c[1] + ' ' + c[2]
            place = c[3]
            date = c[4]
            doc_id = c[5]
            doc_type = c[6]

            ref = Reference(ref_id, name)
            doc = Document(doc_id, [ref], place, date, doc_type)
            if self.docs.get(doc_id):
                self.docs[doc_id].ref_list.append(ref)
            else:
                self.docs[doc_id] = doc
        log("load_references_all_persons finished.")

    def load_notaries(self, limit=None):
        log("load_notaries started.")
        if limit:
            query = """
                    SELECT row_id, text1, text2, text3, place, date from notary_acts where date like %s limit %d
                    """ % ("'%-18%'", limit)
        else:
            query = """
                    SELECT row_id, text1, text2, text3, place, date from notary_acts where date like %s
                    """ % ("'%-18%'")
        cur = run_query(query)
        for c in cur.fetchall():
            doc_id = 'n' + str(c[0])
            text = c[1] + ' ' + c[2] + ' ' + c[3]
            place = c[4]
            date = c[5]
            doc_type = 'notary'

            nerd = Nerd(text)
            relations = nerd.get_relations()
            ref_list = []
            for index, rel in enumerate(relations):

                ref_list.append(Reference(str(doc_id)+ str(2 * index), rel['ref1'][1]))
                ref_list.append(Reference(str(doc_id)+ str(2 * index + 1), rel['ref2'][1]))

            if ref_list:
                doc = Document(doc_id, ref_list, place, date, doc_type)
                self.notaries[doc_id] = doc

                for index in xrange(len(ref_list)/2):
                    self.fill_in_blocks([ref_list[2 * index], ref_list[2 * index+1]], doc)

        log("load_notaries finished.")

    def fill_in_blocks(self, ref_list, doc):
        """
        for each to ref in ref_list add the document to the block
        """
        for ref1 in ref_list:
            for ref2 in ref_list:
                if ref1.ref_id < ref2.ref_id:
                    key_list = [ref1.get_compact_name(),ref2.get_compact_name()]
                    # key_list = sorted(key_list)
                    # block_key = key_list[0] + '_' + key_list[1]
                    # if self.blocks.get(block_key):
                    #     if not doc.doc_id in self.blocks.get(block_key):
                    #         self.blocks[block_key].append(doc.doc_id)
                    # else:
                    #     self.blocks[block_key] = [doc.doc_id]

                    block_key = key_list[0]
                    if self.blocks.get(block_key):
                        if not doc.doc_id in self.blocks.get(block_key):
                            self.blocks[block_key].append(doc.doc_id)
                    else:
                        self.blocks[block_key] = [doc.doc_id]

                    block_key = key_list[1]
                    if self.blocks.get(block_key):
                        if not doc.doc_id in self.blocks.get(block_key):
                            self.blocks[block_key].append(doc.doc_id)
                    else:
                        self.blocks[block_key] = [doc.doc_id]


    def generate_blocks(self):
        log("generate_blocks started")

        for doc in self.docs.values():
            self.fill_in_blocks(doc.ref_list, doc)

        log("generate_blocks finished")

    def generate_hash_code(self):
        """
        here we generate a 2D hashcode
        :return:
        """



class ER():

    def __init__(self):
        self.document_source = Document()
        self.document_target = Document()

    def compare_docs(self):
        name_set1 = []
        name_set2 = []

        # generating a set of compact names of source document
        for ref in self.document_source.ref_list:
            name_set1.append(ref.get_compact_name())
        name_set1 = set(name_set1)

        # generating a set of compact names of target document
        for ref in self.document_target.ref_list:
            name_set2.append(ref.get_compact_name())
        name_set2 = set(name_set2)

        # Getting intersection of documents
        similarity = list(name_set1.intersection(name_set2))

        return similarity


if __name__ == '__main__':
    er = ER()

    file_name = open('new_blocks_3.p', 'wa')
    data = FullData()
    data.load_references_all_persons(1000)
    data.generate_blocks()
    # data.load_notaries(100000)
    log("start pickling")
    # hast_file = open('hast_tmp', 'a')
    # for b in data.blocks:
    #     hast_file.write('%s, %s \n' %(b, data.blocks[b]))

    pickle.dump(data.blocks, open("full_hash_tmp.p", "w"))
    log("end pickling")

    #


    # useful_blocks = {}
    # for b in data.blocks.keys():
    #     flag_notarial = False
    #     flag_civil = False
    #     for doc in data.blocks[b]:
    #         if 'n' in doc:
    #             flag_notarial = True
    #         else:
    #             flag_civil = True
    #
    #         # if (len(data.blocks[b]) > 1 and flag_notarial) or (flag_notarial and flag_civil):
    #         #     useful_blocks[b] = data.blocks[b]
    #
    #             useful_blocks[b] = data.blocks[b]


    # new_block_list = []
    # for index, key in enumerate(useful_blocks.keys()):
    #     new_block_list.append([key, useful_blocks[key]])
    #
    # pickle.dump(new_block_list, open("matches_notary_civil.p", "w"))




    # data.load_notaries(100)
    # match_id = 0
    # # print data.notaries
    #
    # log("matching started.")
    # for doc_source in data.notaries.values():
    #     # for doc_target in data.notaries.values():
    #     for doc_target in data.docs.values():
    #         # if doc_source.doc_id < doc_target.doc_id:
    #         er.document_source = doc_source
    #         er.document_target = doc_target
    #         similarity = er.compare_docs()
    #         if len(similarity) > 2:
    #             match_id += 1
    #             match = Match(match_id, doc_source.doc_id, doc_target.doc_id, 'notary_to_certificate')
    #             data.matches[match_id] = match
    #
    # for d in data.matches.values():
    #     print d
    #
    # log("matching finished.")






