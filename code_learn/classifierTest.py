import numpy as np
from collections import OrderedDict
from scipy.sparse import *
from sklearn.linear_model import *
from sklearn.svm import *
from sklearn.ensemble import *
from fileProcessing import *
from bagOrganizer import *
from classifier import *
import subprocess
import os
import sys

# training data: 
# full positive, while negative = 1.6 * positive
# full positive, while negative = 3.0 * positive


# training a binary classifier
# param: X_test, sparse matrix
# param: y_train, sparse matrix
# param: X_train, sparse matrix
def trainAndTestModel_print_weight(X_test, y_train, X_train, allFeatures, testFile, relInd, negPortion):
	# y_train = y_train.toarray()

	relName = ["nationality", "born", "lived", "died", "travel"]
	relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']

	model = LogisticRegression() 
	model.fit(X_train, y_train)
	
	featureWeights = model.coef_[0]
	proba = model.predict_proba(X_test)
	print proba.shape


	with open(testFile) as f:
		ctr = 0
		for row in f:
			parts = row.split('\t')
			partsCopy = list(parts)
			featureWalker = 12
			while featureWalker < len(parts):
				if parts[featureWalker] in allFeatures:
					featureWeight = featureWeights[allFeatures[parts[featureWalker]]]
					partsCopy[featureWalker+1]=str(featureWeight)
				featureWalker+=2
			partsCopy.append(str(proba[ctr][1])+'\n') # add probability to the array
			with open("test_"+sys.argv[1]+"_"+relName[relInd]+'_'+str(negPortion)+'_NA', 'a') as fw:
				fw.write('\t'.join(partsCopy))
			ctr += 1
	print ctr



if __name__ == "__main__":
	direc = "/homes/gws/anglil/learner/"
	sampleTimes = 1
	pruningThres = 3

	# positive and negative training files that include all 5 relations
	fullFile = direc+"data_train_CS/train_CS_MJ_comb_new_feature"
	posFile = direc+"data_train_CS/train_CS_MJ_pos_comb_new_feature"
	negFile = direc+"data_train_CS/train_CS_MJ_neg_comb_new_feature"
	posFileLen = getLen(posFile)
	negFileLen = getLen(negFile)

	# test file
	testFile = direc+"data_test/test_"+sys.argv[1]+"_new_feature_no_grammatic"

	# feature file with which to construct a feature vector
	featureFile = direc+"data_featurized/data_only_CS_and_test"
	fileConcat(fullFile, testFile, featureFile)

	relation = ["nationality", "born", "lived", "died", "travel"]

	# ------------- getting positive and negative training data for each relation ---------
	posRelFiles = []
	negRelFiles = []
	for relationWalker in relation:
		posRelFile = posFile + "_" + relationWalker
		negRelFile = negFile + "_" + relationWalker
		posRelFiles.append(posRelFile)
		negRelFiles.append(negRelFile)
	posRelFilesLen, negRelFilesLen = getPosNegFileRel(fullFile, posRelFiles, negRelFiles)

	# ------------features--------------
	allFeatures = getFeatures(featureFile, pruningThres)

	# ------------- test data and gold labels regarding all relations ----------
	y_gold, X_test = getTestAndGoldData(testFile, allFeatures)

	# ------------- experiment parameters -------------------------
	DS_CS = "CS"
	negPortion = 3.0
	expName = "FWNA"+str(negPortion)

	thresArrayLabel = []

	thresArray = None
	bagOrTriple = None

	if DS_CS == "CS":
		thresArray = [0.96]
		bagOrTriple = "triple"
	lenThresArray = len(thresArray)

	thresArrayLabel += thresArray

	# ------------- experiment -----------------------
	mydir = direc+"exp_"+expName+sys.argv[1]+'0'+'0'+"/"

	if not os.path.exists(mydir):
		os.makedirs(mydir)

	splitFileShared = mydir+"train"
	trainingFileResSuffix = "Res"

	staticTrainingFile = -1
	scalingTrainingFile = mydir+"scalingTrainingFile"

	# ------------ experiment ---------------------
	for relInd in range(5):
		fileConcatPartial(posRelFiles[relInd], 1, negRelFiles[relInd], negPortion*posRelFilesLen[relInd]/negRelFilesLen[relInd], scalingTrainingFile+str(relInd))
		trainingFiles = getSplitData(scalingTrainingFile+str(relInd), thresArray, bagOrTriple, sampleTimes, staticTrainingFile, splitFileShared)
			
		y_train, X_train = getTrainingData_2(trainingFiles[0], relInd, allFeatures)
		trainAndTestModel_print_weight(X_test, y_train, X_train, allFeatures, testFile, relInd, negPortion)
