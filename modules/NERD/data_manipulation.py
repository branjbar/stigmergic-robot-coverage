"""
Here we export the results of NERD in form of offline html file, sql table, etc.

"""
import time
import operator
from modules.NERD import html_generate
from modules.NERD.dict_based_nerd import Nerd
from modules.basic_modules import basic
from modules.basic_modules.basic import log

__author__ = 'bijan'
from modules.NERD.dict_based_nerd import Nerd


def find_frequent_words():
    """
    here we parse through all the available names and find the most frequent ones.
    :return:
    """

    word_dict = {}

    log('importing names')
    the_query = "SELECT text1, text2, text3, row_id, id from notary_acts"
    cur = basic.run_query(the_query)
    for c in cur.fetchall():
        text = c[0] + ' ' + c[1] + ' ' + c[2]
        nerd = Nerd(text)
        for word in nerd.pp_text.split():
            word_dict[word] = word_dict.get(word,0) + 1

    sorted_x = sorted(word_dict.iteritems(), key=operator.itemgetter(1), reverse=True)

    for x in sorted_x[:100]:
        print x


def generate_html_report():
    log('importing names')
    the_query = "SELECT name, type FROM meertens_names"
    cur = basic.run_query(the_query)
    name_dict = {}
    name_list = []
    for c in cur.fetchall():
        name_dict[c[0].lower()] = c[1]
        name_list.append(c[0].lower())

    log('importing notarial acts')
    the_query = """select * from (
                    select text1, text2, text3 FROM labeled_acts as l1
                    inner join
                    notary_acts as l2
                    where LEFT(text, 200)  = LEFT(text1, 200)
                    ) as T
                    """
    cur = basic.run_query(the_query)
    notarial_list = []
    for c in cur.fetchall()[:1000]:
        # each notarial_list element is [text, date, place]
        notarial_list.append([c[0] + ' ' + c[1] + ' ' + c[2]])

    log('extracting names')
    output = []
    # TODO: To be checked!
    for n in notarial_list:
        text = n[0]
        nerd = Nerd(text)
        output.append([text, nerd.word_list_labeled, nerd.get_references()])
    html_generate.export_html(output)


def export_names_to_sql_table():
    """
    here we replace frog, and extract names from text.
    The extracted names are added to natary_acts_refse as following:
    id, reference, index, text_id, text_row_id


    Data can be loaded to sql by using following command
    LOAD DATA INFILE 'extracted_names.csv'
    INTO TABLE notary_acts_refs FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';
    """
    ref_id = 0
    log('importing notarial acts')
    the_query = "SELECT text1, text2, text3, row_id, id from notary_acts"
    cur = basic.run_query(the_query)
    notarial_list = []
    for c in cur.fetchall():
        # each notarial_list element is [text, date, place]
        notarial_list.append([c[0] + ' ' + c[1] + ' ' + c[2], c[4], c[3]])

    log('extracting names')
    now = time.time()
    for n in notarial_list:
        text = n[0]
        nerd = Nerd(text)
        for ref in nerd.get_references():
            ref_id += 1
            csv_text = str(ref_id) + ',' + str(ref[1]) + ',' + str(ref[0]) + ',' + str(n[1]) + ',' + str(n[2]) + '\n'
            with open("../../data/extracted_names.csv", "a") as my_file:
                                my_file.write(csv_text)

    print time.time() - now


def export_patterns_to_sql_table():
    """
    for every two extracted reference finds the pattern in between
    :return:
    """

    log('importing notarial acts')
    the_query = "SELECT text1, text2, text3, row_id, id from notary_acts"
    cur = basic.run_query(the_query)
    notarial_list = []
    for c in cur.fetchall():
        # each notarial_list element is [text, date, place]
        notarial_list.append([c[0] + ' ' + c[1] + ' ' + c[2], c[4], c[3]])

    log('extracting names and looking at patterns')
    now = time.time()
    freq_term = {}
    term_example = {}
    for n in notarial_list:
        text = n[0]
        text = text_pre_processing(text)
        word_list = text.split()
        if word_list:
            word_spec = extract_name(word_list)
            ref_list = extract_references(word_list, word_spec)
            for index1, ref1 in enumerate(ref_list):
                for index2, ref2 in enumerate(ref_list):
                    if index2 == index1 + 1:
                        # print ref1[1]
                        # term_len = ref2[0] - ref1[0] - len(ref1[1].split())
                        # if term_len < 6:
                        term = ' '.join(word_list[ref1[0] + len(ref1[1].split()):ref2[0]])
                        freq_term[term] = freq_term.get(term, 0) + 1
                        if not n[1] in term_example.get(term,[]) and len(term_example.get(term,[])) < 20:
                            term_example[term] = term_example.get(term,[]) + [n[2]]


    print time.time() - now

    import operator
    sorted_x = sorted(freq_term.iteritems(), key=operator.itemgetter(1), reverse=True)
    for x in sorted_x:
        phrase = [y for y in x]
        if phrase[1] > 20:
            example = ''
            for text_id in term_example[phrase[0]]:
                example += str(text_id) + ', '

            query = """
                    INSERT INTO relation_indicator (phrase,freq,example)
                    VALUES ("%s", %d, "%s");
            """ %(phrase[0], phrase[1], example[:-2])
            basic.run_query(query)


def look_for_pattern():

    """
    for every two extracted reference finds the pattern in between
    :return:
    """

    ref_id = 0
    log('importing notarial acts')
    the_query = "SELECT text1, text2, text3, row_id, id from notary_acts"
    cur = basic.run_query(the_query)
    notarial_list = []
    for c in cur.fetchall():
        # each notarial_list element is [text, date, place]
        notarial_list.append([c[0] + ' ' + c[1] + ' ' + c[2], c[4], c[3]])

    log('extracting names and looking at patterns')
    now = time.time()
    freq_term = {}
    for n in notarial_list:
        text = n[0]
        text = text_pre_processing(text)
        word_list = text.split()
        if word_list:
            word_spec = extract_name(word_list)
            ref_list = extract_references(word_list, word_spec)
            for index1, ref1 in enumerate(ref_list):
                for index2, ref2 in enumerate(ref_list):
                    if index2 == index1 + 1:
                        term = ' '.join(word_list[ref1[0] + len(ref1[1].split()) :ref2[0]])
                        if '( president )' in term :
                            print n[2]

if __name__ == "__main__":
    export_names_to_sql_table()

