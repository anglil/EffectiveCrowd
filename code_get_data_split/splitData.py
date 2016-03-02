import numpy as np
import os

# splitting data means to get separate sets of DS and CS and test data, and development set if necessary
# generating 
# data_train_pre_CS, 
# data_test, and 
# data_train_DS
# under this definition, below is a wrong implementation

def writeSplitDataToFile(stdFile, posFile, negFile):

	posCtr = 0
	negCtr = 0

	direc = "/homes/gws/anglil/learner/data_train_DS/"

	with open(negFile, 'wb') as fneg:
		with open(posFile, 'wb') as fpos:
			with open(stdFile) as f:
				for row in f:
					parts = row.split('\t')
					rel = parts[7]
					if rel == 'NA':
						fneg.write(row)
						negCtr += 1
					else:
						fpos.write(row)
						posCtr += 1 
	print 'amount of positive examples:', posCtr
	print 'amount of negative examples:', negCtr


# -------------------- posFiles and negFiles are vectors ---------------------------
def writeSplitDataTofileByRelation(stdFile, posFiles, negFiles):
	# make sure the posFiles and negFiles are mint
	for pFile in posFiles:
		if os.path.exists(pFile):
			os.remove(pFile)
	for nFile in negFiles:
		if  os.path.exists(nFile):
			os.remove(nFile)

	posCtr = np.zeros(5)
	negCtr = np.zeros(5)

	with open(stdFile) as f:
		for row in f:
			parts = row.split('\t')

			arg1 = parts[0]
			arg1StartOffset = parts[1]
			arg1EndOffset = parts[2]
			arg2 = parts[3]
			arg2StartOffset = parts[4]
			arg2EndOffset = parts[5]
			docName = parts[6]
			rel = parts[7]

			relInd = relName.index(rel)

			for i in range(5):
				# a positive example:
				if relInd == i:
					posCtr[i] += 1
					fw = open(posFiles[i], 'a')
					fw.write(row)
					fw.close()
				# a negative example
				else:
					negCtr[i] += 1
					fw = open(negFiles[i], 'a')
					fw.write(row)
					fw.close()
	print 'amount of positive examples by relation:', posCtr
	print 'amount of negative examples by relation:', negCtr



if __name__ == "__main__":
	relName = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']
	relAlias = ["nationality", "born", "lived", "died", "travel"]
	direc = '/homes/gws/anglil/learner/'
	CSFileGabor = direc+'data_train_CS/gabor_CS_MJ_new_feature_shuffled'
	CSFileGaborPos = CSFileGabor+'_pos'
	CSFileGaborNeg = CSFileGabor+'_neg'
	CSFilesGaborPos = []
	CSFilesGaborNeg = []
	for item in relAlias:
		CSFilesGaborPos.append(CSFileGaborPos+'_'+item)
		CSFilesGaborNeg.append(CSFileGaborNeg+'_'+item)

	writeSplitDataToFile(CSFileGabor, CSFileGaborPos, CSFileGaborNeg)
	writeSplitDataTofileByRelation(CSFileGabor, CSFilesGaborPos, CSFilesGaborNeg)
