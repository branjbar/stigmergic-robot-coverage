from modules.basic_modules import myOrm, basic

__author__ = 'Bijan'

ALL_PERSONS_QUERY = "select * from all_persons"
import jellyfish
import time
import logging

genders_dict = {}  # this is used to store all the names with majority gender




def extract_block_key(person, gender_names):
    feature_set = {'id': person['id'],
                   'first_name': person['first_name'].replace("'", ""),
                   'last_name': person['last_name'].replace("'", ""),
                   'role': person['role'],
                   'register_type': person['register_type'],
                   'register_id': person['register_id']}
    if person['gender'] == "male" or person['gender'] == "female":
        feature_set['gender'] = person['gender']

    if p['first_name'] and person['last_name']:
        if not (person['gender'] == "male" or person['gender'] == "female"):
            first_split = person['first_name'].split()[0]
            if first_split in gender_names['male']:
                feature_set['gender'] = "male"
                # print first_split, "male"
            if first_split in gender_names['female']:
                feature_set['gender'] = "female"
                # print first_split, "female"
            if first_split not in gender_names['male'] and first_split not in gender_names['female']:
                feature_set['gender'] = "unknown"
                # print first_split, "unknown"

        feature_set['f3f'] = person['first_name'].split()[0][:3].replace("'", "")
        feature_set['l2f'] = person['first_name'].split()[0][-2:].replace("'", "")

        feature_set['f3l'] = person['last_name'].split()[0][:3].replace("'", "")
        feature_set['l2l'] = person['last_name'].split()[0][-2:].replace("'", "")

        feature_set['soundex'] = jellyfish.soundex(person['first_name'].split()[0].replace("'", "")) + '_' + \
                                 jellyfish.soundex(person['last_name'].split()[0].replace("'", ""))

        feature_set['block_key'] = feature_set.get('gender', '') + '_' + feature_set.get('f3f',
                                                                                         '') + '_' + feature_set.get(
            'f3l', '') + '_' \
                                   + feature_set.get('l2f', '') + '_' + feature_set.get('l2l',
                                                                                        '') + '_' + feature_set.get(
            'soundex', '')
    else:
        feature_set['gender'] = ''
        feature_set['soundex'] = ''
        feature_set['block_key'] = ''
        feature_set['f3f'] = ''
        feature_set['f3l'] = ''
        feature_set['l2l'] = ''
        feature_set['l2f'] = ''

    return feature_set


def get_block_ids(db):
    """
        extracts the current block keys and their ids for using in insertion of new blocks
    """
    global block_set, max_block_id
    block_id_query = 'SELECT distinct(block_id), block_key FROM links_based.all_persons_features';
    cur = basic.run_query(block_id_query)
    for row in cur.fetchall():
        block_set[row[1]] = row[0]
        if row[0] > max_block_id:
            max_block_id = row[0]


def insert_blocking_keys(sb, f_set):
    """
        inserts the features and blocking key to the features table
    """
    # global block_set, max_block_id
    # if block_set.get(f_set['block_key']):
    # block_id = block_set.get(f_set['block_key'])
    # else:
    #     max_block_id += 1
    #     block_id = max_block_id
    #     block_set[f_set['block_key']] = block_id
    block_id = 0

    insert_query = "insert into all_persons_features (id, first_name, last_name, role, document_type, document_id," \
                   " gender , f3f, f3l, l2f, l2l, soundex, block_key, block_id) values (" + str(f_set['id']) \
                   + ",'" + f_set['first_name'] + "','" + f_set['last_name'] + "','" + str(f_set['role']) \
                   + "', '" + str(f_set['register_type']) + "'," + str(f_set['register_id']) + ",'" + str(
        f_set['gender']) \
                   + "','" + str(f_set['f3f']) + "','" + str(f_set['f3l']) + "','" + str(f_set['l2f']) + "','" \
                   + str(f_set['l2l']) + "','" + str(f_set['soundex']) + "','" + str(f_set['block_key']) + "'," + str(
        block_id) + ");"

    # print insert_query
    return insert_query


def do_blocking(gender_names):
    """
    does the blocking by adding the blocking key and feature_sets for all the persons; everything
    is added to all_persons_features
    """
    # cur = basic.run_query('SELECT count(*) FROM links_based.all_persons_features')
    # N = cur.fetchone()[0]
    # N = 1000000

    blocking_query = "select id, first_name, last_name, date_1, place_1, gender, role, register_id, register_type" \
                     " from all_persons where not exists " \
                     "(select all_persons_features.id from all_persons_features " \
                     "where all_persons.id = all_persons_features.id)"

    cur = basic.run_query(blocking_query)
    logging.debug("importing persons")
    row_list = []
    for c in cur.fetchall():
        row_list.append(c)

    logging.debug("extracting features")
    cum_query = ''
    query_count = 0
    t = time.time()
    for row in row_list:
        query_count += 1
        person = myOrm.row_to_reference(row)
        f_set = extract_block_key(person, gender_names)
        cum_query += insert_blocking_keys(f_set)

        if not query_count % 1000:
            # print cum_query
            query_count = 0
            basic.run_query(cum_query)
            logging.debug('elapsed time in extracting featuresis %s' % str(time.time() - t))
            t = time.time()
            cum_query = ''

    basic.run_query(cum_query)


def get_name_gender_list(db):
    male_query = '''
                select name1 from (
                select substring_index(first_name, ' ', 1) as name1, gender, count(*) as cnt1 from all_persons
                where gender = "male"
                group by substring_index(first_name, ' ', 1)
                ) as t1 where t1.cnt1 > 10 and t1.name1 != '' and not exists ( select * from
                (
                select * from (
                select substring_index(first_name, ' ', 1) as name, gender, count(*) as cnt from all_persons
                where gender = "female"
                group by substring_index(first_name, ' ', 1)
                ) as t2
                where t2.cnt > 10 and t2.name != '' ) as t3 where t1.name1 = t3.name and cnt1 < t3.cnt)
                '''
    female_query = '''
                    select name1 from (
                    select substring_index(first_name, ' ', 1) as name1, gender, count(*) as cnt1 from all_persons
                    where gender = "female"
                    group by substring_index(first_name, ' ', 1)
                    ) as t1 where t1.cnt1 > 10 and t1.name1 != '' and not exists ( select * from
                    (
                    select * from (
                    select substring_index(first_name, ' ', 1) as name, gender, count(*) as cnt from all_persons
                    where gender = "male"
                    group by substring_index(first_name, ' ', 1)
                    ) as t2
                    where t2.cnt > 10 and t2.name != '' ) as t3 where t1.name1 = t3.name and cnt1 < t3.cnt)
                    '''

    male_names = []
    cur = basic.run_query(male_query)
    for name in cur.fetchall():
        male_names.append(name[0])

    female_names = []
    cur = basic.run_query(female_query)
    for name in cur.fetchall():
        female_names.append(name[0])

    return {'male': male_names, 'female': female_names}


if __name__ == "__main__":
    # gender_names = get_name_gender_list()
    # max_block_id = 0
    # block_set = {}
    # get_block_ids(db)
    # do_blocking(gender_names)
    # print get_block_key('Bijan', 'Ranjbar Sahraei')

    pass