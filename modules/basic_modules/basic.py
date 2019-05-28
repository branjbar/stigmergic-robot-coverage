"""
Created on Jan 30, 2014

@author: Bijan

This file includes basic procedures for connecting to SQL database on the server, 
and also simple comparison modules for assigning scores to different matches. 

"""
import jellyfish
import time
import MySQLdb
import heapq

STANDARD_QUERY = "SELECT id, first_name, last_name, date_1, place_1, gender, role, register_id, register_type \
          FROM all_persons WHERE "

STANDARD_QUERY_MEERTENS = "SELECT id, name, standard, type FROM meertens_names"

global_db = None


class DB:
    conn = None
    from modules.basic_modules import config_local, config_server

    def connect(self):

        try:
            self.conn = MySQLdb.connect(**self.config_local)
        except:
            self.conn = MySQLdb.connect(**self.config_server)

    def query(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
        return cursor


def run_query(query):
    """ (string) -> (query)
    gets a SQL query and returns the list of results
    """
    global global_db
    if not global_db:
        global_db = DB()

    # cur = db.cursor()
    cur = global_db.query(query)
    return cur


def string_compare(str1, str2, method='JARO'):
    ''' (string, string, string) -> double
    returns the similarity of str1 and str2 according to the method: LEV or JARO
    
    '''

    if method == "LEV":
        # computes Levnenshtein distance which is an integer larger or equal to zero 
        return jellyfish.levenshtein_distance(str1, str2)

    if method == "JARO":
        # computes Jaro Winkler measure which is always between 0 and 1
        return jellyfish.jaro_distance(str1, str2)

    print("ERROR: Choose the right string similarity measure : LEV or JARO")


def get_match_score(ref1, ref2, level):
    ''' (dict, dict, string) --> double
    
    returns the similarity of reference 1 and 2 according to the level
    level 0 : no context
    level 1: profile context
    level 2: family context
    level 3: profile context (no year)
    level 4: family context (profile no_year)
    
    '''
    # if either person does not have any name, then score = 0 for any level
    if (not ref1['first_name'] and not ref1['last_name']) or (not ref2['first_name'] and not ref2['last_name']):
        return 0

    if level == 0:
        score_first_name = string_compare(ref1['first_name'], ref2['first_name'])
        score_last_name = string_compare(ref1['last_name'], ref2['last_name'])
        return (score_first_name + score_last_name) / 2

    if level == 1:
        score_0 = get_match_score(ref1, ref2, 0)
        MAXDISTANCE = 1.92
        import math

        score_place = 1 - ((math.fabs(ref1['place'][0] - ref2['place'][0]) \
                            + math.fabs(ref1['place'][1] - ref2['place'][1]) ) / MAXDISTANCE)

        if ref1['year'] and ref2['year']:
            MAXYEAR = 144.0
            score_year = (MAXYEAR - abs(int(ref1['year']) - int(
                ref2['year'])) ) / MAXYEAR  # score 1 for exact match and 0 for 144 years difference
        else:
            score_year = 0

        # just in case of weird numbers
        if score_year > 1: score_year = 0
        if score_year < 0: score_year = 0
        # print('score_0: ', score_0 , 'score_place:', score_place , 'score_year:', score_year, 'score_1:', (score_0 + score_place + score_year) / 3)
        return (score_0 + score_place + score_year) / 3  # HOSSEIN: DON'T USE WEIGHT

    if level == 2:
        score_1 = get_match_score(ref1, ref2, 1)
        family_1 = get_family_new(ref1)
        family_2 = get_family_new(ref2)

        score_family = 0

        # print ref1['register_type'],ref1['role'],family_1.keys(),ref2['register_type'],ref2['role'],family_2.keys()

        for rel in ['m', 'f', 'p', 'c']:
            if family_1.get(rel) and family_2.get(rel):
                score_family += get_match_score(family_1[rel], family_2[rel], 0)

        return (
                   score_1 + score_family) / 4  # in the best case, three relatives would fit. that's why we divide by 3+1=4

    if level == 3:
        score_0 = get_match_score(ref1, ref2, 0)
        MAXDISTANCE = 1.92
        import math

        score_place = (math.fabs(ref1['place'][0] - ref2['place'][0]) \
                       + math.fabs(ref1['place'][1] - ref2['place'][1]) ) / MAXDISTANCE


        # print('score_0: ', score_0 , 'score_place:', score_place , 'score_year:', score_year, 'score_1:', (score_0 + score_place + score_year) / 3)
        return (score_0 + score_place ) / 2  # HOSSEIN: DON'T USE WEIGHT

    if level == 4:
        score_1 = get_match_score(ref1, ref2, 3)
        family_1 = get_family_new(ref1)
        family_2 = get_family_new(ref2)
        score_family = 0

        for rel in ['m', 'f', 'p', 'c']:
            if family_1.get(rel) and family_2.get(rel):
                score_family += get_match_score(family_1[rel], family_2[rel], 0)

        return (
                   score_1 + score_family) / 4  # in the best case, three relatives would fit. that's why we divide by 3+1=4

    print("ERROR: Choose the right context level from {0, 1, 2, 3}")


def row_to_reference(row, table="all_persons"):
    ''' (list, table) -> (dict)
    adds labels to different elements of the list, according to the table type,
    and makes a reference
    '''

    if table == 'all_persons':
        # first get the geocode:

        place = row[4]
        if place:
            query = 'select latitude, longitude from geocode where municipality = "' + place + '"'
            cur = run_query(query)  # fetch the person with the the random id
            geocode = cur.fetchone()
        else:
            geocode = None

        ref = {}
        ref['id'] = row[0]
        ref['first_name'] = row[1]
        ref['last_name'] = row[2]
        ref['year'] = row[3][6:12]
        ref['place'] = geocode
        ref['gender'] = row[5]
        ref['role'] = row[6]
        ref['register_id'] = row[7]
        ref['register_type'] = row[8]

        return ref

    if table == 'all_documents_2014':
        ref = {}
        ref['id'] = row[0]
        ref['type_number'] = row[1]
        ref['archive'] = row[2]
        ref['type_text'] = row[3]
        ref['date'] = row[4]
        ref['index'] = row[5]
        ref['province'] = row[6]
        ref['municipality'] = row[7]
        ref['latitude'] = row[8]
        ref['longitude'] = row[9]
        ref['access no.'] = row[10]
        ref['inventory no.'] = row[11]
        return ref


def get_person(person_id=None):
    print 'wrong get_person is used!!'

    ''' (integer) -> (dict)
    return a person with the id
    '''

    # if no id then find a random person
    if person_id:
        cur = run_query(STANDARD_QUERY + ' id = ' + str(person_id))  # fetch the person with the the random id
        reference = row_to_reference(cur.fetchone())
        return reference

    if not person_id:
        flag = False  # this flag is used to be sure we get a valid person (i.e., has at least name)
        while not flag:

            # generate a random number
            from random import randrange

            person_id = randrange(1, 5244863)

            cur = run_query(STANDARD_QUERY + ' id = ' + str(person_id))  # fetch the person with the the random id
            reference = row_to_reference(cur.fetchone())
            if reference['first_name'] or reference['last_name']:
                flag = True  # if the person has name, then flag is toggled
        return reference


def get_document(document_id=None):
    print 'wrong get_document is used, use the one from myOrm!!'
    ''' (integer) -> (dict)
    return a document with the id
    '''

    # if no id then find a random person
    if document_id:
        cur = run_query('SELECT * FROM all_documents_2014 where id =' + str(document_id))
        row = cur.fetchone()
        if row:
            reference = row_to_reference(row, "all_documents_2014")
        else:
            reference = {}

        return reference

    if not document_id:
        flag = False  # this flag is used to be sure we get a valid person (i.e., has at least name)
        while not flag:

            # generate a random number
            from random import randrange

            document_id = randrange(2846095, 23729952)

            cur = run_query('SELECT * FROM all_documents_2014 where id =' + str(document_id))
            row = cur.fetchone()
            if row:
                flag = True  # if the person has name, then flag is toggled

        reference = row_to_reference(row, "all_documents_2014")
        return reference


def get_dutch_names(db):
    ''' () --> [id, name, standard]

    returns the list of names and their ids and standards
    '''

    cur = run_query(STANDARD_QUERY_MEERTENS)
    return cur.fetchall()


def insert_features(id, name, standard, document_type, f_list):
    """ (database, int, string, string, list) --> Null
    insert a feature list to the database
    """
    name = name.replace('"', ",")
    query = "insert into meertens_names_features (id, name, standard, type,  f1, f2, f3, f4, f5, f6, f7, f8, f9, f10) values (" \
            + str(id) + ',"' + name + '","' + standard + '","' + document_type + '", ' + str(f_list[0]) + "," + str(
        f_list[1]) + "," + str(f_list[2]) + "," \
            + str(f_list[3]) + "," + str(f_list[4]) + "," + str(f_list[5]) + "," + str(f_list[6]) + "," + str(
        f_list[7]) + "," \
            + str(f_list[8]) + "," + str(f_list[9]) + ')'

    # print query

    run_query(query)


def get_family_new(person):
    ''' (dict) -> (dictionary of lists)
    returns a dictionary which contains the the family members information 
    
    '''
    family = {}

    # find all relatives in the same document
    # how many relatives should be returned?
    lim = 2
    if (person['role'] == 1) and (person['register_type'] == 'marriage' or person['register_type'] == 'death'):
        lim = 3
    if (person['role'] == 6):
        lim = 1

    query = "select ref2, relation_type from relations where ref1 = " + str(person['id']) + ' limit ' + str(lim)
    cur = run_query(query)  # fetch the person with the the random id
    # for each relative find the relation type
    for row in cur.fetchall():
        relative = get_person(row[0])
        family[row[1]] = relative

    if not family:
        print('ODD!! has no family member: ', person)

    return family


def get_family(person):
    ''' (dict) -> (dictionary of lists)
    returns a dictionary which contains the the family members information 
    
    '''
    family = {}

    # find all relatives in the same document
    query = STANDARD_QUERY + " register_id = " + str(person['register_id']) \
            + " and register_type = '" + str(person['register_type']) \
            + "' and id != " + str(person['id'])
    cur = run_query(query)  # fetch the person with the the random id

    # for each relative find the relation type
    for row in cur.fetchall():
        relative = row_to_reference(row)
        rel = relation_decode(person, relative)
        if rel:
            family[rel] = relative

    if not family:
        print('ODD!! has no family member: ', person)

    return family


def relation_decode(person, relative):
    ''' (dict, dict) -> (str)
    return the relation type of two persons in the same document using their role and gender

    p: partner
    f: father
    m: mother
    c: child

    '''
    # define pairs for relation
    partner_list = [[1, 1], [1, 6], [6, 1], [5, 5], [4, 4], [2, 2], [3, 3]]
    parent_list = [[1, 5], [1, 4]]
    child_list = [[5, 1], [4, 1]]

    if [person['role'], relative['role']] in partner_list:
        return ('p')

    if [person['role'], relative['role']] in child_list:
        return ('c')

    if [person['role'], relative['role']] in parent_list:
        if relative['gender'] == 'male':
            return ('f')
        if relative['gender'] == 'female':
            return ('m')

    if person['role'] == 1 and person['gender'] == 'male':
        if relative['role'] == 2:
            if relative['gender'] == 'male':
                return ('f')
            if relative['gender'] == 'female':
                return ('m')

    if person['role'] == 1 and person['gender'] == 'female':
        if relative['role'] == 3:
            if relative['gender'] == 'male':
                return ('f')
            if relative['gender'] == 'female':
                return ('m')

    if person['role'] == 2:
        if relative['role'] == 1 and relative['gender'] == 'male':
            return ('c')

    if person['role'] == 3:
        if relative['role'] == 1 and relative['gender'] == 'female':
            return ('c')

    return None


def count_islands(level):
    '''(int) -> (int)
    returns number of islands left after the matching of requested level  
   
    level 0: no context
    level 1: profile context
    level 2: family context
    level 3: network context
    '''
    if level == 0:
        query = 'Select count(*) from all_documents_2014'
        cur = run_query(query)  # fetch the person with the the random id
        return cur.fetchone()[0]


def add_blocking_code(blocking_type=2):
    '''(int) -> ()
    adds new potential matches according to the blocking technique to the carr_match table.
    
    blocking_type 1: metaphone of last name
    '''
    import time

    if blocking_type == 1:
        import jellyfish

        count = 0
        query = 'Select id, last_name from all_persons'
        cur1 = run_query(query)  # fetch the person with the the random id

        ref_list = []
        for row in cur1.fetchall():
            ref_list.append([row[0], row[1]])
        cur1.close()
        query = ''
        for ref in ref_list:
            count += 1
            if count % 10000 == 0:
                if query:
                    # print query 
                    cur = run_query(query)
                    cur.fetchall()
                    cur.close()
                    query = ''
            metaphone = jellyfish.metaphone(ref[1])
            query += 'update all_persons set metaphone = "' + metaphone + '" where id =' + str(ref[0]) + ';'
        if query:
            cur = run_query(query)
            cur.fetchall()
            cur.close()
            query = ''

    if blocking_type == 2:
        start = time.time()
        import jellyfish

        count = 0

        # importing all names and their ids
        query = 'Select id, concat(first_name, " ", last_name) from all_persons'
        cur1 = run_query(query)  # fetch the person with the the random id
        ref_list = []
        for row in cur1.fetchall():
            ref_list.append([row[0], row[1]])
        cur1.close()

        for ref in ref_list[4300000:]:
            count += 1
            if count % 10000 == 0:
                end = time.time()
                elapsed = end - start
                print count, elapsed
                # start = time.time()

            metaphone = jellyfish.metaphone(ref[1])
            query = 'update all_persons set metaphone = "' + metaphone + '" where id =' + str(ref[0]) + ';'
            cur = run_query(query)
            cur.fetchall()
            cur.close()


def do_matching(db):
    ''' (int)->()
    does the matching on the whole database for specific level of context
    level 0 : no context
    level 1: profile context
    level 2: family context
    level 3: network context    
    '''

    import time

    # get a list of all metaphones
    query = 'SELECT distinct(metaphone) FROM links_based.all_persons where metaphone != "" '
    cur = run_query(query)
    metaphone_list = []
    for metaphone in cur.fetchall():
        metaphone_list.append(metaphone[0])

    # while True: # for parallel work, we pick a random metaphone, and do blocking that
    # from random import choice
    #         metaphone = choice(metaphone_list)

    count = 0  # to count number of matches in 3 levels

    # I manually removed the 3372087 and 4885049

    for metaphone in metaphone_list:

        # Get a list of all available matches with this metaphone
        query = 'SELECT ref1, ref2, level FROM links_based.carr_match where blocking = "' + metaphone + '"'
        cur = run_query(query)
        match_list = []
        for match in cur.fetchall():
            match_list.append([match[0], match[1], match[2]])


        # Get the complete data of all individuals in this match
        query = STANDARD_QUERY + ' metaphone = "' + metaphone + '"'
        cur = run_query(query)
        ref_list = []
        for row in cur.fetchall():
            reference = row_to_reference(row)
            ref_list.append(reference)
        for ref1 in ref_list:
            for ref2 in ref_list:

                if ref1['id'] < ref2['id']:

                    start = time.time()

                    for level in [1, 2]:
                        if not [ref1['id'], ref2['id'], level + 10] in match_list:
                            score = get_match_score(ref1, ref2, level)
                            date_time = time.strftime('%Y-%m-%d %H:%M:%S')
                            query = 'insert into carr_match (ref1,ref2,score,level, blocking, date) VALUES (' \
                                    + str(ref1['id']) + ',' + str(ref2['id']) + ',' + str(score) + ',' + str(level + 10) \
                                    + ',"' + str(metaphone) + '","' + str(date_time) + '");'
                            cur = run_query(query)
                            cur.fetchall()
                            cur.close()

                    count += 1
                    end = time.time()
                    elapsed = end - start
                    print count, elapsed


def generate_relations(doc_type):
    ''' (str)->()
    generates all the relations for doc_type and inserts them into relatins table
    '''
    # # Birth
    N = 106245
    # birth_list = []
    #     for c in range(1,N):
    #         f = c + N
    #         m = c + 2 * N
    #         birth_list.append([c,f,'f'])
    #         birth_list.append([c,m,'m'])
    #         birth_list.append([m,f,'p'])
    #         birth_list.append([f,m,'p'])
    #         birth_list.append([f,c,'c'])
    #         birth_list.append([m,c,'c'])
    #
    #     query = ''
    #     count = 0
    #     for row in birth_list:
    #         query += 'insert into relations (ref1, ref2, relation_type) values(' + str(row[0]) +',' + str(row[1]) + ',"' + str(row[2]) + '");'
    #         count += 1
    #         if count == 100:
    #             print count
    #             count = 0
    #             cur = run_query(query)
    #             cur.fetchall()
    #             cur.close()
    #             query = ''
    #
    # Death
    birth_list = []
    M = 707069
    for c in range(3 * N + 1, 3 * N + M):
        f = c + M
        m = c + 2 * M
        p = c + 3 * M
        birth_list.append([c, f, 'f'])
        birth_list.append([c, m, 'm'])
        birth_list.append([m, f, 'p'])
        birth_list.append([f, m, 'p'])
        birth_list.append([f, c, 'c'])
        birth_list.append([m, c, 'c'])
        birth_list.append([c, p, 'p'])
        birth_list.append([p, c, 'p'])

    query = ''
    count = 0
    for row in birth_list:
        query += 'insert into relations (ref1, ref2, relation_type) values(' + str(row[0]) + ',' + str(
            row[1]) + ',"' + str(row[2]) + '");'
        count += 1
        if count == 100:
            print row[0]
            count = 0
            cur = run_query(query)
            cur.fetchall()
            cur.close()
            query = ''


    # Marriage
    birth_list = []
    L = 349642
    for g in range(3 * N + 4 * M + 1, 3 * N + 4 * M + L):
        b = g + L
        fg = g + 2 * L
        mg = g + 3 * L
        fb = g + 4 * L
        mb = g + 5 * L

        birth_list.append([g, fg, 'f'])
        birth_list.append([g, mg, 'm'])
        birth_list.append([b, fb, 'f'])
        birth_list.append([b, mb, 'm'])

        birth_list.append([mg, fg, 'p'])
        birth_list.append([fg, mg, 'p'])
        birth_list.append([mb, fb, 'p'])
        birth_list.append([fb, mb, 'p'])

        birth_list.append([fg, g, 'c'])
        birth_list.append([mg, g, 'c'])
        birth_list.append([fb, b, 'c'])
        birth_list.append([mb, b, 'c'])

        birth_list.append([g, b, 'p'])
        birth_list.append([b, g, 'p'])

    query = ''
    count = 0
    for row in birth_list:
        query += 'insert into relations (ref1, ref2, relation_type) values(' + str(row[0]) + ',' + str(
            row[1]) + ',"' + str(row[2]) + '");'
        count += 1
        if count == 100:
            print row[0]
            count = 0
            cur = run_query(query)
            cur.fetchall()
            cur.close()
            query = ''


def longest_common_substring(s1, s2):
    """ (string, string) --> (integer)
    extracts the longest common substring available between two codes
    Source: http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring

    """

    m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in xrange(1, 1 + len(s1)):
        for y in xrange(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0

    return s1[x_longest - longest: x_longest]


def estimate_gender(name):
    """
    estimates the gender of a person using the majority of people with the same name
    """
    # import time
    if name:
        name = str(name)
        first_part = name.split()[0]
        query = 'select gender, count(*) from ( select gender from all_persons where first_name like "' \
                + first_part + '" and (gender = "male" or gender = "female") limit 50) as table_gender' \
                + ' group by gender order by count(*) desc limit 1 ;'

        # print query
        # print query
        # t = time.time()
        cur = run_query(query)
        row = cur.fetchone()
        if row:
            gender = row[0]
        else:
            gender = 'unknown'

    else:
        return None
    # print 'estimation time: ', time.time() - t
    return gender


def pretty(d, indent=0):
    """
    prints a pretty tree from a stored in a mixed dictionary and list
    """
    if indent < 100:
        if isinstance(d, dict):
            for key, value in d.iteritems():
                print '\t' * indent + str(key)
                if isinstance(value, dict) or isinstance(value, list):
                    pretty(value, indent + 1)
                else:
                    print '\t' * (indent + 1) + str(value)

        if d and isinstance(d, list):
            for key, item in enumerate(d):
                print '\t' * indent + str(key)
                if isinstance(item, dict) or isinstance(item, list):
                    pretty(item, indent + 1)
                else:
                    print '\t' * (indent + 1) + str(item)


def get_block_key(name1, name2, input_type='REFERENCE'):
    """
       from name1 and name2 generates a blocking key
       for input_type of reference: first name, last_name
       for input_type of document: first_name_last_name, first_name_last_name
    """

    if input_type == 'REFERENCE':
        name1 = name1.split()[0].lower().replace("'", "").encode('ascii', 'ignore').decode('ascii')
        name2 = name2.split()[0].lower().replace("'", "").encode('ascii', 'ignore').decode('ascii')

        feature_set = {'f3f': name1[:3], 'l2f': name1[-2:],
                       'f3l': name2[:3], 'l2l': name2[-2:],
                       'soundex': jellyfish.soundex(name1) + '_' + \
                                  jellyfish.soundex(name2)}

        # TODO: For now we're not considering the gender! Please check it later!

        block_key = feature_set.get('f3f', '') + '_' + feature_set.get('l2f', '') + '_' + feature_set.get('f3l',
                                                                                                          '') + '_' + feature_set.get(
            'l2l', '') + '_' + feature_set.get('soundex', '')

    if input_type == 'DOCUMENT':
        name1 = name1.strip().replace(' ','_')
        name2 = name2.strip().replace(' ','_')
        blocks = sorted([get_block_key(name1.split('_')[0], name1.split('_')[-1]),
                         get_block_key(name2.split('_')[0], name2.split('_')[-1])])

        block_key = '_'.join(blocks).decode('utf-8', 'ignore')

    return block_key



def log(msg):
    """
    prints the msg by adding time before it.
    """
    print str(time.ctime()) + ' - ' + str(msg)


def main():
    pass


if __name__ == '__main__':
    main()


