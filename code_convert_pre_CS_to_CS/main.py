from downloadStdFileAsCSData import *
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
from scipy.stats.stats import pearsonr
from scipy.stats import ttest_ind


relation_name = ['has nationality', 'was born in', 'lived in', 'died in', 'traveled to']

# praxeng6_production: 5000 sentences crowdsourced
# praxeng7_production: 4000*4 + 1971 sentences crowdsourced 
# praxeng8_production: demo
# gabor_data: gabor's crowd data with our labels
#data = turkData('chris_data_exp_2000')
data = turkData('jbragg_data_164_gold_1')

# {u_id: {"duration": duration, "time_track":[], "question_track":[], "approved":f/t, "response": {q_id: {updated_time, annotation, isCorrect, isCorrectRe, interval}}}
# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isCorrect, isCorrectRe, interval}}}



# --------------------- download the data from the database -----------------------------
#data.writeCSDataToFileWithVotes("crowd_data_2000")

#----------------------- delete one user ------------------
# data.remove_worker_info("sudotry2", False)


# ---------------------- delete all disapproved users and empty annotations -----
# data.remove_empty_worker_info()
# data.remove_disapproved_worker_info()
# data.remove_empty_annotation()

# ---------------------- delete all worker and annotation information ----------
# data.remove_all_worker_and_annotation()


# ---------------------- monitoring progress on crowdsourcing ---------
counting = {}
q_num = 0
for q_id in data.test_question.keys():
	if data.test_question[q_id]['for_test'] == False:
		if 'response_made' in data.test_question[q_id]:
			q_num += 1
			num = data.test_question[q_id]['response_made']
			if num not in counting.keys():
				counting[num] = 1
			else:
				counting[num] += 1
print 'annotation distribution:', counting
print 'amount of question answered:', q_num


approved_num = 0
for row in data.ann_u_view:
	u_id = row['key']
	q_id = str(row['value'][0])
	if 'g_' in q_id:
		continue
	if data.test_question[q_id]['for_test'] == False:
		if data.approved_worker[u_id]['approved']:
			approved_num += 1
print 'amount of annotations (excluding test questions) by approved workers:', approved_num


# --------------------- count the number of questions by distant supervision relation ---
# count = {}
# for row in data.q_view:
# 	rel = row['value'][0]
# 	if rel not in count:
# 		count[rel] = 1
# 	else:
# 		count[rel] += 1
# print count


# ---------------------check the quality of majority vote--------------
# pos = np.zeros(5)
# neg = np.zeros(5)
# non = np.zeros(5)
# for q_id in data.test_question.keys():
# 	# only real questions got a majority vote
# 	if data.test_question[q_id]['for_test'] == False:
# 		mj_v = data.test_question[q_id]["majority"]
# 		if mj_v == None:
# 			continue
# 		for i in range(len(mj_v)):
# 			if 'neg' in mj_v[i]:
# 				neg[i] += 1
# 			elif mj_v[i] == 'NA':
# 				non[i] += 1
# 			else:
# 				pos[i] += 1
# print 'pos', pos
# print 'neg', neg
# print 'non', non


# ----------------------- agreement heatmap (confusion matrix) ----------------------------
# heatmap = data.get_question_agreement_heatmap('/home/anglil/csehomedir/learner/data_featurized/Gabor_CS_new_feature')
# print 'heatmap'
# print heatmap
# heatmap2 = np.copy(heatmap)
# for i in range(len(heatmap2)):
# 	tmp = heatmap2[i].sum()
# 	if tmp == 0:
# 		tmp = 1
# 	heatmap2[i] = np.divide(heatmap2[i], tmp)
# print np.around(heatmap2, decimals=2)

# plt.pcolor(np.flipud(heatmap2), cmap=plt.cm.Reds, edgecolors='k')
# plt.xlabel('nationality, born, lived, died, traveled')
# plt.title('Agreement on Crowdsourcing Results')
# plt.show()


#--------------------------temporarily related statistics (stochastics)----------------------------------
# q_answered = []
# # {u_id: {"duration": duration, "time_track":[], "question_track":[], "approved":f/t, "response": {q_id: {updated_time, annotation, isCorrect, isCorrectRe, interval}}}
# for u_id in data.approved_worker.keys():
# 	if data.approved_worker[u_id]["approved"]:
# 		q_answered.append(len(data.approved_worker[u_id]["response"]))

# pl.figure()
# pl.hist(q_answered)
# pl.title('Histogram of the number of questions answered')
# pl.xlabel('# of questions answered')
# pl.ylabel('# of workers')
# pl.show()

# with open('Figures/q_answered.txt', 'wb') as f:
# 	for item in q_answered:
# 		f.write(str(item))
# 		f.write(' ')


#----------------------- sample a subset of examples for handlabeling --------------------------------
# data.get_sample_question_to_hand_label_2()


#------------------------check how many positive examples in the database -----------------
# test_count = 0
# pos_count = np.zeros(5)
# for q_id in data.test_question.keys():
# 	if data.test_question[q_id]['for_test'] == False:
# 		test_count += 1
# 		mj_ann = data.test_question[q_id]['majority']
# 		for item in mj_ann:
# 			if ('neg' not in item) & (item != 'NA'):
# 				pos_count[relation_name.index(item)] += 1
				
# print "test_count:", test_count
# print "mj pos_count:", pos_count


#---------------------------------------------------------------------------------

# print data.get_question_pos_example()
# agreement_hist, agreement_hist_re, agreement_hist_re_pos, agreement_hist_re_neg = data.get_question_agreement()

# pl.figure()
# pl.hist(agreement_hist, 10)
# pl.show()

# for i in range(5):
# 	pl.figure()
# 	pl.hist(agreement_hist_re[i], 10)
# 	pl.show()

# f, axarr = plt.subplots(5, sharex=True)
# plt.title('histogram of the positive examples that are the majority')
# for i in range(5):
# 	axarr[i].hist(agreement_hist_re_pos[i], 10, range=[0,1])
# 	axarr[i].set_title(relation_name[i])
# plt.show()

# f, axarr = plt.subplots(5, sharex=True)
# plt.title('histogram of the negative examples that are the majority')
# for i in range(5):
# 	axarr[i].hist(agreement_hist_re_neg[i], 10, range=[0,1])
# 	axarr[i].set_title(relation_name[i])
# plt.show()

# print data.get_question_agreement_2()


# data.write_ann_to_csv_training_MJ()
# data.write_ann_to_csv_test_MJ()




# dur = []
# for i in data.approved_worker.keys():
# 	dur.append(data.approved_worker[i]['duration'])
# plt.figure()
# plt.bar(range(10), dur)
# plt.xlabel('Worker index')
# plt.ylabel('Completion time / min')
# plt.show()


# a = data.get_user_accuracy()
# for i in range(len(a)):
# 	a[i] = a[i]/160.0
# # plt.figure()
# # plt.bar(range(10), a)
# # plt.xlabel('Worker index')
# # plt.ylabel('Accuracy')
# # plt.show()
# print a


# # dur_sorted = sorted(dur)
# # dur_order = sorted(range(len(dur)), key=lambda k: dur[k])
# # a_sorted = [a[i] for i in dur_order]
# plt.figure()
# # plt.plot(dur_sorted, a_sorted, 'o')
# plt.plot(dur, a, 'o')
# plt.xlabel('Completion time / min')
# plt.ylabel('Accuracy')
# plt.show()


###############################################################################

# time_track_histo = []
# time_track_histo_tutorial = []
# time_track_histo_question = []

# time_accuracy = np.zeros([10, 160])
# time_accuracy_avg = np.zeros(160)

# time_accuracy_re = np.zeros([10, 160, 5])
# time_accuracy_re_avg = np.zeros([160, 5])

# user_count = 0
# # {u_id: {"duration": duration, "time_track":[], "question_track":[], "response": {q_id: [create_time, response, isCorrect, {interval:start}, isCorrectRe]}}}
# for u_id in data.approved_worker.keys():
# 	time_track = data.approved_worker[u_id]["time_track"]
# 	time_track_histo = np.concatenate((time_track_histo, time_track[1:160]), axis=0)
# 	# time_track_histo_tutorial.append(time_track[0])
# 	time_tutorial = 0
# 	if time_track[0] > 0:
# 		time_tutorial = time_track[0]
# 	else:
# 		time_tutorial = time_track[0]
# 		while time_tutorial < 0:
# 			time_tutorial += 60
# 	time_track_histo_tutorial.append(time_tutorial)
# 	# time_track_histo_question.append(sum(time_track[1:160]))
# 	time_track_histo_question.append(data.approved_worker[u_id]["duration"]-time_tutorial)

# 	num_correct = 0

# 	for i in range(160):
# 		q_id = data.approved_worker[u_id]['question_track'][i]


# 		isCorrect = data.approved_worker[u_id]['response'][q_id][2]
# 		num_correct += isCorrect
# 		time_accuracy[user_count][i] = num_correct*1.0/(i+1)
# 		time_accuracy_avg[i] += isCorrect


# 		isCorrectRe = data.approved_worker[u_id]['response'][q_id][4]
# 		for j in range(5):
# 			time_accuracy_re[user_count][i][j] = isCorrectRe[j]


# 	# plt.figure()
# 	# plt.plot(time_accuracy[user_count])
# 	# plt.xlabel('Question index')
# 	# plt.ylabel('Worker accuracy')
# 	# plt.title('worker' + str(user_count))
# 	# plt.show()


# 	# plt.figure()
# 	# plt.plot(time_track[1:160])
# 	# plt.xlabel('Question index')
# 	# plt.ylabel('Question completion time')
# 	# plt.title('worker' + str(user_count))
# 	# plt.show()


# 	user_count += 1

############################################################################
# sum_correct = 0
# time_accuracy_avg_smooth = np.zeros(160)
# for i in range(160):
# 	sum_correct += time_accuracy_avg[i] 
# 	time_accuracy_avg_smooth[i] = sum_correct*1.0/(10*(i+1))
# pl.figure()
# pl.plot(time_accuracy_avg_smooth)
# pl.xlabel('Time (questions completed)')
# pl.ylabel('Average worker accuracy')
# pl.show()

# K = 20 # plot a dot every 10 annotations 
# time_accuracy_avg_immediate = np.zeros([10, 160/K])
# time_accuracy_avg_immediate_re = np.zeros([10, 160/K, 5])
# for i_user in range(10):
# 	ifSample = False
# 	num_correct = 0
# 	num_correct_re = np.zeros(5)
# 	for i_question in range(160):
# 		if (i_question+1)%K == 0:
# 			ifSample = True
# 		if ifSample:
# 			time_accuracy_avg_immediate[i_user][i_question/K] = num_correct*1.0/(K*5)
# 			for i_relation in range(5):
# 				time_accuracy_avg_immediate_re[i_user][i_question/K][i_relation] = num_correct_re[i_relation]*1.0/K
# 			num_correct = 0
# 			num_correct_re = np.zeros(5)
# 			ifSample = False
# 		else:
# 			ann = time_accuracy_re[i_user][i_question]
# 			num_correct += sum(ann)
# 			num_correct_re += ann
# lgd = []
# m = ['+', '.', 'o', '*', '^']
# l = ['-', ':']
# for i_user in range(10):
# 	plt.plot(time_accuracy_avg_immediate[i_user], marker=m[i_user/2], linestyle=l[i_user/5])
# 	lgd.append('worker'+str(i_user))
# plt.legend(lgd, loc=3)
# plt.ylim([0.5, 1])
# plt.xlabel('Number of batches answered')
# plt.ylabel('Worker accuracy')
# plt.show()

# f, axarr = plt.subplots(5, sharex=True)
# lgd = []
# for i_relation in range(5):
# 	lgd = []
# 	for i_user in range(10):
# 		ann = time_accuracy_avg_immediate_re[i_user]
# 		ann = ann.transpose()
# 		axarr[i_relation].plot(ann[i_relation], marker=m[i_user/2], linestyle=l[i_user/5])
# 		lgd.append('worker'+str(i_user))
# 	axarr[i_relation].set_ylim([0.5, 1])
# 	axarr[i_relation].set_ylabel('Worker accuracy')
# 	axarr[i_relation].set_title(str(data.relation_name[i_relation]))
# plt.legend(lgd, loc=3)
# plt.xlabel('Number of batches answered')
# plt.show()

#######################################################################

# time_track_histo_repair = []
# for i in time_track_histo:
# 	if i > 0:
# 		time_track_histo_repair.append(i)

# pl.figure()
# pl.hist(time_track_histo_repair, 400)
# pl.xlim([0, 10])
# pl.xlabel('Time / min')
# pl.ylabel('Number of annotations')
# pl.show()



# plt.figure()
# p1 = plt.bar(range(10),time_track_histo_tutorial, color='r')
# p2 = plt.bar(range(10),time_track_histo_question, color='y', bottom=time_track_histo_tutorial)
# plt.xlabel('Worker index')
# plt.ylabel('Time / min')
# plt.legend((p1[0], p2[0]), ('tutorial', 'question'))
# plt.show()


# pl.figure()
# pl.bar(range(10),time_track_histo_tutorial, color='r')
# pl.xlabel('Worker index')
# pl.ylabel('Time / min')
# pl.title('Tutorial')
# pl.show()


# pl.figure()
# pl.bar(range(10),time_track_histo_question, color='y')
# pl.xlabel('Worker index')
# pl.ylabel('Time / min')
# pl.title('Question')
# pl.show()


# plt.figure()
# plt.plot(time_track_histo_tutorial, a, 'o')
# plt.xlabel('Time spent on Tutorial / min')
# plt.ylabel('Accuracy')
# plt.show()

# plt.figure()
# plt.plot(time_track_histo_question, a, 'o')
# plt.xlabel('Time spent on Question / min')
# plt.ylabel('Accuracy')
# plt.show()


##########################################################################

# for u_id in data.disapproved_worker.keys():
# 	l = len(data.disapproved_worker[u_id]['response'])
# 	print l
# 	isCorrect = 0
# 	isCorrectRe = np.zeros(5)
# 	for q_id in data.disapproved_worker[u_id]['response']:
# 		isCorrect += data.disapproved_worker[u_id]['response'][q_id][2]
# 		isCorrectRe += data.disapproved_worker[u_id]['response'][q_id][3]
# 	print isCorrect*1.0/l
# 	print isCorrectRe*1.0/l

##########################################################################


# time_accuracy_re[10][160][5] related

# i_user = 0
# batch_res_total = []
# for u_id in data.approved_worker.keys():
# 	batch_res = {}
# 	for i_question in range(160):
# 		i_batch = i_question/20
# 		if i_batch not in batch_res:
# 			batch_res[i_batch] = 0
# 		q_id = data.approved_worker[u_id]['question_track'][i_question]
# 		for_test = data.test_question[q_id]['for_test']
# 		if for_test:
# 			isCorrectRe = time_accuracy_re[i_user][i_question]
# 			if sum(isCorrectRe) != 5:
# 				batch_res[i_batch] += 1

# 	i_user += 1
# 	batch_res_total.append(batch_res)
# for item in batch_res_total:
# 	print item.values() 

# success_num = 8*np.ones(10)
# fail_num = np.zeros(10)
# for i_user in range(10):
# 	flag = 0
# 	for i_batch in range(8):
# 		if batch_res_total[i_user][i_batch] == 2:
# 		# if batch_res_total[i_user][i_batch] >= 1:
# 			fail_num[i_user] += 1
# 		if (batch_res_total[i_user][i_batch] == 2) & (flag == 0):
# 		# if (batch_res_total[i_user][i_batch] != 0) & (flag == 0):
# 			success_num[i_user] = i_batch
# 			flag = 1
# print success_num
# print fail_num


# plt.figure()
# plt.plot(success_num, a, 'o')
# plt.xlabel('# of successful batches')
# plt.ylabel('Accuracy')
# plt.show()
# print pearsonr(success_num, a)

# plt.figure()
# plt.plot(fail_num, a, 'o')
# plt.xlabel('# of failed batches')
# plt.ylabel('Accuracy')
# plt.show()
# print pearsonr(fail_num, a)

# print pearsonr([3,2,1,1,2,3,1,4,1,1], a)
# print pearsonr([1, 3, 1, 3, 1, 1, 1, 0, 2, 1], a)

##########################################################################

# print data.compute_question_majority_vote_accuracy()


# print data.compute_question_EM_accuracy()


# print data.compute_question_raw_accuracy()


##########################################################################

# print data.compute_raw_accuracy_disapproved()



