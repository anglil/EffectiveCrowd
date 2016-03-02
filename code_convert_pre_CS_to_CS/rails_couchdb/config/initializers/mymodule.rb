def getBatchDistro()
	q_num = Question.all.length
	q_distro = Array.new(q_num/20, 20)
	q_distro.push(q_num%20)
	return q_distro
end

def getTestAll()
	test_all = Question.by_for_test.key('1').all
	test_id = []
	test_all.each do |q|
		test_id.push(q["_id"])
	end
	test_id = test_id.shuffle
	return test_id
end

def getRealAll()
	real_all = Question.by_for_test.key('0').all
	real_id = []
	real_all.each do |q|
		real_id.push(q["_id"])
	end
	real_id = real_id.shuffle
	return real_id
end

::Test_all_shuffle = getTestAll()
::Real_all_shuffle = getRealAll()
::Batch_distribution = getBatchDistro()
::Question_amount = ::Batch_distribution.sum

