import json
import couchdb
import csv
import numpy as np
import sys


# -------------- importing data ----------------


def setupDB(dbName):
	couch = couchdb.Server()
	# the new database
	db_new = None
	if dbName not in couch:
		db_new = couch.create(dbName)
	else:
		del couch[dbName]
		db_new = couch.create(dbName)
	db_new = couch[dbName]

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
	return db_new



def uploadStdFileCS(stdFile, db_new):
	relName = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']
	with open(stdFile) as f:
		relCtr = np.zeros(5)

		for row in f:
			parts = row.split('\t')
			arg1 = parts[0]
			arg1StartOffset = parts[1]
			arg1EndOffset = parts[2]
			arg2 = parts[3]
			arg2StartOffset = parts[4]
			arg2EndOffset = parts[5]
			docName = parts[6]
			relation = parts[7]
			sent = parts[11]

			relInd = relName.index(relation)

			# ----------------- questions ----------------------
			q = {}
			q_id = 'q_'+str(int(relCtr[relInd]))+'_'+docName
			q['for_test'] = '0'
			arg1_attr = {'sent_tok_span':[arg1StartOffset, arg1EndOffset], 'mention_text':arg1}
			arg2_attr = {'sent_tok_span':[arg2StartOffset, arg2EndOffset], 'mention_text':arg2}
			q['args'] = [arg1_attr, arg2_attr]
			q['dataset'] = relation
			q['doc_name'] = docName
			q['answers_gold'] = [{}]
			q['type'] = 'Question'
			if q_id not in db_new:
				# del db_new[q_id]
				db_new[q_id] = q

			# --------------- documents ------------------------
			d = {}
			d['doc_name'] = docName
			d['text'] = sent
			d['type'] = 'Document'
			if docName not in db_new:
				# del db_new[doc_name]
				db_new[docName] = d 

			relCtr[relInd] += 1


def uploadStdFileTest(stdFileTest, db_new):
	relName = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']
	with open(stdFileTest) as f:
		ctr = 0

		for row in f:
			parts = row.split('\t')
			arg1 = parts[0]
			arg1StartOffset = parts[1]
			arg1EndOffset = parts[2]
			arg2 = parts[3]
			arg2StartOffset = parts[4]
			arg2EndOffset = parts[5]
			docName = parts[6]
			sent = parts[11]

			relGold = parts[7]
			relGold = relGold.split(',')

			goldLabel = {
				'r1': relGold[0],
				'r2': relGold[1],
				'r3': relGold[2],
				'r4': relGold[3],
				'r5': relGold[4]
			} 

			# ----------------- questions ----------------------
			q = {}
			q_id = 'g_'+str(ctr)+'_'+docName
			q['for_test'] = '1'
			arg1_attr = {'sent_tok_span':[arg1StartOffset, arg1EndOffset], 'mention_text':arg1}
			arg2_attr = {'sent_tok_span':[arg2StartOffset, arg2EndOffset], 'mention_text':arg2}
			q['args'] = [arg1_attr, arg2_attr]
			q['dataset'] = 'answer_key'
			q['doc_name'] = docName
			q['answers_gold'] = [goldLabel]
			q['type'] = 'Question'
			if q_id not in db_new:
				# del db_new[q_id]
				db_new[q_id] = q

			# --------------- documents ------------------------
			d = {}
			d['doc_name'] = docName
			d['text'] = sent
			d['type'] = 'Document'
			if docName not in db_new:
				# del db_new[doc_name]
				db_new[docName] = d 

			ctr += 1

# if __name__ == "__main__":
# 	direc = '/home/anglil/csehomedir/learner/'
# 	stdFile = sys.argv[1]#direc + 'data_featurized/chris_data_exp'#data_featurized/Gabor_CS_new_feature'
# 	stdFileTest = sys.argv[2]#direc + 'data_test/test_strict_new_feature_no_grammatic'
# 	db_prefix = sys.argv[3]#chris
# 	db_suffix = sys.argv[4]#data
# 	dbName = db_prefix+"_"+db_suffix


# 	db_new = setupDB(dbName)
# 	uploadStdFileCS(stdFile, db_new)
# 	uploadStdFileTest(stdFileTest, db_new)





