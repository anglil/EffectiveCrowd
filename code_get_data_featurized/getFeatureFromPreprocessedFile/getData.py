import numpy as np


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


def getFeature(featureFile):
	sent = {}

	# count_x = 0
	# count_y = 0
	# the feature file can have more than one relation for an example
	with open(featureFile) as f:
		for row in f:
			parts = row.split('\t')
			relationTmp = parts[3]
			if relationTmp != "NA":

				docIndex = parts[0]
				argId1 = parts[1]
				argId2 = parts[2]
				triple = docIndex + argId1 + argId2

				# get all the features
				featureLen = len(parts) - 4
				features = []
				for i in range(4, 4+featureLen-1):
					features.append(parts[i])
				featureLast = parts[4+featureLen-1]
				featureLast = featureLast.strip("\n")
				features.append(featureLast)
				# get the relation
				relationAll = relationTmp.split("&&")
				
				# if triple not in sent:
				# 	sent[triple] = []
				# else:
				# 	if features != sent[triple][0]["features"]:
				# 		count_x += 1
				# 	if relationAll != sent[triple][0]["relation"]:
				# 		count_y += 1
				# sent[triple].append({"relation": relationAll, "features": features})

				# we only need unique entries, so we ignore those repeating ones
				sent[triple] = {"relation": relationAll, "features": features}

	# print count_x
	# print count_y
	print "Finished feature loading"
	return sent


def getDS(DSFile, doc, sent):
	# relation names in freebase definition
	allRel = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death']
	# no new triple in the DS file
	count = 0
	with open("nationality", "a") as fNationality:
		with open("born", "a") as fBorn:
			with open("lived", "a") as fLived:
				with open("died", "a") as fDied:

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
								docSent = doc[docIndex][1]

								# sent[triple]["docId"] = docId
								# sent[triple]["docSent"] = docSent


								relationAll = sent[triple]["relation"]
								features = sent[triple]["features"]
								featureAll = ""
								for item in features:
									featureAll += (item+"\t0\t")
								featureAll = featureAll.strip("\t") + "\n" 

								for rel in relationAll:
									line = arg1+"\t0\t0\t"+arg2+"\t0\t0\t"+docId+"\t"+rel+"\t0\t0\t0\t"+docSent+"\t"+featureAll
									if rel == allRel[0]:
										fNationality.write(line)
									elif rel == allRel[1]:
										fBorn.write(line)
									elif rel == allRel[2]:
										fLived.write(line)
									else:
										fDied.write(line)
									count += 1

									if count % 1000 == 0:
										print count

	print "Finished DS loading"
			

if __name__ == "__main__":
	docFile = "/projects/WebWare8/Multir/MultirSystem/files/corpus/FullCorpus/sentences.meta"
	featureFile = "/projects/WebWare8/Multir/KBP2014/KBPModel1/FeatureGeneration/PERLOC-FG"
	DSFile = "/projects/WebWare8/Multir/KBP2014/KBPModel1/DistantSupervision/PERLOC-DS"

	doc = getDoc(docFile)
	sent = getFeature(featureFile)
	getDS(DSFile, doc, sent)


