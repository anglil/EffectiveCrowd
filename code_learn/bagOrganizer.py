import numpy as np
import sys
import os
import random
from fileProcessing import *



# ----------------------- organize sentences into bags (and triples) -------------------------
# stdFile: standard distance supervision file
# bagOrTriple: "bag", "triple", or anything else
def bagTripleConstruction(stdFile, bagOrTriple):
	bags = {}
	triples = {}
	with open(stdFile) as f:
		for row in f:
			parts = row.split('\t')
			arg1 = parts[0]
			arg2 = parts[3]
			pair = arg1 + ' ' + arg2

			# bag construction
			if bagOrTriple == "bag":
				if pair in bags:
					bags[pair].append(row)
				else:
					bags[pair] = [row]

			# triple construction
			if bagOrTriple == "triple":
				rel = parts[6]
				sent = pair + ' ' + rel
				if sent in triples:
					triples[sent].append(row)
				else:
					triples[sent] = [row]

	if bagOrTriple != "triple":
		return bags
	elif bagOrTriple != "bag":
		return triples




# ---------------- get certain number of sentences from organized bags --------------
# bags: sentences organized by the pair of mentions
# thresArray: thresholding the amount of sentences to take; there is an array of thresholds
# resFileIn: write the re-sorted sentences to file
def getRandomBags(bags, thresArray, resFileIn):
	pairs = bags.keys()
	# shuffling bags
	random.shuffle(pairs)
	instanceCtr = 0

	content = []

	thresIndex = 0
	thresArrayLen = len(thresArray)

	resFileOuts = []

	for pair in pairs:
		instances = bags[pair]
		for instance in instances:
			content.append(instance)
			instanceCtr += 1
		# maintaining integral bags
		if instanceCtr >= thresArray[thresIndex]:
			print "training size:", instanceCtr
			resFileOut = resFileIn+str(thresIndex)
			with open(resFileOut, 'wb') as fw:
				fw.write("".join(content))
			resFileOuts.append(resFileOut)
			thresIndex += 1
			# all the thresholds are visited
			if thresIndex == thresArrayLen:
				break
	return resFileOuts



# -------------- get the split data -----------------------------
# scalingFile: the file that gets split
# thresArray: 
# staticFile: the file that adds to the split scalingFile
# resFileIn: a name shared in part by all resulting files
def getSplitData(scalingFile, thresArray, bagOrTriple, sampleTimes, staticFile, resFileIn):
	lenScalingFile = getLen(scalingFile)

	resFileOuts = []

	# do random sampling for sampleTimes times
	bags = bagTripleConstruction(scalingFile, bagOrTriple)
	for sample in range(sampleTimes):
		scalingFiles = getRandomBags(bags, np.array(thresArray)*lenScalingFile, resFileIn+str(sample)+'tmp')

		count = 0
		for scalingFileFinal in scalingFiles:
			resFileOut = resFileIn+str(count)+str(sample)
			# file concatenation
			if staticFile != -1:
				fileConcat(scalingFileFinal, staticFile, resFileOut)
				os.remove(scalingFileFinal)
			else:
				os.rename(scalingFileFinal, resFileOut)

			resFileOuts.append(resFileOut)
			count += 1
		print "%d sampled" % sample

	return resFileOuts








