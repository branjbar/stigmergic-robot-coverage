"""
This file is used for getting a quick statistic about how good the content-based measure is. 
"""
from modules.basic_modules import basic
import time

import csv
csv_writer_1 = csv.writer(open("MYFILE.csv", "wb"))
csv_writer_2 = csv.writer(open("scores.csv", "wb"))

t = time.time()

query = "Select first_name, last_name, block_key from all_persons_2014 limit 10000000"

cur = basic.run_query(query)

count = 0

name_dict = {}
for c in cur:
   
    if name_dict.get(c[2]):
        #if not "%s %s" % (c[0], c[1]) in name_dict[c[2]]:
        name_dict[c[2]].append("%s %s" % (c[0], c[1]))
    else:
        name_dict[c[2]] = [c[0] + ' ' + c[1]]

for key in name_dict.keys():
    # print name_dict[key]
    if name_dict[key] and len(name_dict[key]) > 1 and len(name_dict[key]) <= 100:
        for i1, name1 in enumerate(name_dict[key]):
            for i2, name2 in enumerate(name_dict[key]):
                # print name1, name2
                if i2 > i1:
                    score = basic.string_compare(name1, name2)
                    
                    #print key, name1, name2, score
                    csv_writer_1.writerow([name1, name2, score])
                    csv_writer_2.writerow([score])

print time.time() - t, count
