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
# xlabel: an array of strings that label the x axis, not used when relIndex is not -1
# imageName: give a name shared in part by three images generated, not used when relIndex is not -1
# relIndex: if it is one of the relation indices, then only output the prf1 of that relation
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


# relResArray: relation -> prf1 -> Y, Y_err1, Y_err2
def drawIndividualCurve(relResArray, xlabel, imageName):
	t = ["Precision", "Recall", "F1"]
	rel = ["nationality", "birth", "live", "death", "travel"]

	for rowCount in range(3):
		plt.figure()
		lenY = None
		for colCount in range(5):
			tmp = relResArray[colCount][rowCount]
			Y = tmp[0]
			Y_err1 = tmp[1]
			Y_err2 = tmp[2]
			lenY = len(Y)

			plt.errorbar(range(lenY), Y, yerr=[Y_err1, Y_err2])

		plt.xticks(range(lenY), xlabel, size='small')
		plt.ylim(0,1)
		plt.legend(rel, loc=4)
		plt.title(t[rowCount])
		savefig(imageName + t[rowCount] + ".png")










				

