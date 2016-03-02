import numpy as np
from collections import OrderedDict
from scipy.sparse import *
from sklearn.linear_model import *
from sklearn.svm import *
from sklearn.ensemble import *
from fileProcessing import *
import subprocess
import os
import math

# get every feature with its counts and do feature pruning
# pruningThres: features that occur less than pruningThres will be pruned
def getFeatures(stdFile, pruningThres):
	allFeatures = OrderedDict()
	featureCount = 0

	# load all the features
	with open(stdFile) as f:
		for row in f:
			parts = row.split('\t')
			lenParts = len(parts)
			featureWalker = 12
			while featureWalker < lenParts:
				feature = parts[featureWalker]
				if feature not in allFeatures:
					featureCount += 1
					allFeatures[feature] = 1
				else:
					allFeatures[feature] += 1
				featureWalker += 2

	# feature pruning
	if pruningThres > 0:
		for key in allFeatures:
			if allFeatures[key] < pruningThres:
				del allFeatures[key]

	# use the value as index to have O(1) time
	featureIndex = 0
	for key in allFeatures:
		allFeatures[key] = featureIndex
		featureIndex += 1

	print len(allFeatures), "features loaded"
	return allFeatures



# express the test data in the feature space
# allow multiple positive relations in one sentence
# return: y_gold, sparse_matrix
# return: X_test, sparse_matrix
def getTestAndGoldData(testFile, allFeatures):
	lenFeatures = len(allFeatures)

	# generate class expression
	# relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']

	# testFeatures = {}
	num = getLen(testFile)

	y_gold = lil_matrix((num, 5), dtype=np.int8)
	X_test = lil_matrix((num, lenFeatures), dtype=np.int8)

	count = 0
	with open(testFile) as f_test:
		for row in f_test:
			parts = row.split('\t')

			# arg1 = parts[0]
			# arg2 = parts[3]
			# d_id = parts[6]
			# triple = arg1 + ' ' + arg2 + ' ' + d_id

			# process the gold annotation item
			y_gold_row = parts[7]
			y_gold_row = y_gold_row.split(',')
			for i in range(5):
				y_gold_row[i] = y_gold_row[i].strip().strip('\'').strip('[').strip(']').strip('u\'')
				if y_gold_row[i] == 'optional':
					y_gold[count, i] = -1
				elif 'neg' not in y_gold_row[i]:
					y_gold[count, i] = 1

			# process the feature vector
			lenParts = len(parts)
			featureWalker = 12
			while featureWalker < lenParts:
				feature = parts[featureWalker]
				if feature in allFeatures:
					X_test[count, allFeatures[feature]] = 1
				featureWalker += 2

			count += 1

	print "Test Data Ready"
	# lenTestFeatures = len(testFeatures)
	# print "%d features in the test data" % lenTestFeatures
	return y_gold, X_test





# relation-wise training data collection
def getTrainingData_2(trainingFile, relInd, allFeatures):
	num = getLen(trainingFile)
	lenFeatures = len(allFeatures)

	# generate class expression
	relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']

	y_train = np.zeros(num, dtype=np.int8)
	X_train = lil_matrix((num, lenFeatures), dtype=np.int8)

	ctr = 0
	with open(trainingFile) as f:
		for row in f:
			parts= row.split('\t')

			# the training file is already binary
			rel = parts[7]
			if rel == relation[relInd]:
				y_train[ctr] = 1

			lenParts = len(parts)
			featureWalker = 12
			while featureWalker < lenParts:
				feature = parts[featureWalker]
				# since the features could be pruned, we need to make sure features that belong to this instance exist in the feature vector
				if feature in allFeatures:
					X_train[ctr, allFeatures[feature]] = 1
				featureWalker += 2
			ctr += 1

	print "Training Data Ready"
	return y_train, X_train


# training a binary classifier
# param: X_test, lil sparse matrix
# param: y_train, numpy array
# param: X_train, lil sparse matrix
def trainAndTestModel_2(X_test, y_train, X_train, classifier):
	# y_train = y_train.toarray()

	if classifier == "LR":
		model = LogisticRegression()
	elif classifier == "perceptron":
		model = Perceptron()
	model.fit(X_train, y_train)
	y_test = model.predict(X_test)

	print "Training And Test Done"
	return y_test


# param: y_test, numpy array
# param: y_gold, lil sparse matrix
def evalModel_2(y_test, y_gold, relInd):
	y_gold = y_gold.toarray()
	yLen = len(y_test)

	tp = 0
	fp = 0
	fn = 0

	for i in range(yLen):
		if y_gold[i][relInd] == 1:
			if y_test[i] == 1:
				tp += 1
			else:
				fn += 1
		elif y_gold[i][relInd] == 0:
			if y_test[i] == 1:
				fp += 1
		else:
			tp += 1

	print tp
	print fp
	print fn

	p = np.divide(tp * 1.0, tp + fp)
	if math.isnan(p):
		p = 0
	print "Precision:", p
	r = np.divide(tp * 1.0, tp + fn)
	if math.isnan(r):
		r = 0
	print "Recall:", r
	f1 = np.divide(2.0*tp, 2*tp + fn + fp)
	if math.isnan(f1):
		f1 = 0
	print "F1:", f1

	return p, r, f1


def trainAndTestModelMultiRBinary_2(trainingFile, testFile, relInd, resNameShared):
	relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']

	subprocess.call(["sh", "multirTraining.sh", trainingFile, testFile, resNameShared])

	tp = 0
	fp = 0
	fn = 0

	with open(testFile) as f_gold, open(resNameShared) as f_test:
		allGold = f_gold.read().split('\n')
		allTest = f_test.read().split('\n')
		for item in range(len(allGold)-1):
			relGold = allGold[item].split('\t')[7] # hand-labels
			relTest = allTest[item].split('\t')[3] # prediction

			# formalize gold answers
			y_gold = 0
			y_gold_row = relGold.split(',')[relInd].strip('\'').strip('[').strip(']').strip('u\'')
			if y_gold_row == 'optional':
				y_gold = -1
			elif 'neg' not in y_gold_row:
				y_gold = 1

			# formalize prediction answers
			y_test = 0
			if relTest == relation[relInd]:
				y_test = 1

			# compute p, r, f1
			if y_gold == 1:
				if y_test == 1:
					tp += 1
				else:
					fn += 1
			elif y_gold == 0:
				if y_test == 1:
					fp += 1
			else:
				tp += 1

	print tp 
	print fp
	print fn

	p = np.divide(tp * 1.0, tp + fp)
	if math.isnan(p):
		p = 0
	print "Precision:", p
	r = np.divide(tp * 1.0, tp + fn)
	if math.isnan(r):
		r = 0
	print "Recall:", r
	f1 = np.divide(2.0*tp, 2*tp + fn + fp)
	if math.isnan(f1):
		f1 = 0
	print "F1:", f1

	return p, r, f1


# train, test and evaluate with MultiR
def trainAndTestModelMultiR(trainingFile, testFile, resName):
	relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']

	subprocess.call(["sh", "multir.sh", trainingFile, testFile, resName])

	# compare results with testFile
	tp = np.zeros(5)
	fp = np.zeros(5)
	fn = np.zeros(5)

	with open(testFile) as fTest, open(resName) as fRes:
		allTest = fTest.read().split('\n')
		allRes = fRes.read().split('\n')
		# the last symbol is just a '' because of the split
		for item in range(len(allTest)-1):
			relTest = allTest[item].split('\t')[7] # annotations on each relation
			relRes = allRes[item].split('\t')[3] # only prediction 
			
			# formalize gold answers
			y_gold = np.zeros(5)
			y_gold_row = relTest.split(',')
			for i in range(5):
				y_gold_row[i] = y_gold_row[i].strip().strip('\'').strip('[').strip(']').strip('u\'')
				if y_gold_row[i] == 'optional':
					y_gold[i] = -1
				elif 'neg' not in y_gold_row[i]:
					y_gold[i] = 1

			# formalize prediction answers
			y_test = np.zeros(5)
			if relRes != 'NA':
				relInd = relation.index(relRes)
				y_test[relInd] = 1

			# compute p, r, f1
			for j in range(5):
				if y_gold[j] == 1:
					if y_test[j] == 1:
						tp[j] += 1

					else:
						fn[j] += 1
				elif y_gold[j] == 0:
					if y_test[j] == 1:
						fp[j] += 1
				# if not counting "optional", comment the following condition out
				# in the current definition, optional == -1
				else:
					tp[j] += 1

	print tp
	print fp
	print fn

	p = np.divide(tp * 1.0, tp + fp)
	for pi in range(len(p)):
		if math.isnan(p[pi]):
			p[pi] = 0
	print "Precision:", p
	r = np.divide(tp * 1.0, tp + fn)
	for ri in range(len(r)):
		if math.isnan(r[ri]):
			r[ri] = 0
	print "Recall:", r
	f1 = np.divide(2.0*tp, 2*tp + fn + fp)
	for f1i in range(len(f1)):
		if math.isnan(f1[f1i]):
			f1[f1i] = 0
	print "F1:", f1

	with open(resName, 'wb') as f:
		f.write(' '.join(p.astype('|S5')))
		f.write("\n")
		f.write(' '.join(r.astype('|S5')))
		f.write("\n")
		f.write(' '.join(f1.astype('|S5')))


def trainAndTestModelMIML(trainingFile, testFile, resName):
	subprocess.call(["sh", "mimlre.sh", trainingFile, testFile, resName])
