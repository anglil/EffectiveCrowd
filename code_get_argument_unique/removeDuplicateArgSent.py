import numpy as np
from mentionPosIdentifier import *

# files to featurize:
# data_train_CS/train_CS_MJ_pos_comb_new_feature
# data_train_CS/train_CS_MJ_neg_comb_new_feature
# data_test/test_relaxed_new_feature
# data_test/test_strict_new_feature

def removeDuplicateArgSent(stdFileIn, stdFileOut):
	with open(stdFileIn) as f:
		with open(stdFileOut, 'wb') as fw:
			for row in f:
				parts = row.split('\t')
				arg1 = parts[0]
				arg1StartOffset = parts[1]
				arg1EndOffset = parts[2]
				arg2 = parts[3]
				arg2StartOffset = parts[4]
				arg2EndOffset = parts[5]
				sent = parts[11]

				sentTok = sent.split(' ')
				sentTokCopy = list(sentTok)
				# replace the word for arg1 and arg2
				for i in range(int(arg1StartOffset), int(arg1EndOffset)):
					sentTokCopy[i] = 'arg'
				for j in range(int(arg2StartOffset), int(arg2EndOffset)):
					sentTokCopy[j] = 'arg'
				sentTokCopy = ' '.join(sentTokCopy)

				# write the same row if either one of the two arguments can't be found twice
				arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset = get_entity_pos(arg1, arg2, sentTokCopy)
				if (arg1StartOffset == -1) and (arg1EndOffset == -1) and (arg2StartOffset == -1) and (arg2EndOffset == -1):
					fw.write(row)

if __name__ == "__main__":
	direc = '/homes/gws/anglil/learner/'

	stdFileIn1 = "data_train_CS/train_CS_MJ_pos_comb_new_feature"
	stdFileIn2 = "data_train_CS/train_CS_MJ_neg_comb_new_feature"
	stdFileIn3 = "data_test/test_relaxed_new_feature"
	stdFileIn4 = "data_test/test_strict_new_feature"
	removeDuplicateArgSent(direc+stdFileIn1, direc+stdFileIn1+"_pruned")
	removeDuplicateArgSent(direc+stdFileIn2, direc+stdFileIn2+"_pruned")
	removeDuplicateArgSent(direc+stdFileIn3, direc+stdFileIn3+"_pruned")
	removeDuplicateArgSent(direc+stdFileIn4, direc+stdFileIn4+"_pruned")