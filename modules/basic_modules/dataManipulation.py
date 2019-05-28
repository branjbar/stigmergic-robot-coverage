__author__ = 'Bijan'

from modules.basic_modules import basic
import logging
import time
import pickle

def refresh_person_id(db):
    """
        this module copies all the references in a new table with modified ids sorted based on documents ids.
    """

    q = "select id, register_id from all_persons"
    cur = basic.run_query(q)
    register_dict = {}
    for c in cur.fetchall():
        if not register_dict.get(int(c[1])):
            register_dict[int(c[1])] = [int(c[0])]
        else:
            register_dict[int(c[1])].append(int(c[0]))

    print 'table imported'
    index = 0
    query = ''
    register_dict = sorted(register_dict.items(), key=lambda s: s[0])
    print register_dict[:10]
    for key in register_dict:
        s = ''
        for ref in key[1]:
            index += 1
            if index > 2387327:
                query += "insert into all_persons_2014 select %d id, id id_old, first_name, prefix, last_name, block_key," \
                         " block_id, date_1, place_1, date_2, place_2, gender, role, register_id, register_type " \
                         "from all_persons where id = %d;\n" % (index, ref)
            s += str(index) + ','
        if index > 2387320:
            query += "update all_documents_2014 set reference_ids = '%s' where id = %d;\n" % (s[:-1], key[0])

        if not index % 10000:
            with open("query.sql", "a") as myfile:
                myfile.write(query)
            query = ''
            print index
    with open("query.sql", "a") as myfile:
        myfile.write(query)
    query = ''
    print index


def referesh_register_id(db):
    """
        updates the (register_ids) in table all_documents as the person ids have been changed previously
    """
    q = "select id, register_id from all_persons_2014"
    cur = basic.run_query(q)
    register_dict = {}
    for c in cur.fetchall():
        if not register_dict.get(c[1]):
            register_dict[c[1]] = str(c[0])
        else:
            register_dict[c[1]] += ',' + str(c[0])

    print 'table imported'
    index = 0
    query = ''
    # register_dict = sorted(register_dict.items(), key=lambda s: s[0])
    for key in register_dict:
        index += 1
        query += "update all_documents_2014 set reference_ids = '%s' where id = %s;\n" % (register_dict[key], key)
        if not index % 1000:
            with open("query2.sql", "a") as myfile:
                myfile.write(query)
            query = ''
    with open("query2.sql", "a") as myfile:
        myfile.write(query)
    query = ''
    print index





def extract_matches():
    """
    according to the blocking keys extracts every pair of references that are connected to
    each other with one, two or more number of blocks.
    """

    t = time.time()

    logging.debug('Importing table started')
    pickled_file = open('data/block_dump_full.txt', 'r')
    blocks_dict = pickle.load(pickled_file)

    # print blocks_dict
    logging.debug('table imported in %s' % str(time.time()-t))

    t = time.time()
    logging.debug('generating matches started')


    matches_dict = {}
    block_index = 1
    for b in blocks_dict.keys():
        if b != [1888] and len(blocks_dict[b]['docs']) < 30:

            block_index += 1
            if not block_index % 1000:
                print block_index, b

            for doc1 in blocks_dict[b]['docs']:
                for doc2 in blocks_dict[b]['docs']:
                    if not doc1[0] is doc2[0]:
                        if int(doc1[0]) < int(doc2[0]):
                            key = str(doc1[0]) + '_' + str(doc2[0])

                            person_ids = sorted([int(doc1[1]), int(doc2[1])])
                            block_tuple = [len(blocks_dict[b]['docs']), person_ids[0],person_ids[1],blocks_dict[b]['block_key'], b]
                            if matches_dict.get(key) and not block_tuple in matches_dict[key]:
                                matches_dict[key].append(block_tuple)
                                # print (doc1[0],  doc2[0]), '<-', matches_dict[key]['block_id']
                            else:
                                matches_dict[key] = [block_tuple]

    logging.debug('matches generated imported in %s' % str(time.time()-t))
    return matches_dict


def write_variable_to_file(variable, file_name):
    # db = basic.do_connect()
    # matches_dict = extract_matches(db)
    file = open(file_name, 'w')
    pickle.dump(variable, file)
    file.close()


if __name__ == "__main__":

    logging.basicConfig(filename='logging.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.info('________________new________________')
    matches_dict = extr/Users/bijan/PycharmProjects/MiSS/modules/record_linkage/dynak/matching_kdd.pyact_matches()

    index = 1
    csv_text = ''
    for key in matches_dict.keys():
        if len(matches_dict[key]) > 1:
            s = ''
            for m in matches_dict[key]:
                s += '['
                for j in m[:-1]:
                    s += str(j) + ','
                s += str(m[-1]) + '],'

            s = s[:-1]
            csv_text += str(index) + ';' + key.replace('_',';') + ';' + str(len(matches_dict[key])) + ';' + s + '\n'
            index +=1
            if not index % 1000:
                with open("data/matches.csv", "a") as myfile:
                    myfile.write(csv_text)
                csv_text = ''
                logging.info('csv file generated for up to row %d' % index)

    with open("data/matches.csv", "a") as myfile:
        myfile.write(csv_text)
    csv_text = ''