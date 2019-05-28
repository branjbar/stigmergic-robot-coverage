from modules.NERD.dict_based_nerd import Nerd
from modules.basic_modules.basic import get_block_key

__author__ = 'Bijan'

from modules.basic_modules import basic, loadData

STANDARD_QUERY = "SELECT id, first_name, last_name, date_1, place_1, gender, role, register_id, register_type \
          FROM all_persons_2014 WHERE "

import random

NOTARY_OFFSET = 30000000


class Reference():
    """
    a class for using any reference
    """
    REF_TYPE = {'birth': {1: "Born",
                          5: "Parent",
                          5: "Parent",
    },
                'marriage': {1: "Groom/Bride",
                             2: "Groom's Parent",
                             3: "Bride's Parent",
                },
                'death': {1: "Deceased",
                          4: "Parent",
                          6: "Relative",
                },
    }

    def __init__(self, ref_id=None, name=None, ref_type=None):
        self.ref_id = ref_id
        self.name = name
        self.ref_type = ref_type


    def __repr__(self):
        # return str(self.ref_id) + '_' + str(self.name)
        return str(self.__dict__)

    def get_compact_name(self):
        if len(self.name) > 1:
            import unicodedata

            compact_name = (self.name.split()[0] + '_' + self.name.split()[-1])
            # compact_name = unicodedata.normalize('NFKD', compact_name)
            return compact_name
        else:
            return ''

    def set_id(self, ref_id, doc_type=None):
        person = get_person(int(ref_id))
        self.ref_id = person['id']
        self.name = person['first_name'] + ' ' + person['last_name']
        if doc_type in ['birth', 'marriage', 'death']:
            self.ref_type = self.REF_TYPE[doc_type][person['role']]
        else:
            self.ref_type = ['Ext. text']


class Document():
    """
    a class for using any document
    """

    def __init__(self, doc_id=None, ref_list=[], place=None, date=None, doc_type=None, rel_list=None):
        self.doc_id = doc_id
        self.ref_list = ref_list
        self.place = place
        self.date = date
        self.doc_type = doc_type
        self.text = None
        self.rel_list = None

    def __repr__(self):
        # return str(self.doc_id) + '_' + str(self.doc_type) + '_' +str(self.ref_list) + '_' + str(self.place) + '_' + str(self.date)
        return str(self.__dict__)

    def __dict_new__(self):

        dict = self.__dict__
        ref_list = []
        for ref in self.ref_list:
            ref_list.append(ref.__dict__)
        dict['ref_list'] = ref_list
        return dict

    def get_html(self, hash_key=[], features_ref=[], block_keys=[]):

        if self.doc_type == "notarial act":
            html = """ <div class="panel-body col-xs-12">"""
        else:
            html = """ <div class="panel-body col-xs-12" >"""

        html += """
                                <div class="panel panel-default">
                                  <div class="panel-heading">
                                    <h3 class="panel-title">%s</h3>
                                  </div>
                                  <div class="panel-body" >


                """ % self.doc_type.title()

        if self.doc_type == "notarial act":
            html += """<code>#%s</code> on <code>%s</code> in <code>%s</code>
                        <hr style="margin: 8px 0;">
                        <div class="col-xs-12">
                    """ % (self.doc_id, self.date, self.place)
            text = self.text

            for rel in self.rel_list:
                for ref_name in [rel['ref1'][1], rel['ref2'][1]]:
                    if len(ref_name.split()) > 1:
                        ref_key = ref_name.split()[0] + '_' + ref_name.split()[-1]
                        ref_block_key = get_block_key(ref_name.split()[0], ref_name.split()[-1])
                        couple_names = ['_'.join(key.split(' ')) for key in features_ref]

                        if block_keys:

                            if [ref_block_key for s in block_keys if ref_block_key in s]: # show whether the reference is in one of the blocks or not!
                                if ref_key in couple_names:
                                    text = text.replace(ref_name, '<span class="highlight">%s</span>' % ref_name)
                                else:
                                    text = text.replace(ref_name, '<span class="highlight_fuzzy">%s</span>' % ref_name)

                        else:
                            if ref_key in hash_key:
                                if ref_key in ['_'.join(key.split('_')[:2]) for key in features_ref] + ['_'.join(key.split('_')[2:]) for key in features_ref]:
                                    text = text.replace(ref_name, '<span class="highlight">%s</span>' % ref_name)
                                else:
                                    text = text.replace(ref_name, '<span class="highlight_fuzzy">%s</span>' % ref_name)

            html += """<small> """ + text + "</small>"
            html += "</div>"
            html += """<div class="col-xs-6">"""

        else:

            html += """ <table class="table table-condensed" style="margin-bottom: 0px; border: none"> """
            html += "<tr > \n <td style='padding: 1px'><small> %s </small></td> \n <td style='padding: 1px'><small> %s</small> </td>  \n </tr>\n" % (
                '<b>id</b>',
                self.doc_id)
            html += "<tr > \n <td style='padding: 1px'><small> %s </small></td> \n <td style='padding: 1px'><small> %s</small> </td>  \n </tr>\n" % (
                '<b>place</b>',
                self.place)
            html += "<tr > \n <td style='padding: 1px'><small> %s </small></td> \n <td style='padding: 1px'><small> %s</small> </td>  \n </tr>\n" % (
                '<b>date</b?',
                self.date)
            for ref in self.ref_list:
                try:
                    ref_name = ref['name']
                    ref_type = ref['ref_type']
                except:
                    ref_name = ref.name
                    ref_type = ref.ref_type

                if len(ref_name.split()) > 1:
                    ref_key = ref_name.split()[0] + '_' + ref_name.split()[-1]
                    ref_block_key = get_block_key(ref_name.split()[0], ref_name.split()[-1])
                    couple_names = ['_'.join(key.split(' ')) for key in features_ref]
                    if block_keys:
                        if [ref_block_key for s in block_keys if ref_block_key in s]: # show whether the reference is in one of the blocks or not!
                        # if ref_block_key in block_keys[0]:
                            if ref_key in couple_names:
                                ref_name = '<span class="highlight"> %s </span>' % ref_name
                            else:
                                # TODO: Doesn't work for "Antonia Visser & Lambertus Berg"
                                ref_name = '<span class="highlight_fuzzy"> %s </span>' % ref_name
                    else:
                        if ref_key in hash_key:
                            if ref_key in ['_'.join(key.split('_')[:2]) for key in features_ref] + ['_'.join(key.split('_')[2:]) for key in features_ref]:
                                ref_name = '<span class="highlight"> %s </span>' % ref_name
                            else:
                                ref_name = '<span class="highlight_fuzzy"> %s </span>' % ref_name

                html += "<tr > \n <td style='padding: 1px'><small> <b>%s</b> </small></td> \n <td style='padding: 1px'>" \
                        "<small> %s</small> </td>  \n </tr>\n" % (ref_type, ref_name)

            html += "</table>"

        if self.doc_type == "notarial act":
            html += "</div>"

        html += """
                                          </div>
                                          </div>
                                          </div>
                                          """

        if self.doc_type == "notarial act":
            year = self.date[-4:]
        else:
            year = self.date[:4]

        place = self.place
        return {'year': year, 'city': place, 'html': html,
                'title': self.doc_type.title(),
                'concept': "test"}

    def add_ref(self, ref):
        self.ref_list.append(ref)

    def set_id(self, doc_id):
        if 'n' in doc_id:
            doc_id = int(doc_id[1:]) + NOTARY_OFFSET

        if int(doc_id) < NOTARY_OFFSET:
            document = get_document(int(doc_id))
            self.doc_id = int(doc_id)
            self.place = document['municipality']
            self.date = document['date']
            self.doc_type = document['type_text']
            self.ref_list = []

            for ref_id in document['reference_ids'].split(','):
                ref = Reference()
                ref.set_id(ref_id, self.doc_type)
                self.add_ref(ref)

        else:  # extract from notary
            if int(doc_id) >= NOTARY_OFFSET:
                text_id = int(doc_id)
                text_doc = get_notarial_act(text_id - NOTARY_OFFSET)
                text = text_doc['text1'] + ' ' + text_doc['text2'] + ' ' + text_doc['text3']
                nerd = Nerd(text)

                self.doc_id = doc_id
                self.place = text_doc['place']
                self.date = text_doc['date']
                self.doc_type = 'notarial act'
                self.text = text

                ref_id = 0
                self.ref_list = []

                self.rel_list = nerd.get_relations()

                for rel in nerd.get_relations():
                    ref_id += 1
                    ref1 = Reference(str(doc_id) + '_' + str(ref_id), rel['ref1'][1], 'couple_' + str((ref_id + 1) / 2))
                    ref_id += 1
                    ref2 = Reference(str(doc_id) + str(ref_id), rel['ref2'][1], 'couple_' + str((ref_id) / 2))
                    self.add_ref(ref1)
                    self.add_ref(ref2)


#
# class Match():
# """
# a class for storing are found matches
#     """
#     def __init__(self, match_id=None, doc_id1=None, doc_id2=None, match_type=None):
#         self.match_id = match_id
#         self.doc_id1 = doc_id1
#         self.doc_id2 = doc_id2
#         self.match_type = match_type
#
#     def __repr__(self):
#
#         return str(self.match_id) + '_' + str(self.doc_id1) + '_' + str(self.doc_id2) + '_' + str(self.match_type)
#

def row_to_reference(row, table="all_persons_2014"):
    ''' (list, table) -> (dict)
    adds labels to different elements of the list, according to the table type,
    and makes a reference
    '''

    if table == 'links':
        ref = {}
        key_dict = {0: 'type', 1: 'id1', 2: 'id2', 3: 'role1', 4: 'role2', 5: 'id'}

        for key in key_dict.keys():
            ref[key_dict[key]] = row[key]
        return ref


def get_person(person_id=None):
    ''' (integer) -> (dict)
    return a person with the id
    '''
    person = None
    if loadData.table_all_persons:
        if not person_id and loadData.table_all_persons:
            person_id = random.choice(loadData.table_all_persons.keys())

        person = loadData.table_all_persons.get(int(person_id))
    if not person and person_id:
        loadData.update_persons_table('', ['', '', 'where id = %s' % str(person_id)])
        person = loadData.table_all_persons.get(int(person_id))

    if person:
        return person
    else:
        return None


def get_document(document_id=None):
    ''' (integer) -> (dict)
    return a document with the id
    '''
    # if no id then find a random person
    document = None
    if loadData.table_all_documents:
        if not document_id:
            document_id = random.choice(loadData.table_all_documents.keys())

        document = loadData.table_all_documents.get(int(document_id))

    if not document and document_id:
        loadData.update_documents_table(['', '', 'where id = %s' % str(document_id)])
        document = loadData.table_all_documents.get(int(document_id))


    if document:
        return document
    else:
        return None


def get_block(block_id=None):
    """ (integer) -> (dict)
    return the block information with the id
    """

    if loadData.block_dict:

        if not block_id:
            retry_counter = 0
            while retry_counter < 100:
                block_id = random.choice(loadData.block_dict.keys())
                block = loadData.block_dict.get(block_id)
                if block.get('block_id') and len(block['block_id']) > 1:
                    retry_counter = 100
                else:
                    retry_counter += 1
        else:
            block = loadData.block_dict.get(block_id)

        return block

    else:
        return {}


def get_links(link_id=None):
    ''' (integer) -> (dict)
    returns the links_match information based on the id
    '''

    # if no id provided then get a random block
    if not link_id:
        from random import randrange

        link_id = randrange(1, 2980158)
    reference = {}
    index = 1
    while index < 3:
        link_query = 'select *, ' + str(link_id) + ' from links where id1 > 0 and id2 > 0 limit ' + str(link_id) + ',1'
        cur = basic.run_query(link_query)
        row = cur.fetchone()
        if row:
            reference = row_to_reference(row, "links")
        else:
            reference = {}

        if reference.get('id1') and reference.get('id2'):
            index = 5
        else:
            index += 1

    if reference.get('id1') and reference.get('id2'):
        reference['id'] = link_id
        return reference
    else:
        return {'id1': 0, 'id2': 0}


def get_notarial_act(text_id=None):
    ''' (integer) -> (dict)
    return a person with the id
    '''

    text = None
    # if loadData.table_notarial_acts:
    #     if not text_id and loadData.table_notarial_acts:
    #         text_id = random.choice(loadData.table_notarial_acts.keys())
    #
    #     text = loadData.table_notarial_acts.get(int(text_id))

    if not text and text_id:
        index = loadData.update_notarial_acts(['', '', 'where row_id = %s' % str(text_id)])
        # index = loadData.update_notarial_acts(['', '', 'where date like %s limit %s, 1' % ("'%-18%'", str(text_id))])
        text = loadData.table_notarial_acts.get(index)

    if text:
        return text
    else:
        return None


def get_miss_matches(match_index=None, match_id=None):
    """ (integer) -> (dict)
    returns the miss_match information based on the id
    """

    # if no id provided then get a random block
    if not loadData.match_pairs:
        loadData.get_matching_pairs()

    if not match_index:
        from random import randrange

        match_index = randrange(1, 1000)

    match_index = int(match_index)
    if loadData.match_pairs.get(match_index):
        reference = loadData.match_pairs[match_index]
        reference['index'] = match_index
    else:
        reference = {}
    return reference


def get_relatives(person_id):
    """
     uses the 'relations' table in order to extract the id of all relatives of person_id
    """
    modified_relative_ids = []
    if person_id:

        key_d = int(loadData.table_all_persons.get(person_id)['register_id'])

        if loadData.table_all_documents.get(key_d):

            relatives = loadData.table_all_documents[key_d]['reference_ids']
            relative_ids = relatives.split(',')
            for i in relative_ids:
                if int(i) != person_id:
                    modified_relative_ids.append(int(i))

    return modified_relative_ids


if __name__ == "__main__":
    pass
