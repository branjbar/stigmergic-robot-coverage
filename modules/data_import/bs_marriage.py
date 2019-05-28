"""
Here we convert the BS-marraige file into a SQL command!


To import the sql file use:
>> mysql links_based -uroot< sql_bs_marriage.sql

Overall: 371,000
"""
__author__ = 'bijan'

import untangle

INPUT_FILE_NAME = "/Users/Bijan/sandbox/Database/MISS-exports/BS-marriage_6899c444-4a46-b2fc-0f78-8d24de2dc491.xml"
OUTPUT_FILE_NAME = "sql_bs_marriage.sql"
FIRST_MARRIAGE_DOCUMENT_ID = 2000000
FIRST_MARRIAGE_PERSON_ID = 6000000

xml_file = open(INPUT_FILE_NAME, 'r')
xml_2_sql = open(OUTPUT_FILE_NAME, 'a')

flag = 0
# reading the header
person_id = FIRST_MARRIAGE_PERSON_ID

while not flag:
    query = ""
    new_line = xml_file.readline()
    if "export" in new_line:
        flag = 1

doc_id = FIRST_MARRIAGE_DOCUMENT_ID
threshold = 8  # counts number of <records/>
while 1:
    document = ''
    flag = 0
    while flag < threshold:
        new_line = xml_file.readline()
        document += new_line
        groom_terminate = """<field name="Bruidegom" label="Bruidegom" formtype="ChildEntity"/>"""
        bride_terminate = """<field name="Bruid" label="Bruid" formtype="ChildEntity"/>"""
        vader_groom_terminate = """<field name="Vader bruidegom" label="Vader bruidegom" formtype="ChildEntity"/>"""
        moeder_groom_terminate = """<field name="Moeder bruidegom" label="Moeder bruidegom" formtype="ChildEntity"/>"""
        vader_bride_terminate = """<field name="Vader bruid" label="Vader bruid" formtype="ChildEntity"/>"""
        moeder_bride_terminate = """<field name="Moeder bruid" label="Moeder bruid" formtype="ChildEntity"/>"""

        if ("/record" in new_line) or (vader_groom_terminate in new_line) or (moeder_groom_terminate in new_line) \
                or (vader_bride_terminate in new_line) or (moeder_bride_terminate in new_line)\
                or (groom_terminate in new_line) or (bride_terminate in new_line):
            flag += 1
    register = {'uuid': '', 'date': '', 'municipality': ''}

    groom = {'uuid': '', 'birth_date': '', 'birth_place': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    father_groom = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    mother_groom = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}

    bride = {'uuid': '', 'birth_date': '', 'birth_place': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    mother_bride = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    father_bride = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}

    try:
        obj = untangle.parse(document)
        try:
            register['uuid'] = obj.record['uuid']  # get unique id
        except:
            pass
        try:
            register['date'] = obj.record.field[5].children[0].cdata
        except:
            pass
        try:
            register['municipality'] = obj.record.field[3].children[0].children[0].children[0].children[0].cdata
        except:
            pass

        try:
            groom['uuid'] = obj.record.field[6].entity['uuid']
        except:
            pass
        try:
            groom['first_name'] = obj.record.field[6].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            groom['prefix'] = obj.record.field[6].entity.record.field[4].children[0].cdata
        except:
            pass
        try:
            groom['last_name'] = obj.record.field[6].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            groom['birth_date'] = obj.record.field[6].entity.record.field[7].children[0].cdata
        except:
            pass
        try:
            groom['birth_place'] = obj.record.field[6].entity.record.field[6].children[0].cdata
        except:
            pass


        try:
            father_groom['uuid'] = obj.record.field[7].entity['uuid']
        except:
            pass
        try:
            father_groom['first_name'] = obj.record.field[7].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            father_groom['prefix'] = obj.record.field[7].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            father_groom['last_name'] = obj.record.field[7].entity.record.field[6].children[0].cdata
        except:
            pass

        try:
            mother_groom['uuid'] = obj.record.field[8].entity['uuid']
        except:
            pass
        try:
            mother_groom['first_name'] = obj.record.field[8].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            mother_groom['prefix'] = obj.record.field[8].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            mother_groom['last_name'] = obj.record.field[8].entity.record.field[6].children[0].cdata
        except:
            pass



        try:
            bride['uuid'] = obj.record.field[9].entity['uuid']
        except:
            pass
        try:
            bride['first_name'] = obj.record.field[9].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            bride['prefix'] = obj.record.field[9].entity.record.field[4].children[0].cdata
        except:
            pass
        try:
            bride['last_name'] = obj.record.field[9].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            bride['birth_date'] = obj.record.field[9].entity.record.field[7].children[0].cdata
        except:
            pass
        try:
            bride['birth_place'] = obj.record.field[9].entity.record.field[6].children[0].cdata
        except:
            pass


        try:
            father_bride['uuid'] = obj.record.field[10].entity['uuid']
        except:
            pass
        try:
            father_bride['first_name'] = obj.record.field[10].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            father_bride['prefix'] = obj.record.field[10].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            father_bride['last_name'] = obj.record.field[10].entity.record.field[6].children[0].cdata
        except:
            pass

        try:
            mother_bride['uuid'] = obj.record.field[11].entity['uuid']
        except:
            pass
        try:
            mother_bride['first_name'] = obj.record.field[11].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            mother_bride['prefix'] = obj.record.field[11].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            mother_bride['last_name'] = obj.record.field[11].entity.record.field[6].children[0].cdata
        except:
            pass



    except:
        print document
        break

    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (`id`, `uuid`, gender, `first_name`, `prefix`, `last_name`, `date_1`, `place_1`,
            `date_2`, `place_2`, `role`, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s","%s", "%s", "%s", %d, %d, "%s");
            """ % (person_id, groom['uuid'], "male", groom['first_name'].replace('"',"'"), groom['prefix'].replace('"',"'"), groom['last_name'].replace('"',"'"), register['date'],
                   register['municipality'], groom['birth_date'],  groom['birth_place'], 1, doc_id, 'marriage')
    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (`id`, `uuid`, gender, `first_name`, `prefix`, `last_name`, `date_1`, `place_1`,
            `date_2`, `place_2`, `role`, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s","%s", "%s", "%s", %d, %d, "%s");
            """ % (person_id, bride['uuid'], "female", bride['first_name'].replace('"',"'"), bride['prefix'].replace('"',"'"), bride['last_name'].replace('"',"'"), register['date'],
                   register['municipality'], bride['birth_date'],  bride['birth_place'], 1, doc_id, 'marriage')

    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender,  `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, father_groom['uuid'], "male", father_groom['first_name'].replace('"',"'"), father_groom['prefix'].replace('"',"'"), father_groom['last_name'].replace('"',"'"), register['date'], 2, doc_id, 'marriage')

    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender,  `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, mother_groom['uuid'], "female", mother_groom['first_name'].replace('"',"'"), mother_groom['prefix'].replace('"',"'"), mother_groom['last_name'].replace('"',"'"), register['date'], 2, doc_id, 'marriage')

    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender,  `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, father_bride['uuid'], "male", father_bride['first_name'].replace('"',"'"), father_bride['prefix'].replace('"',"'"), father_bride['last_name'].replace('"',"'"), register['date'], 3, doc_id, 'marriage')

    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender,  `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, mother_bride['uuid'], "female", mother_bride['first_name'].replace('"',"'"), mother_bride['prefix'].replace('"',"'"), mother_bride['last_name'].replace('"',"'"), register['date'], 3, doc_id, 'marriage')

    query += """
            INSERT INTO `all_documents_2014` (id, uuid,  `type_text`, date, `municipality`, reference_ids)
            VALUES (%d,"%s","%s","%s","%s","%s");
            """ % (doc_id, register['uuid'], 'marriage', register['date'], register['municipality'], ','.join([str(person_id-5), str(person_id-4), str(person_id-3), str(person_id-2), str(person_id-1), str(person_id)]))


    if not doc_id % 1000:
        print doc_id

        xml_2_sql.write(query.encode('utf-8').replace('\\',''))
        query = ""

    doc_id += 1
