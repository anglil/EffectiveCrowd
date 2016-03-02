
def tunePos(myFile):
	with open(myFile) as f:
		with open('new_'+myFile, 'wb') as fw:
			for row in f:
				parts = row.split('\t')
				lenParts = len(parts)
				newParts = list(parts)
				newParts.pop()
				newParts.insert(0, parts[lenParts-1].strip('\n'))
				newParts[lenParts-1] = newParts[lenParts-1]+'\n'
				fw.write('\t'.join(newParts))

if __name__ == "__main__":
	relation = ['nationality', 'born', 'lived', 'died', 'travel']
	np = ['1.6', '3.0']
	na = ['NA', 'noneNA']

	for i in relation:
		for j in np:
			for k in na:
				tunePos("test_strict_"+i+"_"+j+"_"+k)

