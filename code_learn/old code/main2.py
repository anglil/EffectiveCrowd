
import os
import numpy as np
from fileProcessing import *
from bagOrganizer import *
from classifier import *
from evaluation import *

if __name__ == "__main__":

	direc = "/homes/gws/anglil/learner/"
	sampleTimes = 3
	pruningThres = 3
	featureFile = direc+"data_featurized/data"
	testFile = direc+"data_test/test_relaxed"
	relation = ["nationality", "born", "lived", "died", "travel"]

	


	

	# ------------features--------------
	allFeatures = getFeatures(featureFile, pruningThres)

	# ------------prepare the test data---------
	y_gold, X_test = getTestAndGoldData(testFile, allFeatures)



	
	# ------------getting training file size------------
	posLenRel = np.zeros(5)
	negLenRel = np.zeros(5)
	for i in range(5):
		posLenRel[i] = getLen(direc+"data_train_CS/train_CS_"+relation[i]+"_pos_comb")
		negLenRel[i] = getLen(direc+"data_train_CS/train_CS_"+relation[i]+"_neg_comb")
	posLenRelMJ = getLen(direc+"data_train_CS/train_CS_MJ_pos_comb")
	negLenRelMJ = getLen(direc+"data_train_CS/train_CS_MJ_neg_comb")

	# ------------variables------------------

	# mydir = direc+sys.argv[1] # exp?
	# classifier = sys.argv[2] # LR, perceptron, multir, multirBinary
	# negPortion = sys.argv[3] # 0, 0.1, 0.2, 0.4, 0.8
	DS_CS = "CS" # CS, DS
	classifiers = ["multir", "multirBinary"]#["LR", "perceptron", 
	negPortions =  [0.0, 0.4, 0.8, 1.2, 1.6, 2.4, 3.0, 4.0]
	for ii in range(2):
		for jj in range(8):
			mydir = direc+"exprelaxed"+str(ii+2)+str(jj)+"/"
			classifier = classifiers[ii]
			negPortion = negPortions[jj]


			# ------------ fixed --------------------
			if not os.path.exists(mydir):
				os.makedirs(mydir)

			headFile = mydir+"head"
			splitFileShared = mydir+"train"
			tailFile = mydir+"tail"
			
			headFileRes = mydir+"headRes"
			trainingFileResSuffix = "Res"
			tailFileRes = mydir+"tailRes"

			plotNameShared = mydir+"plot"

			staticTrainingFile = mydir+"staticTrainingFile"
			scalingTrainingFile = mydir+"scalingTrainingFile"


			thresArray = None
			bagOrTriple = None
			thresArrayLabel = []
			if DS_CS == "CS":
				thresArray = [0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 0.96] 
				bagOrTriple = "triple"
			elif DS_CS == "DS":
				thresArray = [0.01, 0.04, 0.16, 0.64]
				bagOrTriple = "bag"
				thresArrayLabel.append(0.0)
			lenThresArray = len(thresArray)

			headSplit = None
			tailSplit = None
			headProportion = None
			tailProportion = None
			thresArrayLabel+=thresArray
			if DS_CS == "CS":
				headProportion = 0
				tailProportion = 0#1.0
				headSplit = "triple"
				tailSplit = "triple"
				# thresArrayLabel+=[1.0]
			if DS_CS == "DS":
				headProportion = 1
				tailProportion = 0.64
				headSplit = "triple"
				tailSplit = "bag"
				# thresArrayLabel+=[0.64]
			thresArrayLabel+=[tailProportion]

			xlabel = [str(x) for x in thresArrayLabel]
			
			posFile = direc+"data_train_CS/train_CS_MJ_pos_comb"
			negFile = direc+"data_train_CS/train_CS_MJ_neg_comb"

			staticTrainingFile = -1#direc+"data_train_CS/train_CS_MJ"
			fileConcatPartial(posFile, 1, negFile, negPortion*posLenRelMJ/negLenRelMJ, scalingTrainingFile)
			headFile = getPartialFile(staticTrainingFile, headSplit, headProportion, headFile)
			tailFile = getPartialFile(scalingTrainingFile, tailSplit, tailProportion, tailFile)


			# ------------experiment------------
			if classifier in ["LR", "perceptron"]:
				# ------------split the training data--------------
				trainingFiles = getSplitData(scalingTrainingFile, thresArray, bagOrTriple, sampleTimes, staticTrainingFile, splitFileShared)

				# ------------train and test--------------
				if headFile != -1:
					y_train, X_train = getTrainingData(headFile, allFeatures)
					y_test = trainAndTestModel(X_test, y_train, X_train, classifier)
					evalModel(y_test, y_gold, headFileRes)

				for trainingFile in trainingFiles:
					print "training size:", getLen(trainingFile)
					y_train, X_train = getTrainingData(trainingFile, allFeatures)
					y_test = trainAndTestModel(X_test, y_train, X_train, classifier)
					evalModel(y_test, y_gold, trainingFile+trainingFileResSuffix)

				if tailFile != -1:
					y_train, X_train = getTrainingData(tailFile, allFeatures)
					y_test = trainAndTestModel(X_test, y_train, X_train, classifier)
					evalModel(y_test, y_gold, tailFileRes)

			elif classifier == "multir":
				# ------------split the training data--------------
				trainingFiles = getSplitData(scalingTrainingFile, thresArray, bagOrTriple, sampleTimes, staticTrainingFile, splitFileShared)

				# ------------train and test--------------
				if headFile != -1:
					trainAndTestModelMultiR(headFile, testFile, headFileRes)

				for trainingFile in trainingFiles:
					print "training size:", getLen(trainingFile)
					trainAndTestModelMultiR(trainingFile, testFile, trainingFile+trainingFileResSuffix)

				if tailFile != -1:
					trainAndTestModelMultiR(tailFile, testFile, tailFileRes)

			elif classifier == "multirBinary":
				# ------------split the training data--------------
				trainingFiles = getSplitData(scalingTrainingFile, thresArray, bagOrTriple, sampleTimes, staticTrainingFile, splitFileShared)

				# ------------train and test--------------
				if headFile != -1:
					trainAndTestModelMultiRBinary(headFile, testFile, headFileRes)

				for trainingFile in trainingFiles:
					print "training size:", getLen(trainingFile)
					trainAndTestModelMultiRBinary(trainingFile, testFile, trainingFile+trainingFileResSuffix)

				if tailFile != -1:
					trainAndTestModelMultiRBinary(tailFile, testFile, tailFileRes)

			# ------------evaluation--------------
			PRF1Array = []
			

			if headFile != -1:
				resFiles = []
				for sample in range(3):
					resFiles.append(headFileRes)
				PRF1 = learningDot(resFiles)
				PRF1Array.append(PRF1)
				
				

			for dot in range(lenThresArray):
				resFiles = []
				for sample in range(sampleTimes):
					resFiles.append(splitFileShared+str(dot)+str(sample)+trainingFileResSuffix)
				PRF1 = learningDot(resFiles)
				PRF1Array.append(PRF1)
				


			if tailFile != -1:
				resFiles = []
				for sample in range(3):
					resFiles.append(tailFileRes)
				PRF1 = learningDot(resFiles)
				PRF1Array.append(PRF1)
			
			relRes = learningCurve(PRF1Array, xlabel, plotNameShared, -1)

