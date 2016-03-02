import numpy as np
import HTMLParser
import sys


# --------------------- get a dictionary that maps questions to relation labels -----------
def get_rel_by_question(stdFile):
	relDict = {}
	with open(stdFile) as f:
		for row in f:
			parts = row.split('\t')
			arg1StartOffset = parts[1]
			arg1EndOffset = parts[2]
			arg2StartOffset = parts[4]
			arg2EndOffset = parts[5]
			docName = parts[6]

			rel = parts[7]

			sentKey = docName+":"+arg1StartOffset+'-'+arg1EndOffset+":"+arg2StartOffset+'-'+arg2EndOffset

			relDict[sentKey] = rel
	return relDict


h = HTMLParser.HTMLParser()
reload(sys)
sys.setdefaultencoding("utf-8")

direc = '/home/anglil/csehomedir/learner/'
GaborLabelFile = direc+'data_featurized/Gabor_CS_new_feature'
ourLabelFile = direc+'data_train_CS/Gabor_CS_MJ_new_feature'
relName = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel', 'NA']
relDictGabor = get_rel_by_question(GaborLabelFile)

ctr = 0
with open('500Sent', 'wb') as fw:
	with open(ourLabelFile) as f:
		for row in f:
			parts = row.split('\t')
			arg1 = parts[0]
			arg1StartOffset = parts[1]
			arg1EndOffset = parts[2]
			arg2 = parts[3]
			arg2StartOffset = parts[4]
			arg2EndOffset = parts[5]
			docName = parts[6]
			ourLabel = parts[7]
			docText = h.unescape(parts[11])

			sentKey = docName+":"+arg1StartOffset+'-'+arg1EndOffset+":"+arg2StartOffset+'-'+arg2EndOffset

			GaborLabel = relDictGabor[sentKey]


			tmp = np.zeros(5)
			relInd = relName.index(ourLabel)
			if relInd != 5:
				tmp[relName.index(ourLabel)] = 1
			tmp = '\tempty\t'.join(str(x) for x in tmp)
			tmp += '\tempty\n'

			line = docText+'\t'+arg1+'\t'+arg2+'\t'+GaborLabel+'\t'+tmp
			fw.write(line)


