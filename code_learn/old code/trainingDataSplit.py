import numpy as np
import sys
import subprocess


def getLen(inputFile):
	with open(inputFile) as fIn:
		for i, l in enumerate(fIn):
			pass
	return i + 1


def getStartBySplitLen(splitLen, lineNum, N):
	size = (lineNum - splitLen) / (N - 1)
	start = []
	for i in range(N):
		start.append(i*size)
	return start


def splitTraining(start, splitLen, trainingFile, trainingFileSplit):
	count = 0
	with open(trainingFileSplit, 'wb') as fOut:
		with open(trainingFile) as fIn:
			for row in fIn:
				count += 1
				if count < start:
					continue
				if count > start + splitLen:
					break
				fOut.write(row)


def getData(trainingFile, trainingFileSplit, splitTarget):
	lineNum = getLen(trainingFile)

	splitLen = None
	if splitTarget == "DS":
		splitLen = lineNum*np.array([0.01, 0.04, 0.16, 0.64, 0.64])
	elif splitTarget == "CS":
		splitLen = lineNum*np.array(range(1, 10))/10.0 # the reason not to make it to 11 is because the 11th split does not have deviation
	
	countI = 0
	for i in splitLen:
		start = getStartBySplitLen(i, lineNum, 10) # split into 10 pieces for deriving the confidence interval
		countJ = 0
		for j in start:
			splitTraining(j, i, trainingFile, trainingFileSplit)
			print countI, countJ
			countJ += 1
		countI += 1


if __name__ == "__main__":

	# data to be split
	trainingFile = sys.argv[1]
	# data split
	trainingFileSplit = sys.argv[2] # two directory layers
	# split DS or CS for evaluation
	splitTarget = sys.argv[3]

	if splitTarget not in ["DS", "CS"]:
		raise NameError("The data target must either be 'DS' or 'CS'!")

	getData(trainingFile, trainingFileSplit, splitTarget)
