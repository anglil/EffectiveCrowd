import os
import sys
import numpy as numpy
from fileProcessing import *
from bagOrganizer import *
from classifier import *
from evaluation import *

# interface:
# expName
# CSFile
# testFile (don't change)
# featureFile
# posFile (also covers relation-wise pos files under name conventions)
# negFile (also covers relation-wise pos files under name conventions)

if __name__ == "__main__":
	expName = "combGaborOur"#"mimlour"#"mimlgaborour"#"mimlgabororigin"#"gabororiginalCS2"#"gaborCSMoreNeg2"#"onlyNoneNAShuffled"
	direc = "/homes/gws/anglil/learner/"
	sampleTimes = 3
	pruningThres = 0

	# positive and negative training files that include all 5 relations
	# No. 1
	# "data_train_CS/train_CS_MJ_comb_new_feature_shuffled"
	# No. 2: formal experiment for our data
	# "data_train_CS/gabor_CS_MJ_new_feature_shuffled"
	# No. 3: 
	# "data_train_CS/gabor_CS_original_new_feature"
	# No. 4:
	# "data_train_CS/combGaborOur_CS_new_feature"
	CSFile = direc+"data_train_CS/combGaborOur_CS_new_feature"
	
	# test file
	testFile = direc+"data_test/test_"+sys.argv[1]+"_new_feature_no_grammatic" # Note: right now only the test data under the strict rule is no-grammatic sentence free

	# feature file with which to construct a feature vector; provide a name, and we'll create it for you
	# No. 1
	# "data_featurized/data_CS_and_test"
	# No. 2
	# "data_featurized/gabor_CS_and_test"
	# No. 3
	# "data_featurized/gabororiginal_CS_and_test"
	# No. 4
	# "data_featurized/combGaborOur_CS_and_test"
	featureFile = direc+"data_featurized/combGaborOur_CS_and_test"
	fileConcat(CSFile, testFile, featureFile)

	allFeatures = getFeatures(featureFile, pruningThres)

	# -------------- relation alias ------------------------
	relation = ["nationality", "born", "lived", "died", "travel"]

	# ------------- generating positive and negative training data for each relation ---------
	# No. 1
	# "data_train_CS/train_CS_MJ_pos_comb_new_feature"
	# "data_train_CS/train_CS_MJ_neg_comb_new_feature"
	# No. 2
	# "data_train_CS/gabor_CS_MJ_new_feature_shuffled_pos"
	# "data_train_CS/gabor_CS_MJ_new_feature_shuffled_neg"
	# No. 3
	# "data_train_CS/gabor_CS_original_new_feature_shuffled_pos"
	# "data_train_CS/gabor_CS_original_new_feature_shuffled_neg"
	# No. 4
	# "data_train_CS/combGaborOur_CS_new_feature_pos"
	# "data_train_CS/combGaborOur_CS_new_feature_neg"
	posFile = direc+"data_train_CS/combGaborOur_CS_new_feature_pos"
	negFile = direc+"data_train_CS/combGaborOur_CS_new_feature_neg"

	posRelFiles = []
	negRelFiles = []
	for relationWalker in relation:
		posRelFile = posFile + "_" + relationWalker # relation-wise positive data naming convention 
		negRelFile = negFile + "_" + relationWalker # relation-wise negative data naming convention
		posRelFiles.append(posRelFile)
		negRelFiles.append(negRelFile)

	posFileLen, negFileLen, posRelFilesLen, negRelFilesLen = getPosNegFileRel(CSFile, posFile, negFile, posRelFiles, negRelFiles)


	# ------------- test data and gold labels regarding all relations ----------
	y_gold, X_test = getTestAndGoldData(testFile, allFeatures)
	

	# ------------ experiment parameters ------------------
	DS_CS = "CS"
	classifiers = ["multir", "LR"]#["multir", "multirBinary", "LR", "perceptron"]
	negPortions = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0]
	

	# -------------- global variables that depend on the experiment parameters ----------
	thresArrayLabel = []

	thresArray = None
	bagOrTriple = None

	if DS_CS == "CS":
		thresArray = [0.96]
		bagOrTriple = "triple"
	elif DS_CS == "DS":
		thresArray = [0.01, 0.04, 0.16, 0.64]
		bagOrTriple = "bag"
	lenThresArray = len(thresArray)

	thresArrayLabel += thresArray

	xlabel = [str(x) for x in thresArrayLabel]

	# ------------------ loop over classifier types and negative portion numbers ------------ 
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

			staticTrainingFile = -1 #mydir+"staticTrainingFile"
			scalingTrainingFile = mydir+"scalingTrainingFile"

			# TODO: when doing DS, staticTrainingFile should be changed

			# ----------------------- experiment ------------------------
			if classifier in ["LR", "perceptron"]:
				p = [[],[],[],[],[]]
				r = [[],[],[],[],[]]
				f1 = [[],[],[],[],[]]
				trainingFiles = None

				for relInd in range(5):
					fileConcatPartial(posRelFiles[relInd], 1, bagOrTriple, negRelFiles[relInd], negPortion*posRelFilesLen[relInd]/negRelFilesLen[relInd], bagOrTriple, scalingTrainingFile+str(relInd))
					# going through thresholds and samplings
					trainingFiles = getSplitData(scalingTrainingFile+str(relInd), thresArray, bagOrTriple, sampleTimes, staticTrainingFile, splitFileShared)

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
				fileConcatPartial(posFile, 1, bagOrTriple, negFile, negPortion*posFileLen/negFileLen, bagOrTriple, scalingTrainingFile)
				# going through thresholds and samplings
				trainingFiles = getSplitData(scalingTrainingFile, thresArray, bagOrTriple, sampleTimes, staticTrainingFile, splitFileShared)

				for trainingFile in trainingFiles:
					print "training size:", getLen(trainingFile)
					trainAndTestModelMultiR(trainingFile, testFile, trainingFile+trainingFileResSuffix)

			elif classifier == "mimlre":
				fileConcatPartial(posFile, 1, bagOrTriple, negFile, negPortion*posFileLen/negFileLen, bagOrTriple, scalingTrainingFile)
				# going through thresholds and samplings
				trainingFiles = getSplitData(scalingTrainingFile, thresArray, bagOrTriple, sampleTimes, staticTrainingFile, splitFileShared)

				for trainingFile in trainingFiles:
					addOneNeg(trainingFile, negRelFile)
					addOneNeg(trainingFile, posRelFile)
					print "training size:", getLen(trainingFile)
					trainAndTestModelMIML(trainingFile, testFile+"_miml", trainingFile+trainingFileResSuffix)

			elif classifier == "multirBinary":
				p = [[],[],[],[],[]]
				r = [[],[],[],[],[]]
				f1 = [[],[],[],[],[]]
				trainingFiles = None

				for relInd in range(5):
					fileConcatPartial(posRelFiles[relInd], 1, bagOrTriple, negRelFiles[relInd], negPortion*posRelFilesLen[relInd]/negRelFilesLen[relInd], bagOrTriple, scalingTrainingFile+str(relInd))
					# going through thresholds and samplings
					trainingFiles = getSplitData(scalingTrainingFile+str(relInd), thresArray, bagOrTriple, sampleTimes, staticTrainingFile, splitFileShared)

					for trainingFile in trainingFiles:
						print "training size:", getLen(trainingFile)
						p0, r0, f10 = trainAndTestModelMultiRBinary_2(trainingFile, testFile, relInd, trainingFile+trainingFileResSuffix+"tmp")
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




















