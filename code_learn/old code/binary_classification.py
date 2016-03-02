import numpy as np
from collections import OrderedDict
from scipy.sparse import *
from sklearn.linear_model import *
from sklearn.svm import *
from sklearn.ensemble import *
# import csv
import sys


# # efficient way to get the number of lines in a file in python
# def file_len(fname):
# 	with open(fname) as f:
# 		for i, l in enumerate(f):
# 			pass
# 	return i + 1


# # make a dictionary where test data triples map to annotations
# def getGoldDict(goldDataFile):
# 	goldDict = {}
# 	with open(goldDataFile, 'rb') as csvfile:
# 		fTest = csv.reader(csvfile, delimiter='\t')
# 		for rowTest in fTest:
# 			q_itTest = rowTest[0]
# 			arg1Test = rowTest[1]
# 			arg2Test = rowTest[2]
# 			# two entities and the question document together define a relation extraction problem
# 			triple = arg1Test + ' ' + arg2Test + ' ' + q_itTest
			
# 			y = np.zeros(5)
# 			ann_gold = rowTest[3]
# 			ann_gold = ann_gold.split(',')
# 			for i in range(5):
# 				ann_gold[i] = ann_gold[i].strip().strip('\'').strip('[').strip(']').strip('u\'')
# 				# print ann_gold[i]
# 				if ann_gold[i] == 'optional':
# 					y[i] = -1
# 				elif 'neg' not in ann_gold[i]:
# 					y[i] = 1

# 			if triple not in goldDict:
# 				goldDict[triple] = y
# 	lenGoldDict = len(goldDict)
# 	print "%d Gold Examples Loaded" % lenGoldDict
# 	return goldDict


# generate feature space
def getFeatures(featureFile):
	allFeatures = OrderedDict()
	with open(featureFile, 'rb') as f:
	# with open('/home/anglil/WebWare6/anglil/TurkData/extraction_with_features/extractions4Relations.sorted', 'rb') as f:
		featureIndex = 0
		for row in f:
			parts = row.split('\t')
			# y = parts[7]
			lenParts = len(parts)
			featureWalker = 12
			while featureWalker < lenParts:
				feature = parts[featureWalker]
				if feature not in allFeatures:
					allFeatures[feature] = featureIndex
					featureIndex += 1
				featureWalker += 2
	lenFeatures = len(allFeatures) # dimension of the feature vector
	print "%d Features Loaded" % lenFeatures
	return allFeatures



# express the test data in the feature space
# allow multiple positive relations in one sentence
# return: y_gold, sparse_matrix
# return: X_test, sparse_matrix
def getTestAndGoldData(testFile, goldDict, allFeatures):
	lenFeatures = len(allFeatures)

	# generate class expression
	# relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']

	# testFeatures = {}
	num = file_len(testFile)

	y_gold = lil_matrix((num, 5), dtype=np.int8)
	X_test = lil_matrix((num, lenFeatures), dtype=np.int8)
	count = 0
	with open(testFile) as f_test:
		for row in f_test:
			parts = row.split('\t')

			# the labels in the test files are junk, so we set to get the gold labels in the csv file by aligning the triples
			arg1 = parts[0]
			arg2 = parts[3]
			d_id = parts[6]
			triple = arg1 + ' ' + arg2 + ' ' + d_id
			y_gold_row = goldDict[triple]
			for i in range(5):
				y_gold[count, i] = y_gold_row[i]

			lenParts = len(parts)
			featureWalker = 12
			while featureWalker < lenParts:
				feature = parts[featureWalker]
				# if feature not in testFeatures:
				# 	testFeatures[feature] = 1
				
				X_test[count, allFeatures[feature]] = 1
				featureWalker += 2

			count += 1
	print "Test Data Ready"
	# lenTestFeatures = len(testFeatures)
	# print "%d features in the test data" % lenTestFeatures
	return y_gold, X_test




# express the training data in the feature space
# return: y_train, sparse matrix
# return: X_train, sparse matrix
def getTrainingData(trainingFile, allFeatures):
	lenFeatures = len(allFeatures)

	# generate class expression
	relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']

	num = file_len(trainingFile)
	
	y_train = lil_matrix((num, 5), dtype=np.int8)
	X_train = lil_matrix((num, lenFeatures), dtype=np.int8)
	count = 0
	with open(trainingFile) as f_train:
		for row in f_train:
			parts = row.split('\t')

			rel = parts[7] # labels in the training data
			if rel != 'NA':
				relInd = relation.index(rel)
				y_train[count, relInd] = 1

			lenParts = len(parts)
			featureWalker = 12
			while featureWalker < lenParts:
				feature = parts[featureWalker]
				X_train[count, allFeatures[feature]] = 1
				featureWalker += 2

			count += 1
			# print count
	print "Training Data Ready"
	return y_train, X_train


# training a binary classifier
# param: X_test, sparse matrix
# param: y_train, sparse matrix
# param: X_train, sparse matrix
def trainAndTestModel(X_test, y_train, X_train, classifier):
	y_test = np.zeros([X_test.shape[0], 5])
	y_train = y_train.toarray()

	for i in range(5):
		if classifier == "LR":
			model = LogisticRegression() 
			model.fit(X_train, y_train[:,i])
			y_test[:,i] = model.predict(X_test)
		elif classifier == "perceptron":
			model = Perceptron()
			model.fit(X_train, y_train[:,i])
			y_test[:,i] = model.predict(X_test)

		# model = SVC()
		# model.fit(X_train, np.char.mod('%d', y_train[:,RELATION_INDEX]))
		# y_test = model.predict(X_test)

		# model = RandomForestClassifier()
		# model.fit(X_train.toarray(), y_train[:,RELATION_INDEX])
		# y_test = model.predict(X_test.toarray())
	print "Training And Test Done"
	return y_test


# evaluate
def evalModel(y_test, y_gold, resName):
	y_gold = y_gold.toarray()
	yLen = len(y_test)

	tp = np.zeros(5)
	fp = np.zeros(5)
	fn = np.zeros(5)
	
	for i in range(yLen):
		for j in range(5):
			if y_gold[i][j] == 1:
				if y_test[i][j] == 1:
					tp[j] += 1
				else:
					fn[j] += 1
			elif y_gold[i][j] == 0:
				if y_test[i][j] == 1:
					fp[j] += 1
			# if not counting "optional", comment the following condition out
			# in the current definition, optional == -1
			else:
				tp[j] += 1

	print tp
	print fp
	print fn

	p = np.divide(tp * 1.0, tp + fp)
	print "Precision:", p
	r = np.divide(tp * 1.0, tp + fn)
	print "Recall:", r
	f1 = np.divide(2*tp, 2*tp + fn + fp)
	print "F1:", f1

	with open(resName, 'wb') as f:
		f.write(' '.join(p.astype('|S5')))
		f.write("\n")
		f.write(' '.join(r.astype('|S5')))
		f.write("\n")
		f.write(' '.join(f1.astype('|S5')))



if __name__ == "__main__":
	
	# training data
	trainingFile = sys.argv[1]
	# training data with the full CS set 
	trainingFileFullCS = sys.argv[2]
	# test data
	testFile = sys.argv[3] # test_mj_multiPositive.csv
	# test features
	testFileTriple = sys.argv[4] # test_CS
	# result data
	resFile = sys.argv[5]
	# result data with the full CS set, used for 
	resFileFullCS = sys.argv[6]
	# classifier
	classifier = sys.argv[7]
	# DS or CS
	target = sys.argv[8]

	if classifier not in ["LR", "perceptron"]:
		raise NameError("Not a supported classifier!")
	if target not in ["DS", "CS"]:
		raise NameError("The data target must either be 'DS' or 'CS'!")


	# get the file that contains all the features
	featureFile = getAllData(trainingFile, testFile)
	# get features
	allFeatures = getFeatures(featureFile)
	# get gold dictionary
	goldDict = getGoldDict(testFile) # test_mj_multiPositive.csv
	# get gold and test data
	y_gold, X_test = getTestAndGoldData(testFileTriple, goldDict, allFeatures)

	splitNum = 5
	if target == "CS":
		splitNum = 9

	for i in range(splitNum):
		for j in range(10):
			# get training data
			y_train, X_train = getTrainingData(trainingFile+str(i)+str(j), allFeatures)
			# train and test model
			y_test = trainAndTestModel(X_test, y_train, X_train)
			# evaluation
			evalModel(y_test, y_gold, resFile+str(i)+str(j))

	# to make the comparison complete
	y_train, X_train = getTrainingData(trainingFileFullCS, allFeatures)
	y_test = trainAndTestModel(X_test, y_train, X_train)
	evalModel(y_test, y_gold, resFileFullCS)

