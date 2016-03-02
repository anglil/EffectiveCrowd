import csv
import numpy as np
import couchdb
import subprocess
import os
import sys
import shutil
import math
import operator
import random
from mentionPosIdentifier import *



class turkData:
	# {u_id: {"duration": duration, "time_track":[], "question_track":[], "approved":f/t, "response": {q_id: {updated_time, annotation, isCorrect, isCorrectRe, interval}}}
	approved_worker = {} # id: property
	# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isCorrect, isCorrectRe, interval}}}
	test_question = {} # id: property

	db = []
	d_view = [] # documents
	q_view = [] # questions
	u_view = [] # users
	ann_q_view = []
	ann_u_view = []
	ann_u_time_view = []
	relation_name = ['has nationality', 'was born in', 'lived in', 'died in', 'traveled to']
	dataset_name = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']

	# whether one sentence can have multiple positive relations
	multiPositive = True

	def __init__(self, database_name):
		#---------------- initiate the database and the variables in the memory ---------
		couch = couchdb.Server()
		self.db = couch[database_name]
		self.d_view = self.get_documents()
		self.q_view = self.get_questions()
		self.u_view = self.get_users()
		self.ann_q_view = self.get_annotations_questions()
		self.ann_u_view = self.get_annotations_users()
		self.ann_u_time_view = self.get_annotations_users_and_update_time()

		#---------------- read the data from the database into a worker dictionary and a question dictionary -----------
		self.get_user_info()
		self.get_question_info()

		#---------------- infer true labels from the data via majority voting and EM -----------------
		# self.get_question_majority_vote(-1) # -1, 3, 5, 7
		# self.get_question_EM(0.5, 1, 1, -1) # -1, 3, 5, 7

	def get_questions(self):
		q = '''function(doc) {
			if ((doc.type == 'Question') && (doc._id != null))
				emit(doc._id, [doc.dataset, doc.doc_name, doc.args[0].mention_text, doc.args[1].mention_text, doc.args[0].sent_tok_span, doc.args[1].sent_tok_span, doc.answers_gold, doc.for_test]);
		}'''
		return self.db.query(q)	


	def get_users(self):
		q = '''function(doc) {
			if ((doc.type == 'User') && (doc._id != null))
				emit(doc._id, null);
		}'''
		return self.db.query(q)

	
	def get_documents(self):
		q = '''function(doc) {
			if ((doc['type'] == 'Document') && (doc['doc_name'] != null)) {
				emit(doc['doc_name'], doc['text']);
			}
		}'''
		return self.db.query(q)


	def get_annotations_questions(self):
		q = '''function(doc) {
			if (doc.type == 'Annotation' && doc.question_id != null && doc.user_id != null && doc.response != null)
				emit(doc.question_id, [doc.user_id, doc.response, doc.updated_at]);
		}'''
		return self.db.query(q)


	def get_annotations_users(self):
		q = '''function(doc) {
			if (doc.type == 'Annotation' && doc.question_id != null && doc.user_id != null && doc.response != null)
				emit(doc.user_id, [doc.question_id, doc.response, doc.updated_at]);
		}'''
		return self.db.query(q)

	def get_annotations_users_and_update_time(self):
		q = '''function(doc) {
			if (doc.type == 'Annotation' && doc.question_id != null && doc.user_id != null && doc.response != null)
				emit([doc.user_id, doc.updated_at], doc.question_id);
		}'''
		return self.db.query(q)

	# def get_travel_to_q_id(self):
	# 	q = '''function(doc) {
	# 		if (doc.type == 'Question') && (doc._id != null)
	# 			emit([doc.args[0].mention_text, doc.args[1].mention_text, doc.dataset], doc.doc_name)
	# 	}'''
	# 	return self.db.query(q)



	# # --------------------------- get the triples from CS data before posing to crowdsourcing -------------------------
	
	# # CS triple: "myTurk5/sentences/train_DS_shuffled_for_CS"
	# # test triple: "myTurk5/sentences/test_CS"

	# def getTripleFromStandardData(self, originalFile):
	# 	tripleDict = {}
	# 	count = 0
	# 	with open(originalFile) as f:
	# 		for row in f:
	# 			parts = row.split('\t')
	# 			arg1 = parts[0]
	# 			arg2 = parts[3]
	# 			docId = parts[6]

	# 			triple = arg1 + ' ' + arg2 + ' ' + docId

	# 			# every triple has a unique instance
	# 			tripleDict[triple] = parts
	# 			count += 1

	# 	print "# of triples loaded:", count
	# 	return tripleDict


	# # -------------------------- get the CS data (prepared for MultiR) with multi-positive annotations into singleton bags for each example -----------------------------------------
	# # aggregation="majority"or"EM"
	# def writeCSDataToFile(self, aggregation, CSTriple):
	# 	# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isApproved, isCorrect, isCorrectRe, interval}}}
	# 	# relation_name = ['has nationality', 'was born in', 'lived in', 'died in', 'traveled to']
	# 	# relation_name_neg = ['has nationality neg', 'was born in neg', 'lived in neg', 'died in neg', 'traveled to neg']
	# 	dataset_name = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']

	# 	count = 0
	# 	count2 = 0
	# 	with open('train_CS_MJ_neg2', 'wb') as fNeg:
	# 		with open('train_CS_MJ_pos2', 'wb') as f:
	# 			for q_id in self.test_question.keys():
	# 				if self.test_question[q_id]['for_test'] == False:
	# 					# majority or EM, 5 dimension vector
	# 					ann = self.test_question[q_id][aggregation] 
	# 					arg1 = list(self.q_view[q_id])[0]['value'][2]
	# 					arg2 = list(self.q_view[q_id])[0]['value'][3]
	# 					tmp = q_id.split('_')
	# 					docId = '_'.join(tmp[2:len(tmp)])

	# 					triple = arg1 + ' ' + arg2 + ' ' + docId	

	# 					# iterate through 5 relations
	# 					neg = 0
	# 					for i in range(5):
	# 						# only collect positive relations
	# 						if (ann[i] != 'NA') & ('neg' not in ann[i]):
	# 							instance = list(CSTriple[triple])
	# 							instance[7] = dataset_name[i] # use freebase names
	# 							count += 1

	# 							f.write('\t'.join(instance))
	# 						elif (ann[i] != 'NA') & ('neg' in ann[i]):
	# 							neg += 1

	# 					# when every relation is negative
	# 					if neg == 5:
	# 						instance = list(CSTriple[triple])
	# 						instance[7] = 'NA'
	# 						count2 += 1

	# 						fNeg.write('\t'.join(instance))

	# 	print "amount of positive examples overall:", count
	# 	print "amount of negative examples overall:", count2


	# --------------------- get the CS data following Gabor's identification convention -----
	def writeCSDataToFileGabor(self, aggregation, featureDict, stdFileRes):
		reload(sys)
		sys.setdefaultencoding("utf-8")

		relName = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']
		# h = HTMLParser.HTMLParser()

		with open(stdFileRes, 'wb') as fw:
			for q_id in self.test_question.keys():
				# not test questions, but real questions
				if self.test_question[q_id]['for_test'] == False:
					# majority or EM, 5 dimension vector
					ann = self.test_question[q_id][aggregation]

					docName = list(self.q_view[q_id])[0]['value'][1]
					docText = list(self.d_view[docName])[0]['value']
					# docText = h.unescape(docText)

					arg1 = list(self.q_view[q_id])[0]['value'][2]
					arg2 = list(self.q_view[q_id])[0]['value'][3]
					arg1Span = list(self.q_view[q_id])[0]['value'][4]
					arg2Span = list(self.q_view[q_id])[0]['value'][5]
					arg1StartOffset = arg1Span[0]
					arg1EndOffset = arg1Span[1]
					arg2StartOffset = arg2Span[0]
					arg2EndOffset = arg2Span[1]
					tmp = q_id.split('_')
					docName = '_'.join(tmp[2:len(tmp)])

					# question identifier
					line = docName+':'+arg1StartOffset+"-"+arg1EndOffset+':'+arg2StartOffset+"-"+arg2EndOffset

					# construct the feature vector
					featureVector = featureDict[line]
					featureVector = '\t0\t'.join(featureVector)
					featureVector += '\t0'

					# iterate over 5 relations
					negCtr = 0
					for i in range(5):
						# only collect positive relations
						if (ann[i] != 'NA') & ('neg' not in ann[i]):
							row = arg1+'\t'+arg1StartOffset+'\t'+arg1EndOffset+'\t' \
								+arg2+'\t'+arg2StartOffset+'\t'+arg2EndOffset+'\t' \
								+docName+'\t'+relName[i]+'\t0\t0\t0\t'+docText+'\t' \
								+featureVector+'\n'
							fw.write(row)
						elif (ann[i] != 'NA') & ('neg' in ann[i]):
							negCtr += 1
					# when every sentence is negative
					if negCtr == 5:
						row = arg1+'\t'+arg1StartOffset+'\t'+arg1EndOffset+'\t' \
							+arg2+'\t'+arg2StartOffset+'\t'+arg2EndOffset+'\t' \
							+docName+'\t'+'NA'+'\t0\t0\t0\t'+docText+'\t' \
							+featureVector+'\n'
						fw.write(row)


	# --------------------------- write crowd data to file with raw worker votes ------------------------------------
	def writeCSDataToFileWithVotes(self, fileRes):
		reload(sys)
		sys.setdefaultencoding("utf-8")
		relName = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']
		with open(fileRes, 'wb') as fw:
			for q_id in self.test_question.keys():
				docName = list(self.q_view[q_id])[0]['value'][1]
				docText = list(self.d_view[docName])[0]['value']
				arg1 = list(self.q_view[q_id])[0]['value'][2]
				arg2 = list(self.q_view[q_id])[0]['value'][3]
				arg1Span = list(self.q_view[q_id])[0]['value'][4]
				arg2Span = list(self.q_view[q_id])[0]['value'][5]
				arg1StartOffset = arg1Span[0]
				arg1EndOffset = arg1Span[1]
				arg2StartOffset = arg2Span[0]
				arg2EndOffset = arg2Span[1]
				tmp = q_id.split('_')
				docName = '_'.join(tmp[2:len(tmp)])
				# question id
				# line = docName+":"+str(arg1StartOffset)+"-"+str(arg1EndOffset)+":"+str(arg2StartOffset)+"-"+str(arg2EndOffset)
				# construct the feature vector 
				
				# featureVector = featureDict[line]
				# featureVector = '\t0\t'.join(featureVector)
				# featureVector = '\t0'
				
				# all the worker votes
				if "response" in self.test_question[q_id]:
					ann = self.test_question[q_id]["response"]
					annVector = []
					for u_id in ann.keys():
						annList = ",".join(ann[u_id]["annotation"])
						annVector.append(u_id)
						annVector.append(annList)
					annVector = '\t'.join(annVector)
					# write row
					row = str(arg1)+'\t'+str(arg1StartOffset)+'\t'+str(arg1EndOffset)+'\t'+str(arg2)+'\t'+str(arg2StartOffset)+'\t'+str(arg2EndOffset)+'\t'+str(docName)+'\t'+str(annVector)+'\t'+str(docText)+'\n'
						
					fw.write(row)


				
	

	# # ------------------------ get the CS data by multi-positive relations and being positive / negative -----------------
	# # aggregation="majority"or"EM"
	# def writeCSDataToFileByRelation(self, aggregation, CSTriple):
	# 	# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isApproved, isCorrect, isCorrectRe, interval}}}
	# 	relationName = ['nationality', 'born', 'lived', 'died', 'travel']
	# 	datasetName = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']

	# 	posCount = np.zeros(5)
	# 	negCount = np.zeros(5)

	# 	for q_id in self.test_question.keys():
	# 		if self.test_question[q_id]['for_test'] == False:
	# 			# majority or EM, 5 dimension vector
	# 			ann = self.test_question[q_id][aggregation]
	# 			arg1 = list(self.q_view[q_id])[0]['value'][2]
	# 			arg2 = list(self.q_view[q_id])[0]['value'][3]
	# 			tmp = q_id.split('_')
	# 			docId = '_'.join(tmp[2:len(tmp)])

	# 			triple = arg1 + ' ' + arg2 + ' ' + docId

	# 			# 5 dimensions
	# 			# collect both positive and negative relations
	# 			for i in range(5):
	# 				# a positive example
	# 				if (ann[i] != 'NA') & ('neg' not in ann[i]):
	# 					instance = list(CSTriple[triple])
	# 					instance[7] = datasetName[i]

	# 					posCount[i] += 1
	# 					fileName = "train_CS_"+relationName[i]+"_pos2"

	# 					f = open(fileName, "a")
	# 					f.write('\t'.join(instance))
	# 					f.close()
	# 				# a negative example
	# 				elif (ann[i] != 'NA') & ('neg' in ann[i]):
	# 					instance = list(CSTriple[triple])
	# 					instance[7] = 'NA'

	# 					negCount[i] += 1
	# 					fileName = "train_CS_"+relationName[i]+"_neg2"

	# 					f = open(fileName, "a")
	# 					f.write('\t'.join(instance))
	# 					f.close()
	# 	print "amount of positive examples by relation:", posCount
	# 	print "amount of negative examples by relation:", negCount




	# dictionary to list
	def ann_gold_format(self, ann_gold):
		ann = []
		ann.append(ann_gold['r1'])
		ann.append(ann_gold['r2'])
		ann.append(ann_gold['r3'])
		ann.append(ann_gold['r4'])
		ann.append(ann_gold['r5'])
		return ann

	
	# -------------------- highlight text ------------------------
	def highlight_text(self, doc_text, per_span, loc_span):
		res = doc_text.split(' ')
		if per_span[1] < loc_span[0]:
			res.insert(per_span[0], '{{')
			res.insert(per_span[1]+1, '}}')
			res.insert(loc_span[0]+2, '{{')
			res.insert(loc_span[1]+3, '}}')
		else:
			res.insert(loc_span[0], '{{')
			res.insert(loc_span[1]+1, '}}')
			res.insert(per_span[0]+2, '{{')
			res.insert(per_span[1]+3, '}}')
		return u' '.join(res).encode('utf-8').strip()



	# ---------------------- get a dictionary that maps questions to features --------------
	def get_feature_by_question(self, stdFile):
		featureDict = {}
		# h = HTMLParser.HTMLParser()
		with open(stdFile) as f:
			for row in f:
				parts = row.split('\t')
				arg1StartOffset = parts[1]
				arg1EndOffset = parts[2]
				arg2StartOffset = parts[4]
				arg2EndOffset = parts[5]
				docName = parts[6]

				featureVector = []
				featureWalker = 12
				while featureWalker < len(parts):
					featureVector.append(parts[featureWalker])
					featureWalker += 2

				line = docName+":"+arg1StartOffset+'-'+arg1EndOffset+":"+arg2StartOffset+'-'+arg2EndOffset

				featureDict[line] = featureVector
		return featureDict


	# --------------------- get a dictionary that maps questions to relation labels -----------
	def get_rel_by_question(self, stdFile):
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

				line = docName+":"+arg1StartOffset+'-'+arg1EndOffset+":"+arg2StartOffset+'-'+arg2EndOffset

				relDict[line] = rel
		return relDict


	# ----------------------- std file for CS training data --------------------
	def get_question_agreement_heatmap(self, stdFile):
		# {q_id: {'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {annotation, isApproved}}}
		relationDict = self.get_rel_by_question(stdFile)

		relName = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']
		mat = np.zeros([5,5])

		# questions that are answered by workers
		for q_id in self.test_question:
			if self.test_question[q_id]['for_test'] == False:
				q_mj_v = self.test_question[q_id]['majority'] # majority_vote = ['NA']*5
				q_docName = list(self.q_view[q_id])[0]['value'][1]
				q_arg1 = list(self.q_view[q_id])[0]['value'][2]
				q_arg2 = list(self.q_view[q_id])[0]['value'][3]
				q_arg1Span = list(self.q_view[q_id])[0]['value'][4]
				q_arg2Span = list(self.q_view[q_id])[0]['value'][5]
				q_sentKey = q_docName+':'+q_arg1Span[0]+'-'+q_arg1Span[1]+':'+q_arg2Span[0]+'-'+q_arg2Span[1]
				
				q_rel = relationDict[q_sentKey] # real name (from Gabor's label)
				q_relInd = relName.index(q_rel)
				for i in range(5):
					# alias (from worker label's majority voting)
					if ('neg' not in q_mj_v[i]) & (q_mj_v[i] != 'NA'):
						mat[q_relInd][i] += 1

		return mat



	# ---------------------- get majority vote for every sentence ---------------------
	def get_question_majority_vote(self, thresholdVoteNum):
		# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isApproved, isCorrect, isCorrectRe, interval}}}
		count = 0
		for q_id in self.test_question.keys():
			# only do majority voting for real questions, because real questions are training data, whereas gold questions are test data
			if self.test_question[q_id]['for_test'] == False:
				vote = []
				vote_num = 0
				# response domain only exists in questions that got answers from approved workers
				if 'response' in self.test_question[q_id]:
					vote_max = len(self.test_question[q_id]['response'])
					
					if thresholdVoteNum != -1:
						vote_index = random.sample(range(0,vote_max), thresholdVoteNum)
					else:
						vote_index = range(vote_max)

					if vote_max >= 2: # otherwise one cannot do majority vote
						u_count = 0
						for u_id in self.test_question[q_id]['response'].keys():
							ann = self.test_question[q_id]['response'][u_id]['annotation']
							if u_count in vote_index:
								vote.append(ann)
								vote_num += 1
							u_count += 1
							

						majority_vote = self.process_vote_majority(vote)
						self.test_question[q_id]["majority"] = majority_vote

						count += 1
					else:
						self.test_question[q_id]['majority'] = None
				else:
					self.test_question[q_id]['majority'] = None
		print count, 'questions got a majority vote'



	# --------------- per relation majority vote that include positive, negative and NA------------
	def process_vote_majority(self, vote):
		relation_name = ['has nationality', 'was born in', 'lived in', 'died in', 'traveled to']
		relation_name_neg = ['has nationality neg', 'was born in neg', 'lived in neg', 'died in neg', 'traveled to neg']

		# votes between the two thresholds are regarded as NA
		majority_vote = ['NA']*5

		# upper row: positive count
		# lower row: negative count
		relation_counter = np.zeros([2, 5])
		for i in range(len(vote)):
			for j in range(5):
				if vote[i][j] == relation_name[j]:
					relation_counter[0][j] += 1
				elif vote[i][j] == relation_name_neg[j]:
					relation_counter[1][j] += 1

		# allow only one positive
		if self.multiPositive == False:
			ind = relation_counter[0].tolist().index(max(relation_counter[0])) # the most voted positive relation is viewed as the majority vote
			majority_vote[ind] = relation_name[ind]
		# allow more than one positives
		else:
			for j in range(5):
				# the threshold can be adjusted (0.5 corresponds to the original majority voting)
				if relation_counter[0][j]*1.0/(relation_counter[0][j]+relation_counter[1][j]) > 0.75:
					majority_vote[j] = relation_name[j]
				elif relation_counter[1][j]*1.0/(relation_counter[0][j]+relation_counter[1][j]) > 0.75:
					majority_vote[j] = relation_name_neg[j]
		return majority_vote


	#--------------------------- get EM labels for every question ----------------------
	def get_question_EM(self, z_param, a_param, b_param, thresholdVoteNum):
		# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isApproved, isCorrect, isCorrectRe, interval}}}
		count = 0
		for q_id in self.test_question.keys():
			if 'index' not in self.test_question[q_id]:
				self.test_question[q_id]['index'] = count
			count += 1
		#################################################


		data_posteriors = np.zeros(5)
		for current_index in range(5):
			q = []
			u = []
			with open('EMdata/labelMAT' + str(current_index) + '.txt', 'w') as f:
			 	for q_id in self.test_question.keys():
			 		q_index = self.test_question[q_id]['index']

			 		vote_max = len(self.test_question[q_id]['response'])
					if thresholdVoteNum != -1:
						vote_index = random.sample(range(0,vote_max), thresholdVoteNum)
					else:
						vote_index = range(vote_max)
					u_count = 0
			 		for u_id in self.test_question[q_id]['response'].keys():
			 			ann = self.test_question[q_id]['response'][u_id]['annotation'] # annotations
			 			if u_count in vote_index:			
				 			index_positive = 0
				 			if 'neg' not in ann[current_index]:
				 				index_positive = 1

				 			f.write(str(q_index))
							f.write(' ')
							f.write(u_id)
							f.write(' ')
							f.write(str(index_positive))
							f.write('\n')

							if q_index not in q:
								q.append(q_index)
							if u_id not in u:
								u.append(u_id)
						u_count += 1

			q_len = len(q)
			u_len = len(u)

			z_prior = z_param*np.ones(q_len)
			a_prior = a_param*np.ones(u_len)
			b_prior = b_param*np.ones(q_len)

			with open('EMdata/z_prior' + str(current_index) + '.txt', 'w') as fz:
				for i in z_prior:
					fz.write(str(z_prior[i]))
					fz.write('\n')
			with open('EMdata/a_prior' + str(current_index) + '.txt', 'w') as fa:
				for i in a_prior:
					fa.write(str(a_prior[i]))
					fa.write('\n')
			with open('EMdata/b_prior' + str(current_index) + '.txt', 'w') as fb:
				for i in b_prior:
					fb.write(str(b_prior[i]))
					fb.write('\n')

			# pass current_index to the program that runs EM
			with open('EMdata/current_index.txt', 'w') as fi:
				fi.write(str(current_index))

			#################################################
			# call the matlab program
			subprocess.call("./callEM.sh", shell=True)
			#print self.relation_name[current_index], 'done!'
			#################################################

			with open('EMdata/index_inferred' + str(current_index) + '.txt', 'r') as f0:
				for row in f0:
					line = row.split('\t')
					q_index = int(line[0]) # question id in numerical form
					index_positive = np.float64(line[1]) # posterior probability
					
					#tmp = index_positive
					#if tmp == 0:
					#	tmp = 0.000001
					#z_posteriors[current_index] = z_posteriors[current_index] + np.log10(tmp)					

					# get q_id by its numerical form
					q_id = 0
					for q_id_tmp in self.test_question.keys():
						if self.test_question[q_id_tmp]['index'] == q_index:
							q_id = q_id_tmp

					if 'EMlist' not in self.test_question[q_id]:
						self.test_question[q_id]['EMlist'] = []
					self.test_question[q_id]['EMlist'].append(index_positive)
					
					# computing the product of all z posteriors
					if (len(self.test_question[q_id]['EMlist'])-1) != current_index:
						raise Exception('index not correct!')


			u_a = {}
			with open('EMdata/a_inferred' + str(current_index) + '.txt', 'r') as f1:
				for row in f1:
					line = row.split('\t')
					u_id = line[0] # string
					alpha = np.float64(line[1])
					u_a[u_id] = alpha

			# collect the posterior user accuracies
			q_b = {}
			with open('EMdata/b_inferred' + str(current_index) + '.txt', 'r') as f2:
				for row in f2:
					line = row.split('\t')
					q_index = int(line[0])
					beta = np.float64(line[1])
					q_b[q_index] = beta

			for q_id in self.test_question.keys():
				q_index = self.test_question[q_id]['index']
				for u_id in self.test_question[q_id]['response'].keys():
					beta = 1.0/q_b[q_index]
					alpha = u_a[u_id]
					data_posteriors[current_index] += np.log(1/(1+math.exp(-alpha*beta)))

		relation_name = ['has nationality', 'was born in', 'lived in', 'died in', 'traveled to']
		relation_name_neg = ['has nationality neg', 'was born in neg', 'lived in neg', 'died in neg', 'traveled to neg']
		
		for q_id in self.test_question.keys():
			tmp_probability = self.test_question[q_id]['EMlist'] 
			ann_EM = ['NA']*5 # initialized as NA

			# allow only one positive
			if self.multiPositive == False:
				most_probable_relation_index = -1
				if max(tmp_probability) > 0.8: # a parameter that needs to be tuned
					most_probable_relation_index = tmp_probability.index(max(tmp_probability))
				if most_probable_relation_index != -1:
					ann_EM[most_probable_relation_index] = relation_name[most_probable_relation_index]
				self.test_question[q_id]['EM'] = ann_EM
			# allow more than one positives
			else:
				for i in range(len(tmp_probability)):
					if tmp_probability[i] > 0.75:
						ann_EM[i] = relation_name[i]
					elif tmp_probability[i] < 0.25:
						ann_EM[i] = relation_name_neg[i]
				self.test_question[q_id]['EM'] = ann_EM

		return data_posteriors





	def checkAnswer(self, ann, ann_gold):
		num_to_relation = ['r1', 'r2', 'r3', 'r4', 'r5']
		for i in range(5):
			if ann_gold[num_to_relation[i]] != 'optional':
				if ann_gold[num_to_relation[i]] != ann[i]:
					return False
		return True

	def checkAnswerPerRe(self, ann, ann_gold):
		correctness = [True, True, True, True, True]
		num_to_relation = ['r1', 'r2', 'r3', 'r4', 'r5']
		for i in range(5):
			if ann_gold[num_to_relation[i]] != 'optional':
				if ann_gold[num_to_relation[i]] != ann[i]:
					correctness[i] = False
		return correctness

	# def time_process(self, t):
	# 	tmp = t.split('T')[1]
	# 	tmp = tmp.split('.')[0]
	# 	hour = tmp.split(':')[0]
	# 	minu = tmp.split(':')[1]
	# 	sec = tmp.split(':')[2]
	# 	return [hour, minu, sec], int(hour)*60+int(minu)+int(sec)/60.0

	# def laterThan(self, time1, time2):
	# 	if time1[0]>time2[0]:
	# 		return True
	# 	elif time1[0] == time2[0]:
	# 		if time1[1]>time2[1]:
	# 			return True
	# 		elif time1[1] == time2[1]:
	# 			if time1[2]>time2[2]:
	# 				return True
	# 	return False


	# count only those that have made annotations
	# include both approved workers and disapproved workers
	# {u_id: {"duration": duration, "time_track":[], "question_track":[], "approved":f/t, "response": {q_id: {updated_time, annotation, isCorrect, isCorrectRe, interval}}}
	def get_user_info(self):
		for row in self.ann_u_view:
			u_id = row['key']
			if u_id not in self.approved_worker.keys():
				self.approved_worker[u_id] = {}
				self.approved_worker[u_id]['response'] = {}
				self.approved_worker[u_id]['response_made'] = 1
			else:
				self.approved_worker[u_id]['response_made'] += 1
			q_id = row['value'][0]
			response = row['value'][1]
			updated_time = row['value'][2]
			self.approved_worker[u_id]['response'][q_id] = {}
			self.approved_worker[u_id]['response'][q_id]['updated_time'] = updated_time
			self.approved_worker[u_id]['response'][q_id]['annotation'] = response

			ann_gold = list(self.q_view[q_id])[0]['value'][6][0] # answers_gold

			# annotations on gold questions have two more attributes, isCorrect and isCorrectRe
			if len(ann_gold) != 0:
				if response != []: # An annotation entry is created at the time when the worker gets a question
					self.approved_worker[u_id]['response'][q_id]['isCorrect'] = self.checkAnswer(response, ann_gold)
					self.approved_worker[u_id]['response'][q_id]['isCorrectRe'] = self.checkAnswerPerRe(response, ann_gold)

		count_approved = 0
		count_disapproved = 0
		for u_id in self.approved_worker.keys():
			# annotations less than 20 imply that the worker has been disapproved
			if self.approved_worker[u_id]['response_made'] < 20:
				self.approved_worker[u_id]['approved'] = False
				# print 'annotations made by disapproved worker', u_id, ':', self.approved_worker[u_id]['response_made']
				count_disapproved += 1
			else:
				self.approved_worker[u_id]['approved'] = True
				# print 'annotations made by approved worker', u_id, ':', self.approved_worker[u_id]['response_made']
				count_approved += 1

				count_correct = 0
				count_gold = 0
				for q_id in self.approved_worker[u_id]['response'].keys():
					if 'isCorrect' in self.approved_worker[u_id]['response'][q_id].keys():
						count_gold += 1
						if self.approved_worker[u_id]['response'][q_id]['isCorrect']:
							count_correct += 1
				# print 'accuracy:', count_correct, count_gold, count_correct*1.0/count_gold

		print '# of approved workers:', count_approved
		print '# of disapproved workers:', count_disapproved


	# only keep questions that are answered by approved workers 
	# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isCorrect, isCorrectRe, interval}}}
	def get_question_info(self):
		# (doc._id, [doc.dataset, doc.doc_name, doc.args[0].mention_text, doc.args[1].mention_text, doc.args[0].sent_tok_span, doc.args[1].sent_tok_span, doc.answers_gold, doc.for_test])
		count_q = 0
		for row in self.q_view:
			q_id = row['key']
			if q_id not in self.test_question.keys():
				self.test_question[q_id] = {}
				for_test = row['value'][7]
				if for_test == "0":
					self.test_question[q_id]['for_test'] = False
				else:
					self.test_question[q_id]['for_test'] = True
					self.test_question[q_id]['gold'] = row['value'][6][0]

				count_q += 1

			# (doc.question_id, [doc.user_id, doc.response, doc.updated_at])
			ann_q = list(self.ann_q_view[q_id])
			for ann in ann_q:
				u_id = ann['value'][0]
				if self.approved_worker[u_id]['approved'] == True:
					if 'response' not in self.test_question[q_id]:
						self.test_question[q_id]['response_made'] = 1
						self.test_question[q_id]['response'] = {}
					else:
						self.test_question[q_id]['response_made'] += 1

					if q_id in self.approved_worker[u_id]['response']:
						self.test_question[q_id]['response'][u_id] = {}	
						self.test_question[q_id]['response'][u_id]['update_time'] = self.approved_worker[u_id]['response'][q_id]['updated_time']
						self.test_question[q_id]['response'][u_id]['annotation'] = self.approved_worker[u_id]['response'][q_id]['annotation']

						if self.test_question[q_id]['for_test'] == True:
							self.test_question[q_id]['response'][u_id]['isCorrect'] = self.approved_worker[u_id]['response'][q_id]['isCorrect']
							self.test_question[q_id]['response'][u_id]['isCorrectRe'] = self.approved_worker[u_id]['response'][q_id]['isCorrectRe']
					else:
						print u_id

		print 'amount of questions:', count_q


	# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isApproved, isCorrect, isCorrectRe, interval}}}
	def get_question_agreement(self):
		agreement_hist = []
		agreement_hist_re = [[], [], [], [], []]
		agreement_hist_re_pos = [[], [], [], [], []]
		agreement_hist_re_neg = [[], [], [], [], []]
		# pos_examples = np.zeros(5)
		for q_id in self.test_question.keys():	
			if self.test_question[q_id]['for_test'] == False: # real questions
				agreement = {} # key: ann, value: times
				pos = np.zeros(5)
				neg = np.zeros(5)
				for u_id in self.test_question[q_id]['response'].keys():
					ann = self.test_question[q_id]['response'][u_id]['annotation'] # must be approved already
					
					for i in range(5):
						if 'neg' in ann[i]:
							neg[i] += 1
						else:
							pos[i] += 1

					ann = ' '.join(ann)
					if ann not in agreement.keys():
						agreement[ann] = 1
					else:
						agreement[ann] += 1
				agreement_hist.append(max(agreement.values())*1.0/self.test_question[q_id]['response_made'])
				for i in range(5):
					# pos_examples[i] += pos[i]
					agreement_hist_re[i].append(max(pos[i], neg[i])*1.0/self.test_question[q_id]['response_made'])
					if pos[i] >= neg[i]:
						agreement_hist_re_pos[i].append(pos[i]*1.0/self.test_question[q_id]['response_made'])
					else:
						agreement_hist_re_neg[i].append(neg[i]*1.0/self.test_question[q_id]['response_made'])

		return agreement_hist, agreement_hist_re, agreement_hist_re_pos, agreement_hist_re_neg#, pos_examples

	def get_question_agreement_2(self):
		numerator = 0
		denominator = 0
		numerator_re_pos = np.zeros(5)
		numerator_re_neg = np.zeros(5)
		for q_id in self.test_question.keys():
			if self.test_question[q_id]['for_test'] == False:
				denominator += 1
				vote_index = random.sample(range(0,self.test_question[q_id]['response_made']), 2)
				count_u = 0
				count = 0
				votes = ['', '']
				votes_re = [['', '', '', '', ''],['', '', '', '', '']]
				for u_id in self.test_question[q_id]['response'].keys():
					if count_u in vote_index:
						ann = self.test_question[q_id]['response'][u_id]['annotation'] # must be approved already
						ann_tmp = list(ann)
						ann = ' '.join(ann)
						votes[count] = str(ann)
						votes_re[count] = ann_tmp
						count += 1
					count_u += 1
				# print 'votes', votes
				if votes[0] == votes[1]:
					numerator += 1
				# print 'votes_re', votes_re
				for i in range(5):
					if votes_re[0][i] == votes_re[1][i]:
						if 'neg' in votes_re[0][i]:
							numerator_re_neg[i] += 1
						else:
							numerator_re_pos[i] += 1
		return numerator*1.0/denominator, numerator_re_pos*1.0/denominator, numerator_re_neg*1.0/denominator

	# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isApproved, isCorrect, isCorrectRe, interval}}}
	def get_question_pos_example(self):
		pos_examples = np.zeros(5)
		for q_id in self.test_question.keys():
			if self.test_question[q_id]['for_test'] == False:
				mj = self.test_question[q_id]['majority']
				for i in range(5):
					if 'neg' not in mj[i]:
						pos_examples[i] += 1
		return pos_examples


	# ------------------------ get the agreement percentages for the 5000 crowdsourcing sentences----
	def get_sample_question_to_hand_label(self):
		with open('raw_data/answer_key_color_2.csv', 'wb') as csvfile:
			f = csv.writer(csvfile, delimiter='\t')

			for q_id in self.test_question.keys():
				# training data
				if self.test_question[q_id]['for_test'] == False:
					# the sentence that has been selected
					# if q_count in q_index:
					doc_name = list(self.q_view[q_id])[0]['value'][1]
					doc_text = list(self.d_view[doc_name])[0]['value']
					per_span = list(self.q_view[q_id])[0]['value'][4]
					loc_span = list(self.q_view[q_id])[0]['value'][5]
					highlighted_text = self.highlight_text(doc_text, per_span, loc_span)

					pos_percent = np.zeros(5)
					for u_id in self.test_question[q_id]['response'].keys():
						# count annotations from approved workers
						if self.approved_worker[u_id]['approved'] == True:
							ann = self.test_question[q_id]['response'][u_id]['annotation']
							for i in range(5):
								if 'neg' not in ann[i]:
									pos_percent[i] += 1
					pos_percent = pos_percent*1.0/self.test_question[q_id]['response_made']

					# add a line to the file by every sentence							
					f.writerow([highlighted_text]+list(pos_percent))
					# q_count += 1	
				
	# ------------------------ get the agreement percentages for the 25k crowdsourcing sentences----
	def get_sample_question_to_hand_label_2(self):
		with open('../data_train_CS/5k_training.txt', 'wb') as fw:
			for q_id in self.test_question.keys():
				if self.test_question[q_id]['for_test'] == False:
					doc_name = list(self.q_view[q_id])[0]['value'][1]
					doc_text = list(self.d_view[doc_name])[0]['value']
					arg1 = list(self.q_view[q_id])[0]['value'][2]
					arg2 = list(self.q_view[q_id])[0]['value'][3]
					arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset=get_entity_pos(arg1, arg2, doc_text)
					# get rid of unidentified arguments
					if (arg1StartOffset != -1) and (arg1EndOffset != -1) and (arg2StartOffset != -1) and (arg2EndOffset != -1):
						highlighted_text = self.highlight_text(doc_text, [arg1StartOffset, arg1EndOffset], [arg2StartOffset, arg2EndOffset])

						pos_percent = np.zeros(5)
						for u_id in self.test_question[q_id]['response'].keys():
							# count annotations from approved workers
							if self.approved_worker[u_id]['approved'] == True:
								ann = self.test_question[q_id]['response'][u_id]['annotation']
								for i in range(5):
									if 'neg' not in ann[i]:
										pos_percent[i] += 1
						pos_percent = pos_percent*1.0/self.test_question[q_id]['response_made']

						tmp = str(arg1)+'\t'+str(arg2)+'\t'+str(highlighted_text)+'\t'+str('\t'.join(map(str, pos_percent)))+'\n'
						fw.write(tmp)


	# --------------------remove a worker's information from the database--------------	
	def remove_worker_info(self, u_id, removeWorkerEntry):
		if removeWorkerEntry:
			try:
				# delete the user profile
				del self.db[u_id]
				print "worker %s's user information deleted!" % u_id
			except:
				print "worker %s's user information does not exist!" % u_id
		try:
			# delete the user's annotations
			items = list(self.ann_u_view[u_id])
			for item in items:
				del self.db[item['id']]
			print "worker %s's annotation information deleted!" % u_id
		except:
			print "worker %s's annotation information does not exist!" % u_id
			


	#-----------------delete information about disapproved workers from the database----
	# never run this when there are ongoing annotation processes
	def remove_disapproved_worker_info(self):
		for u_id in self.approved_worker.keys():
			if self.approved_worker[u_id]['approved'] == False:
				self.remove_worker_info(u_id, True)
		print "Information about disapproved workers is removed!"


	#----------------delete information about workers that have not made any annotation---
	# never run this when there are ongoing annotation processes
	def remove_empty_worker_info(self):
		for row in self.u_view:
			u_id = row['key']
			if u_id not in self.approved_worker.keys():
				try:
					# delete the user profile
					del self.db[u_id]
				except:
					print "worker %s's user information does not exist!" % u_id
		print "Entries to empty workers are removed!"
		

	# --------------delete all empty annotation caused by previous software bugs------
	def remove_empty_annotation(self):
		count = 0
		for u_id in self.approved_worker.keys():
			anns = list(self.ann_u_view[u_id])
			for ann in anns:
				if ann['value'][1] == []:
					del self.db[ann['id']]
					print 'an empty annotation deleted!'

	# -------------- delete all users and annotations ----------------------------
	def remove_all_worker_and_annotation(self):
		for u_id in self.approved_worker.keys():
			anns = list(self.ann_u_view[u_id])
			for ann in anns:
				del self.db[ann['id']]
		for row in self.u_view:
			u_id = row['key']
			try:
				del self.db[u_id]
			except:
				print "worker %s's user information does not exist!" % u_id
		print "Worker and annotation information is deleted!"






