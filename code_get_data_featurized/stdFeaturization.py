# std sentences featurization

# files to featurize:
# data_train_CS/train_CS_MJ_pos_comb
# data_train_CS/train_CS_MJ_neg_comb
# data_test/test_relaxed
# data_test/test_strict

import numpy as np
from mentionPosIdentifier import *
import subprocess
import sys

def computePositionForStdFile(stdFile, stdFileOut):
	with open(stdFileOut, 'wb') as fw:
		with open(stdFile, 'rb') as f:
			for row in f:
				parts = row.split('\t')
				arg1 = parts[0]
				arg2 = parts[3]
				sent = parts[11]
				arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset = get_entity_pos(arg1, arg2, sent)
				if (arg1StartOffset == -1) | (arg1EndOffset == -1) | (arg2StartOffset == -1) | (arg2EndOffset == -1):
					print arg1
					print arg2
					print sent
				else:
					parts2 = list(parts)
					parts2[1] = str(arg1StartOffset)
					parts2[2] = str(arg1EndOffset)
					parts2[4] = str(arg2StartOffset)
					parts2[5] = str(arg2EndOffset)
					fw.write('\t'.join(parts2))

def computeFeatureForStdFile(stdFile, stdFileOut):
	subprocess.call(["sh", "featurizer.sh", stdFile, stdFileOut])

if __name__ == "__main__":
	direc = '/homes/gws/anglil/learner/'

	computePositionForStdFile(direc+sys.argv[1], direc+sys.argv[1]+"_tmp")
	computeFeatureForStdFile(direc+sys.argv[1]+"_tmp", direc+sys.argv[1]+"_new_feature")


