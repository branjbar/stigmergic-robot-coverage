"""
Here we convert the BS-marraige file into a SQL command!


To import the sql file use:
>> mysql links_based -uroot< sql_bs_death.sql
>> head -n 4070168 sql_bs_death.sql | tail -n 10
>> emacs sql_bs_death.sql

overall: 1,072,000
"""
__author__ = 'bijan'

import untangle

INPUT_FILE_NAME = "/Users/Bijan/sandbox/Database/MISS-exports/BS-death_7abc6156-8adf-43f5-8a98-ee009f4262e7.xml"
OUTPUT_FILE_NAME = "sql_bs_death.sql"
FIRST_DEATH_DOCUMENT_ID = 4000000
FIRST_DEATH_PERSON_ID = 18000000

xml_file = open(INPUT_FILE_NAME, 'r')
xml_2_sql = open(OUTPUT_FILE_NAME, 'a')

flag = 0
# reading the header
person_id = FIRST_DEATH_PERSON_ID

while not flag:
    query = ""
    new_line = xml_file.readline()
    if "export" in new_line:
        flag = 1

doc_id = FIRST_DEATH_DOCUMENT_ID
threshold = 5  # counts number of <records/>
while 1:
    document = ''
    flag = 0
    while flag < threshold:
        new_line = xml_file.readline()
        document += new_line
        deceased_terminate = """<field name="Overledene" label="Overledene" formtype="ChildEntity"/>"""
        vader_terminate = """<field name="Vader" label="Vader" formtype="ChildEntity"/>"""
        moeder_terminate = """<field name="Moeder" label="Moeder" formtype="ChildEntity"/>"""
        relatie_terminate = """<field name="Relatie" label="Relatie" formtype="ChildEntity"/>"""

        if ("        </record>" in new_line) and not ("          </record>" in new_line):
            flag = 10

    register = {'uuid': '', 'date': '', 'municipality': ''}

    deceased = {'uuid': '', 'gender': '', 'death_date': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    father = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    mother = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    relative = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}

    try:
        obj = untangle.parse(document)
        try:
            register['uuid'] = obj.record['uuid']  # get unique id
        except:
            pass
        try:
            register['date'] = obj.record.field[4].children[0].cdata
        except:
            pass
        # try:
        #     register['municipality'] = obj.record.field[3].children[0].children[0].children[0].children[0].cdata
        # except:
        #     pass

        try:
            deceased['uuid'] = obj.record.field[5].entity['uuid']
        except:
            pass
        try:
            deceased['first_name'] = obj.record.field[5].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            deceased['prefix'] = obj.record.field[5].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            deceased['last_name'] = obj.record.field[5].entity.record.field[6].children[0].cdata
        except:
            pass
        try:
            deceased['gender'] = obj.record.field[5].entity.record.field[7].children[0].cdata
        except:
            pass
        try:
            deceased['death_date'] = obj.record.field[5].entity.record.field[10].children[0].cdata
        except:
            pass


        try:
            father['uuid'] = obj.record.field[7].entity['uuid']
        except:
            pass
        try:
            father['first_name'] = obj.record.field[7].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            father['prefix'] = obj.record.field[7].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            father['last_name'] = obj.record.field[7].entity.record.field[6].children[0].cdata
        except:
            pass

        try:
            mother['uuid'] = obj.record.field[8].entity['uuid']
        except:
            pass
        try:
            mother['first_name'] = obj.record.field[8].entity.record.field[3].children[0].cdata
        except:
            pass
        try:
            mother['prefix'] = obj.record.field[8].entity.record.field[5].children[0].cdata
        except:
            pass
        try:
            mother['last_name'] = obj.record.field[8].entity.record.field[6].children[0].cdata
        except:
            pass



        try:
            relative['uuid'] = obj.record.field[6].entity['uuid']
        except:
            pass
        try:
            relative['first_name'] = obj.record.field[6].entity.record.field[4].children[0].cdata
        except:
            pass
        try:
            relative['prefix'] = obj.record.field[6].entity.record.field[6].children[0].cdata
        except:
            pass
        try:
            relative['last_name'] = obj.record.field[6].entity.record.field[7].children[0].cdata
        except:
            pass

    except:
        print document
        break

    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (`id`, `uuid`, gender, `first_name`, `prefix`, `last_name`, `date_1`, `place_1`,
             `role`, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s", "%s", "%s", %d, %d, "%s");
            """ % (person_id, deceased['uuid'], deceased['gender'], deceased['first_name'].replace('"',"'"), deceased['prefix'].replace('"',"'"), deceased['last_name'].replace('"',"'"), deceased['death_date'],
                   register['municipality'], 1, doc_id, 'death')
    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender,  `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, father['uuid'], "male", father['first_name'].replace('"',"'"), father['prefix'].replace('"',"'"), father['last_name'].replace('"',"'"), deceased['death_date'], 4, doc_id, 'death')

    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender,  `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, mother['uuid'], "female", mother['first_name'].replace('"',"'"), mother['prefix'].replace('"',"'").replace('"',"'"), mother['last_name'].replace('"',"'"), deceased['death_date'], 4, doc_id, 'death')

    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender,  `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s","%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, relative['uuid'], "", relative['first_name'].replace('"',"'"), relative['prefix'].replace('"',"'"), relative['last_name'].replace('"',"'"), deceased['death_date'], 6, doc_id, 'death')

    query += """
            INSERT INTO `all_documents_2014` (id, uuid,  `type_text`, date, `municipality`, reference_ids)
            VALUES (%d,"%s","%s","%s","%s","%s");
            """ % (doc_id, register['uuid'], 'death', deceased['death_date'], register['municipality'], ','.join([str(person_id-3), str(person_id-2), str(person_id-1), str(person_id)]))


    if not doc_id % 1000:
        print doc_id

        xml_2_sql.write(query.encode('utf-8').replace('\\',''))
        query = ""

    doc_id += 1
