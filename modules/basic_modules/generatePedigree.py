
__author__ = 'Bijan'
"""
    here the idea is to get a person id, and generating the complete pedegree, assuming there is just one root with
    two parents and those have each two parents, and so on so forth
"""

from modules.basic_modules import myOrm, basic
import random, copy, csv
import os

if os.path.isdir("../data/"):
    DATA_FOLDER = "../data/"
else:
    DATA_FOLDER = "/Users/bijan/sandbox/stigmergic-robot-coverage/data/"




BLANK_DICT = {"fname": "", "lname": "", "date": '', "location": '',
              "register_id": '', "register_type": '', "id": '', 'parents': []}

family_3 = []
family_4 = []
family_5 = []



def pedigree(document, selected_id=None, blocks=None, selected_role=None):
    """ (int) --> json dict
    """


    p_dict_dict = {}
    if document:
        person_id_list = document['reference_ids'].split(',')
        index = 0
        for person_id in person_id_list:
            person = myOrm.get_person(int(person_id))
            if person:
                if person['first_name'] or person['last_name']:
                    if person['role'] in [1, 6]:
                        p_dict = {
                        "fname": person['first_name'],
                        "lname": (person['prefix'] + ' ' + person['last_name']).strip().replace('  ', ' '),
                        "date": person['date'][:4],
                        "location": person['place'], #[:20],
                        "register_id": person['register_id'],
                        "register_type": person['register_type'],
                        "id": person['id'],
                        "gender": person['gender'],
                        "parents": []
                        }
                    else:
                        p_dict = {
                        "fname": person['first_name'],
                        "lname": (person['prefix'] + ' ' + person['last_name']).strip().replace('  ', ' '),
                        "date": '',
                        "location": '',
                        "id": person['id'],
                        "parents": []
                        }

                else: # if no name is available, then we make all fields empty
                    p_dict = copy.deepcopy(BLANK_DICT)



                if selected_id and person['id'] == selected_id:
                    p_dict['selected'] = 'true'

                if blocks and person['block_id'] in blocks:
                    p_dict['selected'] = 'true'

                if selected_role and person['role'] == selected_role:
                    p_dict['selected'] = 'true'

                index += 1
                p_dict_dict[index] = []
                p_dict_dict[index].append(p_dict)


    tree = get_tree(p_dict_dict)
    return tree

def get_tree(p_dicts):
    """
    using a list of personal_details, one per person generates a pedigree for visualization.

    """
    tree = {}
    # Birth Certificate
    if p_dicts and p_dicts.get(1) and p_dicts.get(2) and p_dicts.get(3) and not p_dicts.get(4):

        tree = copy.deepcopy(p_dicts[1][0])
        tree['born'] = 'true'
        # parents of born
        tree['parents'].append(p_dicts[2][0])
        tree['parents'].append(p_dicts[3][0])

    # Death certificate
    if p_dicts and p_dicts.get(1) and p_dicts.get(2) and p_dicts.get(3) and p_dicts.get(4) and not p_dicts.get(5):
        tree = copy.deepcopy(BLANK_DICT)

        if p_dicts[1][0]['gender'] == 'male':
            tree['parents'].append(p_dicts[1][0])

            # relative of deceased
            tree['parents'].append(p_dicts[4][0])

            # parents of deceased
            tree['parents'][0]['parents'].append(p_dicts[2][0])
            tree['parents'][0]['parents'].append(p_dicts[3][0])

        else:
            tree['parents'].append(p_dicts[4][0])

            # relative of deceased
            tree['parents'].append(p_dicts[1][0])

            # parents of deceased
            tree['parents'][1]['parents'].append(p_dicts[2][0])
            tree['parents'][1]['parents'].append(p_dicts[3][0])


    # Marriage Certificate
    if p_dicts and p_dicts.get(1) and p_dicts.get(2) and p_dicts.get(3) and p_dicts.get(4) and p_dicts.get(5):
        tree = copy.deepcopy(BLANK_DICT)
        # groom
        tree['parents'].append(p_dicts[1][0])

        # bride
        tree['parents'].append(p_dicts[2][0])

        # parents of groom
        tree['parents'][0]['parents'] = []
        tree['parents'][0]['parents'].append(p_dicts[3][0])
        tree['parents'][0]['parents'].append(p_dicts[4][0])

        # parents of bride
        tree['parents'][1]['parents'] = []
        tree['parents'][1]['parents'].append(p_dicts[5][0])
        tree['parents'][1]['parents'].append(p_dicts[6][0])

    return tree


def integrate_pedigrees(document_tree, depth=1):

    tree = document_tree['pedigree']

    for index, parent in enumerate(document_tree['parents']):
        tree['parents'][index]['parents'] = parent['pedigree']['parents']

        tree['parents'][index]['selected'] = 'true'
        tree['parents'][index]['parents'][0]['selected'] = 'true'
        tree['parents'][index]['parents'][0]['parents'][0]['selected'] = 'true'


    return tree

def import_families():
    global family_3, family_4, family_5

    if not family_3:

        with open(DATA_FOLDER + "family_depth_3.csv", "rb") as myfile:
            reader = csv.reader(myfile)
            for row in reader:
                family_3.append(row)

        with open(DATA_FOLDER + "family_depth_4.csv", "rb") as myfile:
            reader = csv.reader(myfile)
            for row in reader:
                family_4.append(row)

        with open(DATA_FOLDER + "family_depth_5.csv", "rb") as myfile:
            reader = csv.reader(myfile)
            for row in reader:
                family_5.append(row)

    return ([family_3, family_4, family_5])

def check_pedigrees(depth=4, family_id=1):
    if not family_3:
        import_families()

    if depth == 3:

        if not family_id:
            family = random.choice(family_3)
        else:
            family = family_3[family_id]

        document_tree_0 = {'pedigree':pedigree(myOrm.get_document(family[0])),
                           'parents': [{'pedigree':pedigree(myOrm.get_document(family[1]))},
                                     {'pedigree':pedigree(myOrm.get_document(family[2]))},
                                    ],
                        }

    if depth == 4:
        if not family_id:
            family = random.choice(family_4)
        else:
            family = family_4[family_id]


        document_tree_1 = {'pedigree':pedigree(myOrm.get_document(family[3])),
                         'parents': [{'pedigree':pedigree(myOrm.get_document(family[4]))},
                                     {'pedigree':pedigree(myOrm.get_document(family[5]))},
                                    ],
                        }


        document_tree_2 = {'pedigree':pedigree(myOrm.get_document(family[6])),
                         'parents': [{'pedigree':pedigree(myOrm.get_document(family[7]))},
                                     {'pedigree':pedigree(myOrm.get_document(family[8]))},
                                    ],
                        }


        document_tree_0 = {'pedigree':pedigree(myOrm.get_document(family[0])),
                           'parents': [{'pedigree': integrate_pedigrees(document_tree_1)},
                                     {'pedigree': integrate_pedigrees(document_tree_2)},
                                    ],
                        }

    if depth == 5:

        if not family_id:
            family = random.choice(family_5)
        else:
            family = family_5[family_id]


        document_tree_22 = {'pedigree':pedigree(myOrm.get_document(family[18])),
                         'parents': [{'pedigree':pedigree(myOrm.get_document(family[19]))},
                                     {'pedigree':pedigree(myOrm.get_document(family[20]))},
                                    ],
                        }


        document_tree_21 = {'pedigree':pedigree(myOrm.get_document(family[15])),
                         'parents': [{'pedigree':pedigree(myOrm.get_document(family[16]))},
                                     {'pedigree':pedigree(myOrm.get_document(family[17]))},
                                    ],
                        }


        document_tree_2 = {'pedigree':pedigree(myOrm.get_document(family[12])),
                         'parents': [{'pedigree': integrate_pedigrees(document_tree_21)},
                                     {'pedigree': integrate_pedigrees(document_tree_22)},
                                    ],
                        }


        document_tree_12 = {'pedigree':pedigree(myOrm.get_document(family[9])),
                         'parents': [{'pedigree':pedigree(myOrm.get_document(family[10]))},
                                     {'pedigree':pedigree(myOrm.get_document(family[11]))},
                                    ],
                        }


        document_tree_11 = {'pedigree':pedigree(myOrm.get_document(family[6])),
                         'parents': [{'pedigree':pedigree(myOrm.get_document(family[7]))},
                                     {'pedigree':pedigree(myOrm.get_document(family[8]))},
                                    ],
                        }




        document_tree_1 = {'pedigree':pedigree(myOrm.get_document(family[3])),
                         'parents': [{'pedigree': integrate_pedigrees(document_tree_11)},
                                     {'pedigree': integrate_pedigrees(document_tree_12)},
                                    ],
                        }


        document_tree_0 = {'pedigree':pedigree(myOrm.get_document(family[0])),
                           'parents': [{'pedigree': integrate_pedigrees(document_tree_1)},
                                     {'pedigree': integrate_pedigrees(document_tree_2)},
                                    ],
                        }

    integrated_tree = integrate_pedigrees(document_tree_0)

    return integrated_tree


def get_document_ids(parents, flag=False):
    if parents:
        id_list = [parents[0].get('register_id'),parents[1].get('register_id')]

        id_list += get_document_ids(parents[0]['parents'])
        id_list += get_document_ids(parents[1]['parents'])
    else:
        id_list = []

    return id_list



if __name__ == "__main__":
    pass


    # print pedigree()