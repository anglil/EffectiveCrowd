import numpy as np
import scipy as sp
import scipy.stats
import matplotlib.pyplot as plt
from pylab import *
import sys

def confidenceInterval(data, confidence=0.95):
	a = 1.0*np.array(data)
	n = len(a)
	m, se = np.mean(a), scipy.stats.sem(a)
	h = se * sp.stats.t.ppf((1+confidence)/2., n-1)
	return [m, m-h, m+h]

def learningCurve(resFile, resFileCS, i, j):
	dataAll = []
	for dot in range(5):
		data = []
		for run in range(10):
			with open(resFile+str(dot)+str(run)) as f:
				rowCount = 0
				for row in f:
					if rowCount == i:
						parts = row.split(' ')
						parts[4] = parts[4].strip('\n')
						data.append(float(parts[j]))
						break
					else:
						rowCount += 1
		dataAll.append(confidenceInterval(data))

	# the file with Bi is one that's created by logistic regression 
	with open("resTrainCS" + resFileCS) as f:
		rowCount = 0
		for row in f:
			if rowCount == i:
				parts = row.split(' ')
				parts[4] = parts[4].strip('\n')
				dataAll.insert(0, [float(parts[j])]*3)
				break
			else:
				rowCount += 1

	return dataAll

if __name__ == "__main__":
	resFile = None
	resFileCS = None
	if sys.argv[1] == "multir":
		resFile = "resDSMultir"
		resFileCS = "" # could add "Sorted"
	elif sys.argv[1] == "bi":
		resFile = "resDSBi"
		resFileCS = "Bi"
	else:
		raise NameError("can either be 'multir' or 'bi'")

	t = ["precision", "recall", "f1"]
	row = [0, 1, 2] # p, r, f1
	col = [0, 1, 2, 3, 4]
	for i in row:
		plt.figure()
		plt.xticks(range(6), ["CS", "0.01DS+CS", "0.04DS+CS", "0.16DS+CS", "0.64DS+CS", "0.64DS"], size='small')
		for j in col:
			dataAll = np.array(learningCurve(resFile, resFileCS, i, j))
			
			Y = dataAll[:,0]
			Y_err1 = Y - dataAll[:,1]
			Y_err2 = dataAll[:,2] - Y 

			plt.errorbar(range(6), Y, yerr=[Y_err1, Y_err2])
			# plt.title(str(i)+str(j))
		plt.legend(["nationality", "birth", "live", "death", "travel"])
		plt.title(t[i])
		savefig("DS_"+sys.argv[1]+"_"+t[i]+".png")




