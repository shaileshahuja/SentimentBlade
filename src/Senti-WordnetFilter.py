__author__ = 'shailesh'

import csv
filename = "/home/shailesh/webservice/src/classifier_v3.0/SentiWordNet_Lexicon.csv"
lexicon = dict()
total = 0
actual = 0
with open(filename,'r') as file:
    while True:
        data = file.readline()
        if data == "" or data is None:
            break
        if data.startswith("#"):
            continue
        parts = data[:-1].split(',')
        actual += 1
        if parts[0] != 'a':
            continue
        lexicon[parts[1]] = parts[2]
        total += 1


#filename = "/home/shailesh/webservice/src/classifier_v3.0/SentiWordNet_Lexicon.csv"
#file = open(filename,'wb')
#wr = csv.writer(file)
#for data in lexicon:
#    row = [data[0],data[1],lexicon[(data[0],data[1])]]
#    wr.writerow(row)
#file.close()

filename = "/home/shailesh/webservice/src/classifier_v3.0/SentiWordNet_Lexicon_concise.csv"
file = open(filename, 'wb')
wr = csv.writer(file)
for key, value in sorted(lexicon.items()):
    row = [key, value]
    wr.writerow(row)
file.close()



print "Total", total, "Actual", actual