# evaluation 2

import csv
import numpy as np
import sys


# def get_gold(testFile, arg0, arg1):
# 	triple = arg0 + ' ' + arg1
# 	with open(testFile, 'rb') as csvfile:
# 		f = csv.reader(csvfile, delimiter='\t')
# 		for row in f:
# 			arg0_gold = row[1]
# 			arg1_gold = row[2]
# 			triple_gold = arg0_gold + ' ' + arg1_gold
# 			if triple == triple_gold:
# 				return row[3]
# 	return -1


# make a dictionary where test data triples map to annotations
def getGoldDict(goldDataFile):
	goldDict = {}
	with open(goldDataFile, 'rb') as csvfile:
		fTest = csv.reader(csvfile, delimiter='\t')
		for rowTest in fTest:
			# q_itTest = rowTest[0]
			arg1Test = rowTest[1]
			arg2Test = rowTest[2]
			pair = arg1Test + ' ' + arg2Test 
			
			annGold = rowTest[3]
			annGold = annGold.split(',')

			if triple not in goldDict:
				goldDict[pair] = annGold

			# for i in range(5):
			# 	ann_gold[i] = ann_gold[i].strip().strip('\'').strip('[').strip(']').strip('u\'')
			# 	# print ann_gold[i]
			# 	if ann_gold[i] == 'optional':
			# 		y[i] = -1
			# 	elif 'neg' not in ann_gold[i]:
			# 		y[i] = 1

			# if triple not in goldDict:
			# 	goldDict[triple] = y
	
	lenGoldDict = len(goldDict)
	print "%d Gold Examples Loaded" % lenGoldDict
	return goldDict


def pred_process(pred):
	res = ['has nationality neg', 'was born in neg', 'lived in neg', 'died in neg', 'traveled to neg']
	relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']
	ind = relation.index(pred)
	if ind == 5:
		return res # none of these
	tmp = res[ind].split(' ')
	tmp = tmp[0:len(tmp)-1]
	res[ind] = ' '.join(tmp)
	return res

def evalModel(y_test, goldDict, resFile):
	tp = np.zeros(5)
	fp = np.zeros(5)
	fn = np.zeros(5)

	with open('results', 'rb') as f:
		count = 0
		for row in f: 
			if count == 0:
				count += 1
				continue
			parts = row.split('\t')
			arg0 = parts[0]
			arg1 = parts[1]
			pair = arg1Test + ' ' + arg2Test 

			pred = parts[3]
			pred = pred_process(pred)

			gold = goldDict[pair]
			
			for i in range(5):
				if 'neg' not in gold[i]:
					if 'neg' not in pred[i]:
						tp[i] += 1
					else:
						fn[i] += 1
				elif 'neg' not in pred[i]:
					fp[i] += 1
				elif 'optional' in gold[i]:
					tp[i] += 1

			count += 1

	print tp
	print fp
	print fn

	# p = np.zeros(5)
	# r = np.zeros(5)
	# f1 = np.zeros(5)
	# for i in range(5):
	# 	if tp[i]+fp[i] != 0:
	# 		p[i] = tp[i]*1.0/(tp[i]+fp[i])
	# 	else:
	# 		p[i] = 0
	# 	if tp[i]+fn[i] != 0:
	# 		r[i] = tp[i]*1.0/(tp[i]+fn[i])
	# 	else:
	# 		r[i] = 0
	# 	f1[i] = 2.0/(1/p[i]+1/r[i])
	# print "Precision", p
	# print "Recall", r
	# print "F1", f1

	p = np.divide(tp * 1.0, tp + fp)
	print "Precision:", p
	r = np.divide(tp * 1.0, tp + fn)
	print "Recall:", r
	f1 = np.divide(2*tp, 2*tp + fn + fp)
	print "F1:", f1

	with open(sys.argv[3], 'wb') as f:
		f.write(' '.join(p.astype('|S5')))
		f.write("\n")
		f.write(' '.join(r.astype('|S5')))
		f.write("\n")
		f.write(' '.join(f1.astype('|S5')))

if __name__ == "__main__":
	sys.argv[1]
	evalModel()