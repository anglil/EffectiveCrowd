# main_F1_vs_np
import matplotlib.pylab as plt
import numpy as np
from evaluation import *

if __name__ == "__main__":
	expName = "grammar"
	rel = ["nationality", "birth", "live", "death", "travel"]
	c = ['multir', 'multir binary', 'LR', 'perceptron']
	xaxis = ['0.0', '0.4', '0.8', '1.2', '1.6', '3.0', '4.0', '5.0', '6.0', '8.0']
	xaxisLen = len(xaxis)

	direc = "../exp_"+expName+sys.argv[1]+"/"+ sys.argv[1]
	# loop over classifiers
	for classifierInd in range(4):
		
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
				direcTmp = direc+str(classifierInd)+str(negPortionInd)+"/train0"+str(runInd)+"Res" # what follows "/train" depends on the thresArray variable
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
		plt.legend(rel, loc=2)
		plt.title(c[classifierInd])
		savefig("../exp_"+expName+sys.argv[1]+"/"+c[classifierInd]+"P.png")


		plt.figure()
		for relInd in range(5):
			data = np.array(negPortionRelR)[:,relInd]
			Y = data[:,0]
			Y_err1 = Y - data[:,1]
			Y_err2 = data[:,2] - Y

			plt.errorbar(range(xaxisLen), Y, yerr=[Y_err1, Y_err2])

		plt.xticks(range(xaxisLen), xaxis, size='small')
		plt.ylim(0, 1)
		plt.legend(rel, loc=2)
		plt.title(c[classifierInd])
		savefig("../exp_"+expName+sys.argv[1]+"/"+c[classifierInd]+"R.png")


		plt.figure()
		for relInd in range(5):
			data = np.array(negPortionRel)[:,relInd]
			Y = data[:,0]
			Y_err1 = Y - data[:,1]
			Y_err2 = data[:,2] - Y

			plt.errorbar(range(xaxisLen), Y, yerr=[Y_err1, Y_err2])

		plt.xticks(range(xaxisLen), xaxis, size='small')
		plt.ylim(0, 1)
		plt.legend(rel, loc=2)
		plt.title(c[classifierInd])
		savefig("../exp_"+expName+sys.argv[1]+"/"+c[classifierInd]+"F1.png")









				
