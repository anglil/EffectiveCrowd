	# -------------------------- get the test data with multi-positive annotations per example ---------------------------
	# handLabels="test_mj_multiPositive.csv"
	def writeTestDataToFile(self, handLabels, TestTriple):
		# {q_id: {'index': i, 'majority': [], 'gold': [], 'EM': [], 'for_test': f/t, 'response': {u_id: {updated_time, annotation, isApproved, isCorrect, isCorrectRe, interval}}}
		# relation_name = ['has nationality', 'was born in', 'lived in', 'died in', 'traveled to']
		# relation_name_neg = ['has nationality neg', 'was born in neg', 'lived in neg', 'died in neg', 'traveled to neg']
		dataset_name = ['per:origin', '/people/person/place_of_birth', '/people/person/place_lived', '/people/deceased_person/place_of_death', 'travel']

		count = 0

		with open('test_CS_multiPositive', 'wb') as f:
			# this got to be a csv file
			with open(handLabels) as fHand:
				reader = csv.reader(fHand, delimiter='\t')
				for row in reader:
					arg1 = row[1]
					arg2 = row[2]
					docId = row[0]
					label = row[3]

					#------------------- format the labels correctly ------------
					labelArray = label.split(',')
					for item in labelArray:
						item = item.strip().strip('[').strip(']').strip('\'')
					#------------------------------------------------------------

					triple = arg1 + ' ' + arg2 + ' ' + docId

					count += 1

					instance = list(TestTriple[triple])
					instance[7] = ','.join(labelArray)

					f.write('\t'.join(instance))
		print "amount of test examples with positive, negative and optionals:", count
