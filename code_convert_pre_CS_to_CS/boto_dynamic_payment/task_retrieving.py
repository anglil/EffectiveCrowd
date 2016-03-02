# credentials should be root keys, and are now stored in ~/.boto as globally accessible 

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,QuestionForm,Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer
import re
import couchdb

# sandbox in which to simulate: mechanicalturk.sandbox.amazonaws.com
# real environment: mechanicalturk.amazonaws.com
mtc = MTurkConnection(host='mechanicalturk.amazonaws.com')
assignments =  mtc.get_assignments('3FTID4TN8L9OJ5AVQYWP04VL777LY4')
for assignment in assignments:
	print assignment.AssignmentId
#read_input()

# print mtc.APIVersion
# print mtc.get_account_balance()
# print mtc.get_reviewable_hits()
# print mtc.get_all_hits()

# couch = couchdb.Server()
# db = couch['praxeng7_production']
# q = '''function(doc) {
# 		if (doc.type == 'Annotation' && doc.question_id != null && doc.user_id != null && doc.response != null)
# 			emit(doc.user_id, doc.question_id);
# 	}'''
# ann_u_view = db.query(q)


#---------------  Get all reviewable hits -------------------
def get_all_reviewable_hits(mtc):
	page_size = 50 # the number of HITs
	hits = mtc.get_reviewable_hits(page_size=page_size)
	print "Total results to fetch: %s " % hits.TotalNumResults
	# print "Request hits page: %i" % 1
	total_pages = float(hits.TotalNumResults)/page_size
	int_total= int(total_pages)
	if(total_pages-int_total>0):
		total_pages = int_total+1
	else:
		total_pages = int_total
	pn = 1
	while pn < total_pages:
		pn = pn + 1
		print "Request hits page: %i" % pn
		temp_hits = mtc.get_reviewable_hits(page_size=page_size,page_number=pn)
		hits.extend(temp_hits)
	return hits

hits = get_all_reviewable_hits(mtc) # only reviewable hits go here; outstanding hits are not reviewable


def valid_code(code):
	if re.match("^(\d{15})00(\d{3})[a-z]{10}bga[a-z]{7}$", code):
		return True
	elif re.match("^(\d{16})00(\d{2})[a-z]{10}bga[a-z]{7}$", code):
		return True
	elif re.match("^(\d{17})00(\d{1})[a-z]{10}bga[a-z]{7}$", code):
		return True
	return False


def get_batch_finished(code):
	num_string = code.rsplit('00',1)[1]
	batch_finished = re.search("^[0-9]+", num_string)
	batch_finished = int(batch_finished.group(0))
	return batch_finished


def get_batch_finished_pre(worker_id, worker_code):
	if worker_id not in worker_code:
		return 0
	batch_finished = []
	for code in worker_code[worker_id]:
		batch_finished.append(get_batch_finished(code))
	return max(batch_finished)


def code_gen(worker_id):
	q_num = len(list(ann_u_view[worker_id]))
	batch_num = q_num / 20 # the number of batches completed; this needs improvements
	batch_num_str = str(batch_num)
	len_str = len(batch_num_str)
	code = '1'*(18-len_str)+'00'+batch_num_str+'d'*10+'bga'+'d'*7
	return code


worker_code = {}
with open('accepted_workers', 'rb') as fr:
	for row in fr:
		tmp = row.split('\t')
		worker_id = tmp[0]
		code = tmp[1].strip()
		if worker_id not in worker_code:
			worker_code[worker_id] = [code]
		else:
			worker_code[worker_id].append(code)


with open('accepted_workers', 'a') as f:
	for hit in hits:
		assignments = mtc.get_assignments(hit.HITId)
		count = 0
		for assignment in assignments:
			count += 1
			# print "Answers of the worker %s:" % assignment.WorkerId
			confirm_code = []
			for question_form_answer in assignment.answers[0]:
				confirm_code = question_form_answer.fields
				break
			confirm_code[0] = confirm_code[0].strip() # get rid of the space at the head and end
			# print "confirm_code: %s" % confirm_code[0]

			# accept rejected workers by their confirm code
			# if confirm_code[0] == "75143812223714147003froxdafnovbgauditsmh":
			# 	try:
			# 		mtc.approve_rejected_assignment(assignment.AssignmentId)
			# 		print "Worker %s is re-approved" % assignment.WorkerId
			# 		code = code_gen(assignment.WorkerId)
			# 		print "The confirm code created:", code

			# 		f.write(assignment.WorkerId)
			# 		f.write('\t')
			# 		f.write(code)
			# 		f.write('\n')

			# 		batch_finished_pre = get_batch_finished_pre(assignment.WorkerId, worker_code)
			# 		if assignment.WorkerId not in worker_code:
			# 			worker_code[assignment.WorkerId] = code
			#                                 		else:
			# 			worker_code[assignment.WorkerId].append(code)
			# 		batch_finished = get_batch_finished(code)
			# 		batch_finished = batch_finished - batch_finished_pre
			# 		print "Batch finished: %i" % batch_finished
			# 		bonus_price = batch_finished*0.5+batch_finished/10*1
			# 		bonus = mtc.get_price_as_price(bonus_price)
			# 		mtc.grant_bonus(assignment.WorkerId, assignment.AssignmentId, bonus, 'good job!')
			# 		print "Bonus granted: $%f" % bonus_price
			# 		print "--------------------"
			# 	except:
			# 		print 'The assignment is already approved or hasn\'t been rejected before'
			# 		print "--------------------"
			# 	continue

			# check how many batches a worker has done
			# if assignment.WorkerId == "A1E7AQE8GKVRC":
			# 	print "worker accomplishment check:", assignment.WorkerId
			# 	code = code_gen(assignment.WorkerId)
			# 	batch_finished_pre = get_batch_finished_pre(assignment.WorkerId, worker_code)
			# 	print "batch_finished_pre:", batch_finished_pre
			# 	batch_finished = get_batch_finished(code)
			# 	print "batch_finished:", batch_finished
			# 	batch_finished = batch_finished - batch_finished_pre
			# 	print "margin:", batch_finished
			# 	print "--------------------"

			# accept rejected workers by their worker ID
			# if assignment.WorkerId == "AAAG7IZP1V712":
			# 	try:
			# 		mtc.approve_rejected_assignment(assignment.AssignmentId)
			# 		print "Worker %s is re-approved" % assignment.WorkerId
			# 		code = code_gen(assignment.WorkerId)
			# 		print "The confirm code created:", code

			# 		f.write(assignment.WorkerId)
			# 		f.write('\t')
			# 		f.write(code)
			# 		f.write('\n')

			# 		batch_finished_pre = get_batch_finished_pre(assignment.WorkerId, worker_code)
			# 		if assignment.WorkerId not in worker_code:
			# 			worker_code[assignment.WorkerId] = code
			# 		else:
			# 			worker_code[assignment.WorkerId].append(code)
			# 		batch_finished = get_batch_finished(code)
			# 		batch_finished = batch_finished - batch_finished_pre
			# 		print "Batch finished: %i" % batch_finished
			# 		bonus_price = batch_finished*0.5+batch_finished/10*1
			# 		bonus = mtc.get_price_as_price(bonus_price)
			# 		mtc.grant_bonus(assignment.WorkerId, assignment.AssignmentId, bonus, 'good job!')
			# 		print "Bonus granted: $%f" % bonus_price
			# 		print "--------------------"
			# 	except:
			# 		print 'The assignment is already approved or hasn\'t been rejected before'
			# 		print "--------------------"
			# 	continue


			if valid_code(confirm_code[0]):
				
				try:
					mtc.approve_assignment(assignment.AssignmentId)
					print "Worker %s is approved" % assignment.WorkerId
					print "The confirm code submitted:", confirm_code[0]

					f.write(assignment.WorkerId)
					f.write('\t')
					f.write(confirm_code[0])
					f.write('\n')

					batch_finished_pre = get_batch_finished_pre(assignment.WorkerId, worker_code)
					if assignment.WorkerId not in worker_code:
						worker_code[assignment.WorkerId] = [confirm_code[0]]
					else:
						worker_code[assignment.WorkerId].append(confirm_code[0])
					batch_finished = get_batch_finished(confirm_code[0])
					batch_finished = batch_finished - batch_finished_pre
					if (batch_finished < 0):
						batch_finished = 0
					print "Batch finished: %i" % batch_finished
					# jbragg: Commented out long-term bonus.
					bonus_price = batch_finished*0.5#+batch_finished/10*2
					bonus = mtc.get_price_as_price(bonus_price)
					mtc.grant_bonus(assignment.WorkerId, assignment.AssignmentId, bonus, 'good job!')
					print "Bonus granted: $%f" % bonus_price
					print "--------------------"
				except:
					pass
					# print 'The assignment is already approved'
					# print "--------------------"

			else:
				try:
					mtc.reject_assignment(assignment.AssignmentId, 'Incorrect confirm code!')
					print "Worker %s is rejected" % assignment.WorkerId
					print "The confirm code submitted:", confirm_code[0]
					print "--------------------"
				except:
					pass
					# print 'The assignment is already rejected'
					# print "--------------------"
		# print 'count', count
		#mtc.disable_hit(hit.HITId)
		# print "HIT", hit.HITId, "disabled."


	# reverse a rejection by HIT ID
	if False:
		assignments = mtc.get_assignments("3WYZV0QBFJON6RY9UPLT3NS7P10BXM")
		count = 0
		for assignment in assignments:
			try:
				mtc.approve_rejected_assignment(assignment.AssignmentId)
				print "Worker %s is re-approved" % assignment.WorkerId
				code = code_gen(assignment.WorkerId)
				print "The confirm code created:", code

				f.write(assignment.WorkerId)
				f.write('\t')
				f.write(code)
				f.write('\n')

				batch_finished_pre = get_batch_finished_pre(assignment.WorkerId, worker_code)
				if assignment.WorkerId not in worker_code:
					worker_code[assignment.WorkerId] = code
				else:
					worker_code[assignment.WorkerId].append(code)
				batch_finished = get_batch_finished(code)
				batch_finished = batch_finished - batch_finished_pre
				print "Batch finished: %i" % batch_finished
				# jbragg: Commented out long-term bonus.
				bonus_price = batch_finished*0.5#+batch_finished/10*1
				bonus = mtc.get_price_as_price(bonus_price)
				mtc.grant_bonus(assignment.WorkerId, assignment.AssignmentId, bonus, 'good job!')
				print "Bonus granted: $%f" % bonus_price
				print "--------------------"
			except:
				print 'The assignment is already approved or hasn\'t been rejected before'
				print "--------------------"


print mtc.get_account_balance()
