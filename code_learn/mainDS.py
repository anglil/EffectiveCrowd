import os
import sys
import numpy as numpy
from fileProcessing import *
from bagOrganizer import *
from classifier import *
from evaluation import *

# ===== interface =====
# -- expName
# -- DSFile (don't change)
# -- posCSFile (relation-wise CS files are also supposed to exist under name conventions)
# -- negCSFile (relation-wise CS files are also supposed to exist under name conventions)
# -- optProportion (available only after running CS version)
# -- optProportions (available only after running CS version)
# -- testFile (don't change)
# -- featureFile, featureFilePartial
# -- posFile (don't change)
# -- negFile (don't change)



if __name__ == "__main__":
	expName = "mimlDSCSour"#"mimlDSCSMJ"#"gaborDSCSoriginal"#gaborDSCS2strict#lost the original DS plus CS exp name
	direc ="/homes/gws/anglil/learner/"
	sampleTimes = 3
	pruningThres = 2

	# training data
	DSFile = direc+"data_train_DS/train_DS_new_feature"#"data_train_DS/train_DS_sorted2_new_feature"
	
	# get optimal CS training files
	# No. 1
	# "data_train_CS/train_CS_MJ_pos_comb_new_feature"
	# "data_train_CS/train_CS_MJ_neg_comb_new_feature"
	# No. 2
	# "data_train_CS/gabor_CS_original_new_feature_shuffled_pos"
	# "data_train_CS/gabor_CS_original_new_feature_shuffled_neg"
	# No. 3
	# "data_train_CS/gabor_CS_MJ_new_feature_shuffled_pos"
	# "data_train_CS/gabor_CS_MJ_new_feature_shuffled_neg"
	posCSFile = direc+"data_train_CS/train_CS_MJ_pos_comb_new_feature"
	negCSFile = direc+"data_train_CS/train_CS_MJ_neg_comb_new_feature"
	optProportion = 0
	optProportions = [0, 0, 0, 0, 0]#[1, 5, 0.5, 2, 1]
	optResFile, optResFileRel = getOptimalCSTraining(posCSFile, negCSFile, optProportion, optProportions) 

	# test file
	testFile = direc+"data_test/test_"+sys.argv[1]+"_new_feature_no_grammatic"

	# ---------- feature file with which to construct a feature vector -----------
	# No. 1 
	# "data_featurized/data_DS_CS_and_test"
	# No. 2
	# "data_featurized/gaborpartial_DS_CS_and_test"
	# No. 3
	# "data_featurized/gabor_DS_and_test"
	featureFile = direc+"data_featurized/data_DS_CS_and_test"
	# No. 1 
	# "data_featurized/data_CS_and_test"
	# No. 2
	# "data_featurized/gabororiginal_CS_and_test"
	# No. 3
	# "data_featurized/gabor_CS_and_test"
	featureFilePartial = direc+"data_featurized/data_CS_and_test"
	#if not os.path.exists(featureFile):
	fileConcat(DSFile, featureFilePartial, featureFile)

	allFeatures = getFeatures(featureFile, pruningThres)

	

	# -------------- relation alias ------------------------
	relation = ["nationality", "born", "lived", "died", "travel"]

	# -------------- getting positive and negative training data for each relation -----------
	posFile = direc+"data_train_DS/train_DS_pos_new_feature"
	negFile = direc+"data_train_DS/train_DS_neg_new_feature"

	posRelFiles = []
	negRelFiles = []
	for relationWalker in relation:
		posRelFile = posFile + "_" + relationWalker # relation-wise positive data naming convention 
		negRelFile = negFile + "_" + relationWalker # relation-wise negative data naming convention 
		posRelFiles.append(posRelFile)
		negRelFiles.append(negRelFile)

	posFileLen, negFileLen, posRelFilesLen, negRelFilesLen = getPosNegFileRel(DSFile, posFile, negFile, posRelFiles, negRelFiles)

	# ------------- test data and gold labels regarding all relations ----------
	y_gold, X_test = getTestAndGoldData(testFile, allFeatures)

	# ------------ experiment parameters ------------------
	DS_CS = "DS"
	classifiers = ["mimlre"]
	negPortions = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0]
	

	# -------------- global variables that depend on the experiment parameters ----------
	thresArrayLabel = []
	thresArray = [0.96]#[0.01, 0.04, 0.16, 0.64]
	lenThresArray = len(thresArray)
	thresArrayLabel += thresArray
	xlabel = [str(x) for x in thresArrayLabel]

	# ------------ loop over classifier types and negative portion numbers ------------ 
	for classifierInd in range(len(classifiers)):
		for negPortionInd in range(len(negPortions)):
			mydir = direc+"exp_"+expName+sys.argv[1]+"/"+sys.argv[1]+str(classifierInd)+str(negPortionInd)+"/"

			classifier = classifiers[classifierInd]
			negPortion = negPortions[negPortionInd]

			# -------------- fixed ----------------------
			if not os.path.exists(mydir):
				os.makedirs(mydir)

			splitFileShared = mydir+"train"
			trainingFileResSuffix = "Res"
			plotNameShared = mydir + "plot"
			scalingTrainingFile = mydir+"scalingTrainingFile"

			# ------------- experiment ------------------
			if classifier in ["LR", "perceptron"]:
				p = [[],[],[],[],[]]
				r = [[],[],[],[],[]]
				f1 = [[],[],[],[],[]]
				trainingFiles = None

				for relInd in range(5):
					# the file that's attached to the scaling file
					# -1: not to attach anything
					# optResFileRel[relInd]: attach the optimal CS data
					staticTrainingFile = optResFileRel[relInd]
					# combine pos and neg data
					fileConcatPartial(posRelFiles[relInd], 1, "triple", negRelFiles[relInd], negPortion*posRelFilesLen[relInd]/negRelFilesLen[relInd], "triple", scalingTrainingFile+str(relInd))
					# combine static and scaling data, going through thresholds and samplings
					trainingFiles = getSplitData(scalingTrainingFile+str(relInd), thresArray, "triple", sampleTimes, staticTrainingFile, splitFileShared)

					for trainingFile in trainingFiles:
						# sklearn classifiers do not allow the number of classes to be one, so add one negative example here
						addOneNeg(trainingFile, negRelFiles[relInd])
						addOneNeg(trainingFile, posRelFiles[relInd])
						print "training size:", getLen(trainingFile)
						y_train, X_train = getTrainingData_2(trainingFile, relInd, allFeatures)
						y_test = trainAndTestModel_2(X_test, y_train, X_train, classifier)
						p0, r0, f10 = evalModel_2(y_test, y_gold ,relInd)
						p[relInd].append(p0)
						r[relInd].append(r0)
						f1[relInd].append(f10)

				for i in range(len(trainingFiles)):
					p1 = np.array([p[0][i], p[1][i], p[2][i], p[3][i], p[4][i]])
					r1 = np.array([r[0][i], r[1][i], r[2][i], r[3][i], r[4][i]])
					f11 = np.array([f1[0][i], f1[1][i], f1[2][i], f1[3][i], f1[4][i]])
					with open(trainingFiles[i]+trainingFileResSuffix, 'wb') as f:
						f.write(' '.join(p1.astype('|S5')))
						f.write("\n")
						f.write(' '.join(r1.astype('|S5')))
						f.write("\n")
						f.write(' '.join(f11.astype('|S5')))

			elif classifier == "multir":
				# the file that's attached to the scaling file
				# -1: not to attach anything
				# optResFile: attach the optimal CS data
				staticTrainingFile = optResFile
				# combine pos and neg data
				fileConcatPartial(posFile, 1, "bag", negFile, negPortion*posFileLen/negFileLen, "bag", scalingTrainingFile)
				# combine static and scaling data, going through thresholds and samplings
				trainingFiles = getSplitData(scalingTrainingFile, thresArray, "bag", sampleTimes, staticTrainingFile, splitFileShared)

				for trainingFile in trainingFiles:
					print "training size:", getLen(trainingFile)
					trainAndTestModelMultiR(trainingFile, testFile, trainingFile+trainingFileResSuffix)

			elif classifier == "mimlre":
				staticTrainingFile = optResFile
				fileConcatPartial(posFile, 1, "bag", negFile, negPortion*posFileLen/negFileLen, "bag", scalingTrainingFile)
				trainingFiles = getSplitData(scalingTrainingFile, thresArray, "bag", sampleTimes, staticTrainingFile, splitFileShared)
				for trainingFile in trainingFiles:
					print "training size:", getLen(trainingFile)
					trainAndTestModelMIML(trainingFile, testFile+"_miml", trainingFile+trainingFileResSuffix)


			# ----------------------- evaluation ------------------------
			PRF1Array = []

			for dot in range(lenThresArray):
				resFiles = []
				for sample in range(sampleTimes):
					resFiles.append(splitFileShared+str(dot)+str(sample)+trainingFileResSuffix)
				PRF1 = learningDot(resFiles)
				PRF1Array.append(PRF1)

			relRes = learningCurve(PRF1Array, xlabel, plotNameShared, -1)


	# --------------------------- drawing F1/P/R vs. n/p scores ----------------------
	
	xaxis = [str(x) for x in negPortions]
	xaxisLen = len(xaxis)

	direc2 = direc+"exp_"+expName+sys.argv[1]+"/"
	# loop over classifiers
	for classifierInd in range(len(classifiers)):

		negPortionRelP = []
		negPortionRelR = []
		negPortionRel = []
		# loop over negative ratios
		for negPortionInd in range(xaxisLen):
			# loop over runs
			relConfP = np.zeros([5, 3])
			relConfR = np.zeros([5, 3])
			relConf = np.zeros([5, 3])
			relConfRealP = []
			relConfRealR = []
			relConfReal = []
			for runInd in range(3):
				direcTmp = direc2+sys.argv[1]+str(classifierInd)+str(negPortionInd)+"/train"+str(lenThresArray-1)+str(runInd)+"Res" # what follows "/train" depends on the thresArray variable
				with open(direcTmp) as f:
					p = f.readline()
					r = f.readline()
					f1 = f.readline()
					pRel = p.split(' ')
					rRel = r.split(' ')
					f1Rel = f1.split(' ')
					for relInd in range(5):
						pRel[relInd] = float(pRel[relInd])
						rRel[relInd] = float(rRel[relInd])
						f1Rel[relInd] = float(f1Rel[relInd])
						relConfP[relInd][runInd] = pRel[relInd]
						relConfR[relInd][runInd] = rRel[relInd]
						relConf[relInd][runInd] = f1Rel[relInd]
			for relInd in range(5):
				relConfRealP.append(confidenceInterval(relConfP[relInd,:]))
				relConfRealR.append(confidenceInterval(relConfR[relInd,:]))
				relConfReal.append(confidenceInterval(relConf[relInd,:]))
			negPortionRelP.append(relConfRealP)
			negPortionRelR.append(relConfRealR)
			negPortionRel.append(relConfReal)


		plt.figure()
		for relInd in range(5):
			data = np.array(negPortionRelP)[:,relInd]
			Y = data[:,0]
			Y_err1 = Y - data[:,1]
			Y_err2 = data[:,2] - Y

			plt.errorbar(range(xaxisLen), Y, yerr=[Y_err1, Y_err2])

		plt.xticks(range(xaxisLen), xaxis, size='small')
		plt.ylim(0, 1)
		plt.legend(relation, loc=2)
		plt.title(classifiers[classifierInd])
		savefig(direc2+classifiers[classifierInd]+"P.png")


		plt.figure()
		for relInd in range(5):
			data = np.array(negPortionRelR)[:,relInd]
			Y = data[:,0]
			Y_err1 = Y - data[:,1]
			Y_err2 = data[:,2] - Y

			plt.errorbar(range(xaxisLen), Y, yerr=[Y_err1, Y_err2])

		plt.xticks(range(xaxisLen), xaxis, size='small')
		plt.ylim(0, 1)
		plt.legend(relation, loc=2)
		plt.title(classifiers[classifierInd])
		savefig(direc2+classifiers[classifierInd]+"R.png")


		plt.figure()
		for relInd in range(5):
			data = np.array(negPortionRel)[:,relInd]
			Y = data[:,0]
			Y_err1 = Y - data[:,1]
			Y_err2 = data[:,2] - Y

			plt.errorbar(range(xaxisLen), Y, yerr=[Y_err1, Y_err2])

		plt.xticks(range(xaxisLen), xaxis, size='small')
		plt.ylim(0, 1)
		plt.legend(relation, loc=2)
		plt.title(classifiers[classifierInd])
		savefig(direc2+classifiers[classifierInd]+"F1.png")


