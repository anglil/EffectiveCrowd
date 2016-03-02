# get the length of a file
# concatenate two files

import os
import shutil
import numpy as np

# ----------------------- get the length of a file -------------------
def getLen(inputFile):
	if os.stat(inputFile).st_size == 0:
		return 0
	with open(inputFile) as fIn:
		for i, l in enumerate(fIn):
			pass
	return i + 1

# -------------concatenate partial files-----------------------
def fileConcatPartial(file1, thres1, bag1, file2, thres2, bag2, resFile):
	tmp1 = None
	if thres1<1:
		tmp1 = getPartialFile(file1, bag1, thres1, resFile+"tmp1")
	else:
		tmp1 = getPartialFile(file1, bag1, 1, resFile+"tmp1")

	tmp2 = None
	if thres2<1:
		tmp2 = getPartialFile(file2, bag2, thres2, resFile+"tmp2")
	else:
		tmp2 = getPartialFile(file2, bag2, 1, resFile+"tmp2")
	
	fileConcat(tmp1, tmp2, resFile)

# ------------- concatenate two files --------------------------
# resFile must have a different name than file1 and file2
def fileConcat(file1, file2, resFile):
	if file1 == -1:
		shutil.copyfile(file2, resFile)
		return
	if file2 == -1:
		shutil.copyfile(file1, resFile)
		return
	with open(resFile, 'wb') as fw:
		with open(file1) as f1:
			for row in f1:
				fw.write(row)
		with open(file2) as f2:
			for row in f2:
				fw.write(row)

# -------------only apply to sorted files-----------------------
# the argument thres is a fraction
def getPartialFile(stdFile, bagOrTriple, thres, resFile):
	if stdFile == -1:
		return -1 
	if thres == 0:
		return -1
	if thres == 1:
		return stdFile

	num = getLen(stdFile)
	thres = thres * num

	instanceCtr = 0
	pairPre = None
	with open(resFile, 'wb') as fw:
		with open(stdFile) as f:
			for row in f:
				# triple construction
				if bagOrTriple == "triple":
					if instanceCtr >= thres:
						break
					else:
						fw.write(row)
						instanceCtr += 1

				# bag construction
				if bagOrTriple == "bag":
					parts = row.split('\t')
					arg1 = parts[0]
					arg2 = parts[3]
					pair = arg1 + ' ' + arg2
					if pair == pairPre:
						fw.write(row)
						instanceCtr += 1
					else:
						if instanceCtr >= thres:
							break
						else:
							fw.write(row)
							instanceCtr += 1
						pairPre = pair
	# return when a partial file is not empty
	return resFile

# ------------- add one negative example to the training data -----------
def addOneNeg(trainingFile, negFile):
	oneNeg = None
	with open(negFile) as f:
		oneNeg = f.readline()
	with open(trainingFile, 'a') as fw:
		fw.write(oneNeg)


# ------------- run embedded bash scripts in python------------
def runScript(script, stdin=None):
	"""Returns (stdout, stderr), raises error on non-zero return code"""
	import subprocess
	# Note: by using a list here (['bash', ...]) you avoid quoting issues, as the 
	# arguments are passed in exactly this order (spaces, quotes, and newlines won't
	# cause problems):
	proc = subprocess.Popen(['bash', '-c']+script,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		stdin=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	if proc.returncode:
		raise ScriptException(proc.returncode, stdout, stderr, script)
	return stdout, stderr

class ScriptException(Exception):
	def __init__(self, returncode, stdout, stderr, script):
		self.returncode = returncode
		self.stdout = stdout
		self.stderr = stderr
		Exception.__init__('Error in script')
	def __str__():
		print 'error'


# ------------- get certain amount of negative data based on the proportion provided ----------
# param: xTrain, lil sparse matrix
# param: yTrain, numpy array
# param: negPortion, could be equal to 0.0, 0.4, 0.8, ...
def dataSlice(xTrain, yTrain, negPortion):
	
	posNum = yTrain.sum()
	negNum = int(posNum*negPortion)
	if negNum == 0:
		negNum = 1
	rowNum = len(yTrain)

	xOut = lil_matrix((posNum+negNum, xTrain._shape[1]), dtype=np.int8)
	yOut = np.zeros(posNum+negNum)

	posCtr = 0
	negCtr = 0
	ctr = 0
	for i in range(rowNum):
		# a negative example
		if yTrain[i] == 0:
			if negCtr >= negNum:
				continue
			negCtr += 1

			yOut[ctr] = yTrain[i]
			xOut[ctr, :] = xTrain[i, :]
			ctr += 1
		# a positive example
		else:
			if posCtr >= posNum:
				break
			posCtr += 1

			yOut[ctr] = yTrain[i]
			xOut[ctr, :] = xTrain[i, :]
			ctr += 1

	return xOut, yOut 


def fileSlice(trainingFile, rel, negPortion, trainingFileRel):
	posNum = 0
	with open(trainingFile) as f:
		for row in f:
			parts = row.split('\t')
			if rel == parts[7]:
				posNum += 1
	negNum = int(posNum*negPortion)
	if negNum == 0:
		negNum = 1

	posCtr = 0
	negCtr = 0
	with open(trainingFile) as f:
		with open(trainingFileRel, 'wb') as fw:
			for row in f:
				# a positive example
				if rel == row.split('\t')[7]:
					if posCtr >= posNum:
						break
					posCtr += 1

					fw.write(row)
				# a negative example
				else:
					if negCtr >= negNum:
						continue
					negCtr += 1

					fw.write(row)



# ------------- delete a certain row from a lil sparse matrix	
def delete_row_lil(mat, i):
	if not isinstance(mat, lil_matrix):
		raise ValueError("works only for LIL format -- use .tolil() first")
	mat.rows = np.delete(mat.rows, i)
	mat.data = np.delete(mat.data, i)
	mat._shape = (mat._shape[0] - 1, mat._shape[1])
	X_train = lil_matrix((num, lenFeatures), dtype=np.int8)


# -------------- get positive and negative training data for each relation ---------
def getPosNegFileRel(fullFile, posFile, negFile, posRelFiles, negRelFiles):
	relation = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']
	
	posFileLen = 0
	negFileLen = 0
	posRelFilesLen = np.zeros(5)
	negRelFilesLen = np.zeros(5)


	flag = 1
	if os.path.exists(posFile):
		# os.remove(posFile)
		# print posFile, "deleted"
		posFileLen = getLen(posFile)
	else:
		flag = 0
	if os.path.exists(negFile):
		# os.remove(negFile)
		# print negFile, "deleted"
		negFileLen = getLen(negFile)
	else:
		flag = 0

	for i in range(len(posRelFiles)):
		if os.path.exists(posRelFiles[i]):
			# os.remove(posRelFiles[i])
			# print posRelFiles[i], "deleted"
			posRelFilesLen[i] = getLen(posRelFiles[i])
		else:
			flag = 0
		if os.path.exists(negRelFiles[i]):
			# os.remove(negRelFiles[i])
			# print negRelFiles[i], "deleted"
			negRelFilesLen[i] = getLen(negRelFiles[i])
		else: 
			flag = 0

	if flag == 1:
		print "split files exist."
		return posFileLen, negFileLen, posRelFilesLen, negRelFilesLen

	# write to relation-wise files
	with open(fullFile) as f:
		for row in f:
			parts = row.split('\t')
			rel = parts[7]
			relInd = relation.index(rel)

			# ---------NA---------
			if relInd == 5:
				with open(negFile, 'a') as fw:
					fw.write(row)
				negFileLen += 1


				# pass
				for i in range(5):
					with open(negRelFiles[i], 'a') as fw2:
						fw2.write(row)
					negRelFilesLen[i] += 1

			# ------with a relation-------
			else:
				with open(posFile, 'a') as fw:
					fw.write(row)
				posFileLen += 1


				for i in range(5):
					if i != relInd:
						with open(negRelFiles[i], 'a') as fw2:
							partsNeg = list(parts)
							partsNeg[7] = 'NA'
							fw2.write('\t'.join(partsNeg))
						negRelFilesLen[i] += 1
					else:
						with open(posRelFiles[relInd], 'a') as fw2:
							fw2.write(row)
						posRelFilesLen[relInd] += 1

	print "Splitting by relation done."
	return posFileLen, negFileLen, posRelFilesLen, negRelFilesLen

# ------------------- get optimal proportion ----------------------------
def getOptimalCSTraining(posFile, negFile, optProportion, optProportions):
	direc = "/homes/gws/anglil/learner/"
	# posFile = direcCS+"gabor_CS_MJ_new_feature_shuffled_pos"#"train_CS_MJ_pos_comb_new_feature"
	# negFile = direcCS+"gabor_CS_MJ_new_feature_shuffled_neg"#"train_CS_MJ_neg_comb_new_feature"
	posFileLen = getLen(posFile)
	negFileLen = getLen(negFile)

	relation = ["nationality", "born", "lived", "died", "travel"]

	resFile = direc+"data_train_CS/train_CS_opt"
	resFileRel = []
	for i in range(5):
		resFileRel.append(resFile+relation[i])

	# if os.path.exists(resFile):
	# 	print "optimal files exist."
	# 	return resFile, resFileRel

	# optProportion = 1.0
	fileConcatPartial(posFile, 1, "triple", negFile, optProportion*posFileLen/negFileLen, "triple", resFile)
	
	# No.1: optimal percentage for our CS data
	# optProportions = [1.6, 3.0, 1.6, 3.0, 3.0]
	# No.2: optimal percentage for Gabor's CS data
	# optProportions = [2, 3, 1, 2, 1]

	for i in range(5):
		p = posFile+"_"+relation[i]
		n = negFile+"_"+relation[i]
		pLen = getLen(p)
		nLen = getLen(n)
		fileConcatPartial(p, 1, "triple", n, optProportions[i]*pLen/nLen, "triple", resFileRel[i])

	return resFile, resFileRel