from modules.basic_modules import basic


__author__ = 'Bijan'

import time
import threading
import logging
MATCH_TABLE = "miss_matches_random_walk"

table_all_documents = {}
table_all_persons = {}
table_notarial_acts = {}
block_dict = {}
match_pairs = {}


# TODO: write a unique class for data load


def update_persons_table(db_useless, limit):
    """
    loading data from persons table: either for a range of persons or just a specific person
    (i.e., where addendum is provided)
    """

    global table_all_persons, block_dict, db
    __now__ = time.time()


    lim = limit[0]
    type = limit[1]
    addendum = limit[2]
    logging.debug('Loading table all_persons.')

    the_query = "select id, first_name, prefix, last_name, date_1 as date, place_1 as place," \
                " gender, role, register_id, register_type from all_persons_2014"
    if type:
        q_type = None
        for t in type:
            if not q_type:
                q_type = " register_type = '%s'" % t
            else:
                q_type += " or register_type = '%s'" % t
        the_query += " where %s" % q_type

    if lim:
        the_query += " limit %d" % lim

    if addendum:
        the_query += " " + addendum

    cur = basic.run_query(the_query)
    desc = cur.description

    if not addendum:
        t2 = threading.Thread(target=update_documents_table, args=(limit))
        t2.daemon = True
        t2.start()


    tmp_index = 0
    for row in cur.fetchall():
        row_dict = {}
        tmp_index += 1
        for index, value in enumerate(row):
            try:
                row_dict[desc[index][0]] = value.decode('ascii','ignore')
            except:
                row_dict[desc[index][0]] = value
        table_all_persons[row_dict['id']] = row_dict

    logging.debug("table all_persons imported in %s" % str(time.time() - __now__))

def update_notarial_acts(limit):
    """
    loading data from notarial acts: either for a range of acts or just a specific act
    (i.e., where addendum is provided)
    """

    global table_notarial_acts
    __now__ = time.time()


    lim = limit[0]
    type = limit[1]
    addendum = limit[2]
    logging.debug('Loading table notarial_acts.')

    the_query = "select * from notary_acts"

    if type:
        q_type = None
        for t in type:
            if not q_type:
                q_type = " register_type = '%s'" % t
            else:
                q_type += " or register_type = '%s'" % t
        the_query += " where %s" % q_type

    if lim:
        the_query += " limit %d" % lim

    if addendum:
        the_query += " " + addendum
    cur = basic.run_query(the_query)
    desc = cur.description

    if not addendum:
        t2 = threading.Thread(target=update_documents_table, args=(limit))
        t2.daemon = True
        t2.start()


    tmp_index = 0
    for row in cur.fetchall():
        row_dict = {}
        tmp_index += 1
        for index, value in enumerate(row):
            try:
                row_dict[desc[index][0]] = value.decode('ascii', 'ignore')
            except:
                row_dict[desc[index][0]] = value
        table_notarial_acts[row_dict['row_id']] = row_dict
    logging.debug("table notarial_acts imported in %s" % str(time.time() - __now__))
    return row_dict['row_id']





def update_documents_table(limit):
    """
    loading data from documents table: either for a range of documents or just a specific document
    (i.e., where addendum is provided)
    """
    global table_all_documents, block_dict


    __now__ = time.time()

    lim = limit[0]
    type = limit[1]
    addendum = limit[2]

    logging.debug(" Loading table all_documents.")

    the_query = "select id, type_text, date, municipality, " \
                " reference_ids from all_documents_2014"
    if type:
        q_type = None
        for t in type:
            if not q_type:
                q_type = "type_text = '%s'" % t
            else:
                q_type += " or type_text = '%s'" % t
        the_query += " where %s" % q_type

    if lim:
        the_query += " limit %d" % lim

    if addendum:
        the_query += " " + addendum


    cur = basic.run_query(the_query)
    desc = cur.description

    tmp_index = 0
    for row in cur.fetchall():
        row_dict = {}
        tmp_index += 1
        for index, value in enumerate(row):
            try:
                row_dict[desc[index][0]] = value.decode('ascii','ignore')
            except:
                row_dict[desc[index][0]] = value
        table_all_documents[row_dict['id']] = row_dict

    logging.debug("table all_documents imported in %s" % str( time.time() - __now__))

    if not addendum:
        get_matching_pairs()


def get_matching_pairs(limit=1000000):
    """
    loading data from miss_matches table
    """

    global match_pairs, MATCH_TABLE
    __now__ = time.time()


    logging.debug('Loading table miss_matches.')

    # the_query = "select id, ref1, ref2, score from miss_matches order by score desc limit %d" % limit

    the_query = """
                SELECT id, ref1, ref2, score, eval, comment
                FROM (
                    SELECT
                        @row := @row +1 AS rownum, id, ref1, ref2, score, eval, comment
                    FROM (SELECT @row :=0) r,
                """ + MATCH_TABLE + """
                    order by ref1 desc limit 10000000
                    ) ranked
                    # WHERE rownum % 1 = 0
                """

    # the_query = """
    #             SELECT id, ref1, ref2, score, eval, comment
    #             FROM (
    #                 SELECT
    #                     @row := @row +1 AS rownum, id, ref1, ref2, score, eval, comment
    #                 FROM (SELECT @row :=0) r,
    #             """ + MATCH_TABLE + """
    #                  where role1 = 4 and rol2 = 4 and type1 = 'death' and type2 = 'death'
    #                  order by score desc limit 1000
    #                 ) ranked
    #             """


    cur = basic.run_query(the_query)
    desc = cur.description

    tmp_index = 1
    for row in cur.fetchall():
        row_dict = {}
        for index, value in enumerate(row):
            try:
                row_dict[desc[index][0]] = value.decode('ascii', 'ignore')
            except:
                row_dict[desc[index][0]] = value
        match_pairs[tmp_index] = row_dict
        tmp_index += 1
    logging.debug("table miss_matches imported in %s" % str(time.time() - __now__))



def load_data(limit = None):
    """ (database) --> (list of lists)
    this file imports all important tables to memory in order to increase the process speed.

    """

    global table_all_documents, table_all_persons, table_all_persons_features, block_dict

    __now__ = time.time()
    t1 = threading.Thread(target=update_persons_table, args=(limit))
    t1.daemon = True
    t1.start()




def load_table(table_name, limit = None):
    """ (string, integer) --> (list of lists)
    returns the a sql table as a python list of lists
    """
    rows_dict = {}
    if table_name == 'all_persons':
        # query = "select * from %s " % table_name
        the_query = "select id, first_name, prefix, last_name, block_key, block_id, date_1 as date, place_1 as place," \
                    " gender, role, register_id, register_type from all_persons_2014"
        if limit:
            the_query += " limit %d" % limit
    if table_name == 'all_documents':
        # query = "select * from %s" % table_name
        the_query = "select id, type_text, date, `index`, municipality, concat(latitude,',', longitude) geocode," \
                    " reference_ids from all_documents"
        if limit:
            the_query += " limit %d" % int(limit/3)

    cur = basic.run_query(the_query)
    desc = cur.description
    row_index = 1
    for row in cur.fetchall():
        row_dict = {}
        for index, value in enumerate(row):
            try:
                row_dict[desc[index][0]] = value.decode('ascii','ignore')
            except:
                row_dict[desc[index][0]] = value
        rows_dict[index] = row_dict

    return rows_dict
#
#
# def get_blocks_of_document(docuemnt_id):
#     """
#         returns the bag of blocks for a specific docuemnt
#     """
#     doc = myOrm.get_document(docuemnt_id)
#     if doc:
#
#         document_block_list = {}
#         for ref_id in doc['reference_ids'].split(','):
#             if document_block_list.get(docuemnt_id):
#                 document_block_list[docuemnt_id].append(myOrm.get_person(ref_id)['block_id'])
#             else:
#                 document_block_list[docuemnt_id] = myOrm.get_person(ref_id)['block_id']
#         return document_block_list
#     else:
#         return []


def main(limit=None):
    pass

if __name__ == "__main__":
    pass