import numpy as np
import re

def get_entity_pos(arg1, arg2, sent):
	arg1StartOffset = -1
	arg1EndOffset = -1
	arg2StartOffset = -1
	arg2EndOffset = -1
	
	arg1Tok = arg1.split(' ')
	arg2Tok = arg2.split(' ')
	sentTok = sent.split(' ')

	sentLen = len(sentTok)
	arg1Len = len(arg1Tok)
	arg2Len = len(arg2Tok)

	arg1Found = False
	arg2Found = False

	i = 0
	while i < sentLen:
		if arg1Found & arg2Found:
			break
		
		matchLen1 = 0
		nonsenseArgLen1 = 0
		nonsenseSentLen1 = 0
		if arg1Found == False:
			while (matchLen1 + nonsenseArgLen1 < arg1Len) & (i + matchLen1 + nonsenseSentLen1 < sentLen):
				while nonsense_match(arg1Tok[matchLen1 + nonsenseArgLen1])&(matchLen1 + nonsenseArgLen1 < arg1Len-1):
					nonsenseArgLen1 += 1
				while nonsense_match(sentTok[i + matchLen1 + nonsenseSentLen1])&(i + matchLen1 + nonsenseSentLen1 < sentLen-1):
					nonsenseSentLen1 += 1
				if arg_match(arg1Tok[matchLen1 + nonsenseArgLen1], sentTok[i + matchLen1 + nonsenseSentLen1]):
					matchLen1 += 1
					
				else: 
					break
		matchLen2 = 0
		nonsenseArgLen2 = 0
		nonsenseSentLen2 = 0
		if arg2Found == False:
			while (matchLen2 + nonsenseArgLen2 < arg2Len) & (i + matchLen2 + nonsenseSentLen2 < sentLen):
				while nonsense_match(arg2Tok[matchLen2 + nonsenseArgLen2])&(matchLen2 + nonsenseArgLen2 < arg2Len-1):
					nonsenseArgLen2 += 1
				while nonsense_match(sentTok[i + matchLen2 + nonsenseSentLen2])&(i + matchLen2 + nonsenseSentLen2 < sentLen-1):
					nonsenseSentLen2 += 1
				if arg_match(arg2Tok[matchLen2 + nonsenseArgLen2], sentTok[i + matchLen2 + nonsenseSentLen2]):
					matchLen2 += 1
					
				else:
					break
		if (arg1Found == False) & (matchLen1 + nonsenseArgLen1 == arg1Len):
			arg1StartOffset = i
			arg1EndOffset = i + arg1Len
			i = arg1EndOffset
			arg1Found = True
		elif (arg2Found == False) & (matchLen2 + nonsenseArgLen2 == arg2Len):
			arg2StartOffset = i
			arg2EndOffset = i + arg2Len
			i = arg2EndOffset
			arg2Found = True
		else:
			i = i + 1

	if (arg1StartOffset == -1) | (arg1EndOffset == -1):
		print arg1Tok
		print sentTok
	if (arg2StartOffset == -1) | (arg2EndOffset == -1):
		print arg2Tok
		print sentTok

	return arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset

def arg_match(arg, sent_tok):
	if arg == sent_tok:
		return True
	elif re.match(".*[^A-Za-z0-9]*" + arg + "[^A-Za-z0-9]*", sent_tok):
		return True
	elif re.match("[^A-Za-z0-9]*" + arg + "[^A-Za-z0-9]*.*", sent_tok):
		return True
	return False

def nonsense_match(tok):
	if re.match("^[^A-Za-z0-9]+$", tok):
		return True
	elif tok == "":
		return True
	return False


def getDoc(docFile):
	doc = {}
	with open(docFile) as d:
		for row in d:
			parts = row.split('\t')
			docIndex = parts[0]
			docId = parts[1]
			docSent = parts[2].strip('\n')
			doc[docIndex] = [docId, docSent]
	print "Finished documents loading"
	return doc


def getDS(train_DS_pre_feature, DSFile, doc):
	# relation names in freebase definition
	allRel = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death']
	# no new triple in the DS file
	count = 0

	with open(train_DS_pre_feature, 'wb') as fw:
		with open(DSFile) as f2:
			for row2 in f2:
				parts = row2.split('\t')
				relation = parts[9].strip("\n")
				if relation != "NA":

					docIndex = parts[8]
					argId1 = parts[0]
					argId2 = parts[4]
					triple = docIndex + argId1 + argId2

					arg1 = parts[3]
					arg2 = parts[7]

					# if triple not in sent:
					# 	count_repeating += 1

					# sent[triple]["arg1"] = arg1
					# sent[triple]["arg2"] = arg2

					docId = doc[docIndex][0]
					docSent = doc[docIndex][1].strip('\n')

					arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset = get_entity_pos(arg1, arg2, docSent)

					# sent[triple]["docId"] = docId
					# sent[triple]["docSent"] = docSent


					# relationAll = sent[triple]["relation"]
					# features = sent[triple]["features"]
					# featureAll = ""
					# for item in features:
					# 	featureAll += (item+"\t0\t")
					# featureAll = featureAll.strip("\t") + "\n"

					if (arg1StartOffset != -1) & (arg1EndOffset != -1) & (arg2StartOffset != -1) & (arg2EndOffset != -1): 

						line = arg1+"\t"+str(arg1StartOffset)+"\t"+str(arg1EndOffset)+"\t"+ \
								arg2+"\t"+str(arg2StartOffset)+"\t"+str(arg2EndOffset)+"\t"+ \
								docId+"\t"+relation+"\t"+docSent+"\n"
						
						fw.write(line)

						count += 1

						if count % 1000 == 0:
							print count

	print "Finished DS loading"


def getDSTravelTo(train_DS_pre_feature, travel_DS_pre_feature):
	with open(train_DS_pre_feature, 'a') as fw:
		with open(travel_DS_pre_feature) as f:
			count = 0
			for row in f:
				parts = row.split('\t')
				arg1 = parts[0].strip('<').strip()
				arg2 = parts[1]
				docSent = parts[2].strip('\n')

				arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset = get_entity_pos(arg1, arg2, docSent)

				if (arg1StartOffset != -1) & (arg1EndOffset != -1) & (arg2StartOffset != -1) & (arg2EndOffset != -1): 
					line = arg1+"\t"+str(arg1StartOffset)+"\t"+str(arg1EndOffset)+"\t"+ \
							arg2+"\t"+str(arg2StartOffset)+"\t"+str(arg2EndOffset)+"\t"+ \
							"travel"+str(count)+"\t"+"travel"+"\t"+docSent+"\n"

					fw.write(line)

					count += 1

	print "Finished DS loading for travel-to"


def getDSTravelToStandAlone(train_DS_pre_feature_travel, travel_DS_pre_feature):
	with open(train_DS_pre_feature_travel, 'wb') as fw:
		with open(travel_DS_pre_feature) as f:
			count = 0
			for row in f:
				parts = row.split('\t')
				arg1 = parts[0].strip('<').strip()
				arg2 = parts[1]
				docSent = parts[2].strip('\n')

				arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset = get_entity_pos(arg1, arg2, docSent)

				if (arg1StartOffset != -1) & (arg1EndOffset != -1) & (arg2StartOffset != -1) & (arg2EndOffset != -1): 
					line = arg1+"\t"+str(arg1StartOffset)+"\t"+str(arg1EndOffset)+"\t"+ \
							arg2+"\t"+str(arg2StartOffset)+"\t"+str(arg2EndOffset)+"\t"+ \
							"travelDS"+str(count)+"\t"+"travel"+"\t"+docSent+"\n"

					fw.write(line)

					count += 1

	print "Finished DS loading for travel-to"


if __name__ == "__main__":
	docFile = "/projects/WebWare8/Multir/MultirSystem/files/corpus/FullCorpus/sentences.meta"
	DSFile = "/projects/WebWare8/Multir/KBP2014/KBPModel1/DistantSupervision/PERLOC-DS"
	train_DS_pre_feature = "/homes/gws/anglil/test/train_CS_and_DS_five_relations/train_DS_pre_feature"
	travel_DS_pre_feature = "/homes/gws/anglil/test/train_CS_and_DS_five_relations/travel_DS_pre_feature"
	train_DS_pre_feature_travel = "/homes/gws/anglil/test/train_CS_and_DS_five_relations/train_DS_pre_feature_travel"

	# doc = getDoc(docFile)
	# getDS(train_DS_pre_feature, DSFile, doc)
	# getDSTravelTo(train_DS_pre_feature, travel_DS_pre_feature)
	getDSTravelToStandAlone(train_DS_pre_feature_travel, travel_DS_pre_feature)
