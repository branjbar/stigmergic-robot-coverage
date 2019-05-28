"""
In this code we develop a complete matching technique for KDD conference which works as following:
For each two name references r1 and r2 in the same block, we compute their similarity as Sim_nc(r1,r2) + Sim_dc(r1,r2)

in the begining make sure that matches.csv is removed, as the results are appended to the file.
At the end the exported csv file can be imported in mysql using:
    LOAD DATA INFILE '/Users/Bijan/sandbox/Eclipse_Projects/linkPy/data/matching_kdd/matches.csv'
    INTO TABLE miss_matches FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';
"""
import pickle
import math
from modules.basic_modules import basic
from modules.basic_modules.basic import log


def import_block_and_reference_dicts(from_file=True):
    """
    generates block, reference and documents details required for matching

    reference_dict = {ref_id: first_name, last_name, block_id, role, register_id, register_type}
    block_dict = {block_id: block_key, [ref1_id, ref2_id, ...], block_size}
    document_dict = {document_id: {'references': [ref1_id, ref2_id, ...],
                     'blocks': [block1_id, block2_id, ...],
                     'type':register_type}}
    """
    global block_dict, reference_dict, document_dict

    if not from_file:

        log("import blocks started")

        block_query = " SELECT id, first_name, last_name, block_key, block_id, role, register_id, register_type" \
                      " FROM links_based.all_persons_2014"

        cur = basic.run_query(block_query)
        count = 0
        block_dict = {}
        reference_dict = {}
        document_dict = {}
        for row in cur.fetchall():
            ref_id = row[0]
            first_name = row[1]
            last_name = row[2]
            block_key = row[3]
            block_id = row[4]
            role = row[5]
            register_id = row[6]
            register_type = row[7]

            # add name and block to reference dictionary
            reference_dict[ref_id] = [first_name, last_name, block_id, role, register_id, register_type]

            # add the reference to block dictionary
            if not block_dict.get(block_id):
                block_dict[block_id] = [block_key, [ref_id], 1]
            else:
                block_dict[block_id][1].append(ref_id)
                block_dict[block_id][2] += 1

            # add block to document dict
            if not document_dict.get(register_id):
                document_dict[register_id] = {'references': [ref_id],
                                              'blocks': [block_id],
                                              'type': register_type,
                                              }
            else:
                document_dict[register_id]['references'].append(ref_id)
                document_dict[register_id]['blocks'].append(block_id)

            count += 1
            if not count % 10000:
                print count / 10000

        log("importing data ended.")
    #     log("dumping data might take up to 12 minutes...")
    #
    #     with open('../../data/matching_kdd/import_data.txt', 'w') as f:
    #         pickle.dump([block_dict, reference_dict, document_dict], f)
    #
    #    log("dumping blocks ended.")
    # else:
    #     log("importing data dump. might take up to 8 minutes ")
    #     with open('../../data/matching_kdd/import_data.txt', 'r') as f:
    #         block_dict, reference_dict, document_dict = pickle.load(f)


def get_similarity_no_context(ref1, ref2):
    """
    compute the no context similarity between two references based on their name similarity
    """
    global block_dict, reference_dict, document_dict

    first_name_ref1 = reference_dict[ref1][0]
    last_name_ref1 = reference_dict[ref1][1]
    first_name_ref2 = reference_dict[ref2][0]
    last_name_ref2 = reference_dict[ref2][1]

    sim_nc = (basic.string_compare(first_name_ref1, first_name_ref2) + basic.string_compare(last_name_ref1,
                                                                                            last_name_ref2)) / 2.0

    return sim_nc


def get_similarity_document_context(ref1, ref2):
    """
    compute the document context similarity between two references based on similarity of block bags
    """
    global block_dict, reference_dict, document_dict

    doc1 = reference_dict[ref1][4]
    doc2 = reference_dict[ref2][4]

    numerator = 0
    denominator = 0

    block_list_1 = set(document_dict[doc1]['blocks'])
    block_list_2 = set(document_dict[doc2]['blocks'])

    for b in block_list_1.intersection(block_list_2):
        if b != 1888:
            confidence = 1.0 / block_dict[b][2]  # block confidence
            numerator += confidence

    if numerator > 0:
        for b in block_list_1.union(block_list_2):
            if b != 1888:
                confidence = 1.0 / block_dict[b][2]  # block confidence
                denominator += confidence

        sim_dc = numerator / denominator
    else:
        sim_dc = 0

    return sim_dc


def extract_matches():
    """
    parse through all blocks, and for each reference pairs in each block check the similarity
    """

    global block_dict, reference_dict, document_dict
    csv_text = ''
    log("extracting matches started.")

    sim_dict = {}
    count = 1  # just a simple counter
    for block in block_dict.values():
        if block[2] < 100 and block[0] != 1888:  # max size of block (usually less than 100)
            for ref1 in block[1]:
                for ref2 in block[1]:
                    if reference_dict[ref1][4] != reference_dict[ref2][4] \
                            and ref2 > ref1:  # the first condition is to avoid inner documents matches
                        sim = get_similarity_no_context(ref1, ref2) + get_similarity_document_context(ref1, ref2)
                        if sim > 0:
                            # match_instance = [ref1,
                            #                   ref2,
                            #                   sim,
                            #                   reference_dict[ref1][4],  # doc1 id
                            #                   reference_dict[ref2][4],  # doc2 id
                            #                   reference_dict[ref1][3],  # role in doc1
                            #                   reference_dict[ref2][3],  # role in doc2
                            #                   reference_dict[ref1][5],  # register_type
                            #                   reference_dict[ref2][5],  # register_type
                            #                   ]
                            # csv_text += str(count) + ',' + ''.join([str(d) + ',' for d in match_instance])[:-1] + '\n'
                            sim_dict[math.floor(sim*100)/100.0] = sim_dict.get(math.floor(sim*100)/100.0,0) + 1

    log("extracting matches ended.")
    log("storing files in csv file.")

    print sim_dict

def main():

    import_block_and_reference_dicts(from_file=False)
    extract_matches()

if __name__ == "__main__":
    main()

