import numpy as np

relName = ['per:origin', \
	'/people/person/place_of_birth', \
	'/people/person/place_lived', \
	'/people/deceased_person/place_of_death', \
	'travel']

tpOur = np.zeros(5)
fpOur = np.zeros(5)
fnOur = np.zeros(5)
tpGabor = np.zeros(5)
fpGabor = np.zeros(5)
fnGabor = np.zeros(5)
tpGrossOur = 0
fpGrossOur = 0
fnGrossOur = 0
tpGrossGabor = 0
fpGrossGabor = 0
fnGrossGabor = 0


ctr = 0
with open('500Sent_labeled') as f:
	for row in f:
		parts = row.split('\t')
		gaborLabel = parts[3] 
		gaborLabelArray = np.zeros(5)
		gaborLabelArray[relName.index(gaborLabel)] = 1

		ourLabelArray = np.zeros(5)
		goldLabelArray = np.zeros(5)
		for i in range(5):
			ourLabelArray[i] = int(parts[4+2*i])
			goldLabelArray[i] = int(parts[5+2*i])

		for i in range(5):
			if goldLabelArray[i] == 1:
				if ourLabelArray[i] == 1:
					tpOur[i] += 1
				else:
					fnOur[i] += 1
				if gaborLabelArray[i] == 1:
					tpGabor[i] += 1
				else:
					fnGabor[i] += 1
			else:
				if ourLabelArray[i] == 1:
					fpOur[i] += 1
				if gaborLabelArray[i] == 1:
					fpGabor[i] += 1

		ctr += 1
		if ctr >= 203:
			break

print tpOur
print fpOur
print fnOur
print tpGabor
print fpGabor
print fnGabor

pOur = np.divide(tpOur * 1.0, tpOur + fpOur)
print "Precision:", pOur
rOur = np.divide(tpOur * 1.0, tpOur + fnOur)
print "Recall:", rOur
f1Our = np.divide(2.0*tpOur, 2*tpOur + fnOur + fpOur)
print "F1:", f1Our

pGabor = np.divide(tpGabor * 1.0, tpGabor + fpGabor)
print "Precision:", pGabor
rGabor = np.divide(tpGabor * 1.0, tpGabor + fnGabor)
print "Recall:", rGabor
f1Gabor = np.divide(2.0*tpGabor, 2*tpGabor + fnGabor + fpGabor)
print "F1:", f1Gabor