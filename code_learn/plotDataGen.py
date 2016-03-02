import numpy as np
import scipy as sp
import scipy.stats
import matplotlib.pyplot as plt
from pylab import *
import sys

# assuming normal distribution
def confidenceInterval(data, confidence=0.95):
	a = 1.0*np.array(data)
	n = len(a)
	m, se = np.mean(a), scipy.stats.sem(a)
	h = se * sp.stats.t.ppf((1+confidence)/2., n-1)
	return [m, m-h, m+h]

# {sampleTimes} data points
# 3 metrics
# 5 relations
def learningDot(resFiles):
	num = len(resFiles)
	data = np.zeros([3, 5, num])
	PRF1 = np.zeros([3, 5, 3])

	resCount = 0
	for res in resFiles:
		with open(res) as f:
			rowCount = 0
			for row in f:
				parts = row.split(' ')
				parts[4] = parts[4].strip('\n')
				for colCount in range(5):
					data[rowCount][colCount][resCount] = float(parts[colCount])
				rowCount += 1
		resCount += 1

	for rowCount in range(3):
		for colCount in range(5):
			PRF1[rowCount][colCount] = np.array(confidenceInterval(data[rowCount][colCount]))

	return PRF1

# PRF1Array: precision, recall, f1 * all the relations * all the data points
def learningCurve(PRF1Array, xlabel, imageName, relIndex):
	num = len(PRF1Array)

	relRes = []

	
	t = ["Precision", "Recall", "F1"]
	rel = ["nationality", "birth", "live", "death", "travel"]

	for rowCount in range(3):
		if relIndex == -1:
			plt.figure() 
		
		for colCount in range(5):

			data = np.zeros([num, 3])
			for resCount in range(num):
				data[resCount] = np.array(PRF1Array[resCount][rowCount][colCount])
			Y = data[:,0]
			Y_err1 = Y - data[:,1]
			Y_err2 = data[:,2] - Y

			if relIndex == -1:
				plt.errorbar(range(num), Y, yerr=[Y_err1, Y_err2])
			else:
				if colCount == relIndex:
					relRes.append([Y, Y_err1, Y_err2])
					break

		if relIndex == -1:
			plt.xticks(range(num), xlabel, size='small')
			plt.ylim(0, 1)
			plt.legend(rel, loc=4)
			plt.title(t[rowCount])
			savefig(imageName + t[rowCount] + ".png")

	return relRes

if __name__ == "__main__":
	thresArrayLabel = [0.01, 0.04, 0.16, 0.64]
	xlabel = [str(x) for x in thresArrayLabel]
	negPortions = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
	for negPortionInd in range(len(negPortions)):
		mydir = "/home/anglil/csehomedir/learner/exp_DSwithoutCS2strict/strict1"+str(negPortionInd)+"/"
		plotNameShared = mydir + "plot"
		splitFileShared = mydir + "train"
		trainingFileResSuffix = "Res"
		lenThresArray = 4
		sampleTimes = 3

		resFiles = []
		for sample in range(sampleTimes):
			resFiles.append(splitFileShared+'3'+str(sample)+trainingFileResSuffix)
		PRF1 = learningDot(resFiles)

		print PRF1