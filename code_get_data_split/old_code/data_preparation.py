import json
import couchdb
import csv
import numpy as np
import mentionPosIdentifier

#--------------------------------get gold label from the gold-labeled file -------

def getGoldLabel(tmp):
	# -1: optional
	# 0: no
	# 1: yes
	goldLabel = {
		'r1': "optional",
		'r2': "optional",
		'r3': "optional",
		'r4': "optional",
		'r5': "optional"
	} 
	afterNot = False
	for item in tmp:
		if item == 'not:':
			afterNot = True
		elif item != '':
			if afterNot == False:
				goldLabel[num_to_key[item]] = num_to_relation[item]
			else:
				goldLabel[num_to_key[item]] = num_to_relation[item] + " neg"
	return goldLabel

#------------------------------start importing data ------------------
couch = couchdb.Server()

# the new database
db_new = None
if 'praxeng7_production' not in couch:
	db_new = couch.create('praxeng7_production')
else:
	del couch['praxeng7_production']
	db_new = couch.create('praxeng7_production')
db_new = couch['praxeng7_production']


if "_design/User" not in db_new:
	db_new["_design/User"] = {
	"_id": "_design/User",
  	"language": "javascript",
   	"views": {
       	"by_name": {
           	"map": "function(doc) {if ((doc['type'] == 'User') && (doc['name'] != null)) {emit(doc['name'], 1);}}",
           	"reduce": "_sum"
       	},
       	"by_src": {
           	"map": "function(doc) {if ((doc['type'] == 'User') && (doc['src'] != null)) {emit(doc['src'], 1);}}",
           	"reduce": "_sum"
       	},
       	"all": {
           	"map": "function(doc) {if (doc['type'] == 'User') {emit(doc._id, null);}}"
       	}
	}
	}

if "_design/Annotation" not in db_new: # in production, we do not care about feature 'created_at' any more, so we do not rank annotation documents by that
	db_new["_design/Annotation"] = {
   	"_id": "_design/Annotation",
   	"language": "javascript",
   	"views": {
       	"by_question_id": {
           	"map": "function(doc) {if ((doc['type'] == 'Annotation') && (doc['question_id'] != null)) {emit(doc['question_id'], 1);}}",
           	"reduce": "_sum"
       	},
       	"by_user_id": {
           	"map": "function(doc) {if ((doc['type'] == 'Annotation') && (doc['user_id'] != null)) {emit(doc['user_id'], 1);}}",
           	"reduce": "_sum"
       	},
       	"by_user_id_and_question_id": {
           	"map": "function(doc) {if ((doc['type'] == 'Annotation') && (doc['user_id'] != null) && (doc['question_id'] != null)) {emit([doc['user_id'], doc['question_id']], 1);}}",
           	"reduce": "_sum"
       	},
       	"all": {
           	"map": "function(doc) {if (doc['type'] == 'Annotation') {emit(doc._id, null);}}"
       	}
   	}
	}

if "_design/Question" not in db_new:
	db_new["_design/Question"] = {
   	"_id": "_design/Question",
   	"language": "javascript",
   	"views": {
       	"by_doc_name": {
           	"map": "function(doc) {if ((doc['type'] == 'Question') && (doc['doc_name'] != null)) {emit(doc['doc_name'], 1);}}",
           	"reduce": "_sum"
       	},
       	"by_for_test": {
           	"map": "function(doc) {if ((doc['type'] == 'Question') && (doc['for_test'] != null)) {emit(doc['for_test'], 1);}}",
           	"reduce": "_sum"
       	},
       	"all": {
           	"map": "function(doc) {if (doc['type'] == 'Question') {emit(doc._id, null);}}"
       	}
   	}
	}

if "_design/Document" not in db_new:
	db_new["_design/Document"] = {
   	"_id": "_design/Document",
   	"language": "javascript",
   	"views": {
       	"by_doc_name": {
           	"map": "function(doc) {if ((doc['type'] == 'Document') && (doc['doc_name'] != null)) {emit(doc['doc_name'], 1);}}",
           	"reduce": "_sum"
       	},
       	"all": {
           	"map": "function(doc) {if (doc['type'] == 'Document') {emit(doc._id, null);}}"
       	}
   	}
	}

if "_design/Comment" not in db_new:
	db_new["_design/Comment"] = {
   	"_id": "_design/Comment",
   	"language": "javascript",
   	"views": {
   		"by_updated_at": {
   			"map": "function(doc) {if (doc['type'] == 'Comment') {emit(doc['updated_at'], 1);}}",
   			"reduce": "_sum"
   		},
       	"all": {
           	"map": "function(doc) {if (doc['type'] == 'Comment') {emit(doc._id, null);}}"
       	}
   	}
	}

num_to_key = {
	'0': 'r1',
	'1': 'r2',
	'2': 'r3',
	'3': 'r4',
	'4': 'r5'
}

num_to_relation = {
	'0': "has nationality",
	'1': "was born in",
	'2': "lived in",
	'3': "died in",
	'4': "traveled to"
}





# def checkForTestQuestion(sent_id):
# 	with open('Nov24_answer_key.csv', 'rb') as csvfile:
# 		f = csv.reader(csvfile, delimiter=',')
# 		for row in f:
# 			if sent_id == row[0]:
# 				return '1', getGoldLabel(row)
# 	return '0', {}


# # add documents to the new database
# count = 0
# for row in q_view:
# 	sent_id = row['value']['_id']
# 	docName = row['value']['doc_name']

# 	# upload the documents
# 	doc = list(doc_view[docName])[0]['value']
# 	doc_id = str(count) + "_" + doc["doc_name"] # the real doc id that represents the kbp doc id
# 	if doc_id not in db_new:
# 		db_new[doc_id] = doc

# 	# upload the questions
# 	q = {}
# 	IsTestQuestion, goldLabel = checkForTestQuestion(sent_id)
# 	q['for_test'] = IsTestQuestion
# 	if IsTestQuestion:
# 		q['answers_gold'] = [goldLabel]

# 	q['args'] = row['value']['args']
# 	q['dataset'] = row['value']['dataset']
# 	q['doc_name'] = docName
# 	q['type'] = "Question"
# 	# q['mis_segmented'] = False # whether the name entities are mis-segmented

# 	q_id = 'q_' + doc_id
# 	if q_id not in db_new:
# 		db_new[q_id] = q


#	# 	count += 1



q_num_per_relation = 4000

relation_name = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']
with open('train_DS_shuffled_for_DS', 'wb') as f_DS:
	with open('train_DS_shuffled_for_CS', 'wb') as f_CS:
		with open('train_DS_shuffled', 'rb') as f:
			relation_counter = np.zeros(5)

			for row in f:
				flag_balance_full = True
				for i in range(5):
					if relation_counter[i] != q_num_per_relation: # number of questions uploaded is specified here
						flag_balance_full = False
						break
				if flag_balance_full:
					break

				parts = row.split('\t')
				arg1 = parts[0]
				arg2 = parts[3]
				doc_name = parts[6]
				relation = parts[7]
				sent = parts[11]

				relation_index = relation_name.index(relation)
				
			
				q = {}
				# name every sentence differently by adding something unique to the document name of the sentence
				q_id = 'q_'+str(int(relation_counter[relation_index]))+'_'+doc_name
				q['for_test'] = '0'
				arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset = get_entity_pos(arg1, arg2, sent)
				# print arg1
				# print arg2
				# print sent
				# print arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset

				# the four offsets should not be -1
				if (arg1StartOffset != -1) & (arg1EndOffset != -1) & (arg2StartOffset != -1) & (arg2EndOffset != -1):
					if relation_counter[relation_index] == q_num_per_relation:
						f_DS.write(row)
						continue

					f_CS.write(row)	

					arg1_attr = {'sent_tok_span':[arg1StartOffset, arg1EndOffset], 'mention_text':arg1}
					arg2_attr = {'sent_tok_span':[arg2StartOffset, arg2EndOffset], 'mention_text':arg2}
					q['args'] = [arg1_attr, arg2_attr]
					q['dataset'] = relation
					q['doc_name'] = doc_name
					q['answers_gold'] = [{}]
					q['type'] = 'Question'
					if q_id not in db_new:
						# del db_new[q_id]
						db_new[q_id] = q

					d = {}
					d['doc_name'] = doc_name
					d['text'] = sent
					d['type'] = 'Document'
					if doc_name not in db_new:
						# del db_new[doc_name]
						db_new[doc_name] = d 

					relation_counter[relation_index] += 1

					# print relation_counter




# list([arg1, arg1StartOffset, arg1EndOffset, arg2, arg2StartOffset, arg2EndOffset, sent, doc_name, sent_id])+list(row18)
count = 0
with open('answer_key.csv', 'rb') as csvfile:
	f = csv.reader(csvfile, delimiter=',')
	for row in f:
		
		arg1 = row[0]
		arg1StartOffset = row[1]
		arg1EndOffset = row[2]
		arg2 = row[3]
		arg2StartOffset = row[4]
		arg2EndOffset = row[5]
		doc_name = row[7]
		sent = row[6]

		q_id = 'g_'+str(count)+'_'+doc_name
		q = {}
		q['for_test'] = '1'
		arg1_attr = {'sent_tok_span':[arg1StartOffset, arg1EndOffset], 'mention_text': arg1}
		arg2_attr = {'sent_tok_span':[arg2StartOffset, arg2EndOffset], 'mention_text': arg2}
		q['args'] = [arg1_attr, arg2_attr]
		q['dataset'] = 'answer_key'
		q['doc_name'] = doc_name
		q['answers_gold'] = [getGoldLabel(row[10:16])]
		q['type'] = 'Question'
		if q_id not in db_new:
			# del db_new[q_id]
			db_new[q_id] = q

		d = {}
		d['doc_name'] = doc_name
		d['text'] = sent
		d['type'] = 'Document'
		if doc_name not in db_new: # some gold questions share the same document files with real questions
			# del db_new[doc_name]
			db_new[doc_name] = d 

		count += 1
		# print count