import numpy as np
import re
import copy

relation = ['has nationality', 'was born in', 'lived in', 'died in', 'traveled to']


# loop over all the CS data from which test data is drawn
# key: arg1, arg2, sent
# value: std row
tripleDict = {}
with open("../data_train_pre_CS/CS_2nd_batch") as f:
	 for row in f:
	 	parts = row.split('\t')
	 	arg1 = parts[0]
	 	arg2 = parts[3]
	 	sent = parts[11]

	 	triple = arg1+' '+arg2+' '+sent

	 	tripleDict[triple] = row

# get std test data from unregularized test data, strict
# key: arg1, arg2, sent
# value: std row
tripleDictTestStrict = {}
with open("../data_test_unregularized/strict-answerkey.txt") as f:
	f.readline()
	count = 0
	for row in f:
		parts = row.split('\t')
		arg1 = parts[0]
		arg2 = parts[1]
		sentBrackets = parts[2]
		sentBrackets = re.sub('{{ ', '', sentBrackets)
		sentBrackets = re.sub('}} ', '', sentBrackets)
		annGold = np.array(parts[3:8], dtype='|S4')
		annGold = annGold.astype(np.int)

		a = []
		for i in range(5):
			if annGold[i] == 1:
				a.append(relation[i])
			else:
				a.append(relation[i]+ ' neg')
		a = ','.join(a)


		triple = arg1+' '+arg2+' '+sentBrackets.strip("\"")

		# only allow for a triple to occur once in the test set
		tripleDictTestStrict[triple] = a
		count += 1
print count
print len(tripleDictTestStrict)

# get std test data from unregularized test data, relaxed
# key: arg1, arg2, sent
# value: std row
tripleDictTestRelaxed = {}
with open("../data_test_unregularized/relaxed-answerkey.txt") as f:
	f.readline()
	count = 0
	for row in f:
		parts = row.split('\t')
		arg1 = parts[0]
		arg2 = parts[1]
		sentBrackets = parts[2]
		sentBrackets = re.sub('{{ ', '', sentBrackets)
		sentBrackets = re.sub('}} ', '', sentBrackets)
		annGold = np.array(parts[3:8], dtype='|S4')
		annGold = annGold.astype(np.int)

		a = []
		for i in range(5):
			if annGold[i] == 1:
				a.append(relation[i])
			else:
				a.append(relation[i]+ ' neg')
		a = ','.join(a)


		triple = arg1+' '+arg2+' '+sentBrackets.strip("\"")

		# only allow for a triple to occur once in the test set
		tripleDictTestRelaxed[triple] = a
		count += 1
print count
print len(tripleDictTestRelaxed)




# write test and CS training files
count = 0
tripleDict1 = copy.deepcopy(tripleDict)
with open('../data_test/test_strict', 'wb') as fw1:
	for triple in tripleDictTestStrict:
		if triple in tripleDict1:
			row = tripleDict1[triple] # std row
			row = row.split('\t')
			row[7] = tripleDictTestStrict[triple]

			fw1.write('\t'.join(row))


			count += 1
			
print count


# write test and CS training files
count = 0
tripleDict2 = copy.deepcopy(tripleDict)
with open('../data_test/test_relaxed', 'wb') as fw2:
	for triple in tripleDictTestRelaxed:
		if triple in tripleDict2:
			row = tripleDict2[triple] # std row
			row = row.split('\t')
			row[7] = tripleDictTestRelaxed[triple]

			fw2.write('\t'.join(row))

			count += 1
			
print count





