class ApplicationController < ActionController::Base
	# Prevent CSRF attacks by raising an exception.
	# For APIs, you may want to use :null_session instead.
	#protect_from_forgery with: :exception
	# protect_from_forgery with: :null_session

	# before_filter :my_var

	# protected

	# def my_var
	# 	puts 'aaaaaaaaaaaaaaaaaaaaaaaaa'
	# 	@test_all = Question.by_for_test.key('1').all
	# 	@real_all = Question.by_for_test.key('0').all
	# 	@test_all_shuffle = @test_all.shuffle
	# 	@real_all_shuffle = @real_all.shuffle
	# 	@batch_distribution = getBatchDistro()
	# 	@question_amount = @batch_distribution.sum-1
	# 	puts "sssssssssssssssssssssssssssssssssssssss"
	# end

 #  	######################################################
	# def getBatchDistro()
	# 	q_num = Question.all.length
	# 	q_distro = Array.new(q_num/20, 20)
	# 	q_distro.push(q_num%20)
	# 	return q_distro
	# end

end # end of class
