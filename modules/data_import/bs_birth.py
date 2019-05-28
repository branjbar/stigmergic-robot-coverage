"""
Overall: 595000
"""
__author__ = 'bijan'

import untangle
xmldoc = '/Users/Bijan/sandbox/Database/MISS-exports/BS-birth_a69dbe15-9c9b-b331-6497-f4e8c5288bf1.xml'
xml_file = open(xmldoc, 'r')
flag = 0
threshold = 4
# reading the header
person_id = 0

while not flag :
    query = ""
    new_line = xml_file.readline()
    vader_terminate = """<field name="Vader" label="Vader" formtype="ChildEntity"/>"""
    if "export" in new_line:
        flag = 1

doc_id = 1
xml_2_sql = open('sql_bs_birth.sql', 'a')
while 1:
    document = ''
    flag = 0
    while flag < threshold:
        new_line = xml_file.readline()
        document += new_line
        vader_terminate = """<field name="Vader" label="Vader" formtype="ChildEntity"/>"""
        moeder_terminate = """<field name="Moeder" label="Moeder" formtype="ChildEntity"/>"""
        kind_terminate = """<field name="Kind" label="Kind" formtype="ChildEntity"/>"""

        if not (not ("/record" in new_line) and not (vader_terminate in new_line) and not (
            moeder_terminate in new_line) and not (kind_terminate in new_line)):
            flag += 1
    register = {'uuid': '', 'date': ''}
    kid = {'uuid': '', 'gender': '', 'birth_date': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    father = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}
    mother = {'uuid': '', 'first_name': '', 'prefix': '', 'last_name': ''}

    try:
        obj = untangle.parse(document)
        try: register['uuid'] = obj.record['uuid'] # get unique id
        except: pass
        try: register['date'] = obj.record.field[4].children[0].cdata
        except: pass
        
        try: kid['uuid'] = obj.record.field[5].entity['uuid']
        except: pass

        try: kid['gender'] =  obj.record.field[5].entity.record.field[3].children[0].cdata
        except: pass
        try: kid['birth_date'] =  obj.record.field[5].entity.record.field[5].children[0].cdata
        except: pass

        try: kid['first_name'] = obj.record.field[5].entity.record.field[6].children[0].cdata
        except: pass
        try: kid['prefix'] = obj.record.field[5].entity.record.field[7].children[0].cdata
        except: pass
        try: kid['last_name'] = obj.record.field[5].entity.record.field[8].children[0].cdata
        except: pass


        try: father['uuid'] = obj.record.field[6].entity['uuid']
        except: pass
        try: father['first_name'] = obj.record.field[6].entity.record.field[3].children[0].cdata
        except: pass
        try: father['prefix'] = obj.record.field[6].entity.record.field[5].children[0].cdata
        except: pass
        try: father['last_name'] = obj.record.field[6].entity.record.field[6].children[0].cdata
        except: pass

        try: mother['uuid'] = obj.record.field[7].entity['uuid']
        except: pass
        try: mother['first_name'] = obj.record.field[7].entity.record.field[3].children[0].cdata
        except: pass
        try: mother['prefix'] = obj.record.field[7].entity.record.field[5].children[0].cdata
        except: pass
        try: mother['last_name'] = obj.record.field[7].entity.record.field[6].children[0].cdata
        except: pass

    except:
        print document
        break


    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (`id`, `uuid`, gender, `first_name`, `prefix`, `last_name`, `date_1`, `role`, `register_id`, `register_type`)
            VALUES (%d,"%s","%s", "%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, kid['uuid'], kid['gender'], kid['first_name'].replace('"',"'"), kid['prefix'].replace('"',"'"), kid['last_name'].replace('"',"'"), kid['birth_date'], 1, doc_id, 'birth')
    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender, `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s", "%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, father['uuid'], "male", father['first_name'].replace('"',"'"), father['prefix'].replace('"',"'"), father['last_name'].replace('"',"'"), kid['birth_date'], 5, doc_id, 'birth')
    person_id += 1
    query += """
            INSERT INTO `all_persons_2014` (id, uuid, gender, `first_name`, prefix, `last_name`, date_1, role, `register_id`, `register_type`)
            VALUES (%d,"%s","%s", "%s","%s","%s","%s", %d, %d, "%s");
            """ % (person_id, mother['uuid'], "female", mother['first_name'].replace('"',"'"), mother['prefix'].replace('"',"'"), mother['last_name'].replace('"',"'"), kid['birth_date'], 5, doc_id, 'birth')

    query += """
            INSERT INTO `all_documents_2014` (id, uuid, `type_text`, date, `municipality`, reference_ids)
            VALUES (%d,"%s","%s","%s","%s","%s");
            """ % (doc_id, register['uuid'], 'birth', kid['birth_date'], 'ERR', ','.join([str(person_id-2), str(person_id-1), str(person_id)]))

    if not doc_id % 1000:
        print doc_id

        xml_2_sql.write(query.encode('utf-8').replace('\\',''))
        query = ""

    doc_id += 1
