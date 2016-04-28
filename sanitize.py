import requests
import csv
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

relationships = {}
final = []

csv_read = csv.reader(open('edges.csv'))

def sanitize(string):
    return string.lower().replace(" ", "").replace("'", "").replace("$", "s").replace(".", "")

for row in csv_read:
    combined1 = sanitize(row[0]) + sanitize(row[1])
    combined2 = sanitize(row[1]) + sanitize(row[0])
    if combined1 in relationships or combined2 in relationships:
        if combined1 in relationships:
            relationships[combined1]['Value'] = relationships[combined1]['Value'] + 1
        else:
            relationships[combined2]['Value'] = relationships[combined2]['Value'] + 1
    else:
        relationships[combined1] = {'Source': row[0], 'Target': row[1], 'Value': 1, 'Type': 'Undirected'}

for key in relationships:
    final.append(relationships[key])

csv_keys = final[0].keys()

with open('edges_final.csv', 'wb') as output_file:
    writer = csv.DictWriter(output_file, csv_keys)
    writer.writeheader()
    writer.writerows(final)
