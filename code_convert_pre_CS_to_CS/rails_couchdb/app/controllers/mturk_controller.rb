class MturkController < ApplicationController
 	# skip_before_filter	:verify_authenticity_token #a critical step for authentication
	
	
	######################################################  
	def login
		comments = params[:comments]
		if comments != nil
			c = Comment.new(
	  				:body => comments 
	  				)
  			c.save # save to database
		end
		@worker_id = params[:worker_id]
		@chances = 10 # chances a worker you have to pass the tutorial
		@message = nil
		@question_num = 0
		@worker_id_filled = false
		if @worker_id == nil # the first time
			render 'login'
		elsif @worker_id.empty? || !@worker_id.alpha? # upon submission without any id
			@message = "Please enter a valid Amazon mechanical Turk Worker ID."
			render 'login'
		else # upon submission with a worker id
			@worker_id_filled = true
			render 'login' # worker_id is passed to tutorialPage1
		end
  	end

	######################################################  
  	def question
		@check = {
			"r1" => nil,
			"r2" => nil,
			"r3" => nil,
			"r4" => nil,
			"r5" => nil
		}

		@message = nil
		@messageX = {
			"r1" => nil,
			"r2" => nil,
			"r3" => nil,
			"r4" => nil,
			"r5" => nil
		}
		@color0 = "color:red"
		@colorX = {
			"r1" => "color:red", 
			"r2" => "color:red",
			"r3" => "color:red", 
			"r4" => "color:red",
			"r5" => "color:red"
		}

		

  		@worker_id = params[:worker_id]
  		# prevent from directly entering the question section without user authentication
  		if @worker_id == nil
			redirect_to "/mturk" 
			return
		end

  		@chance_q = params[:chance_q]
  		# 1. initial chances for the first 5 extended tutorial questions. 1 mistake allowed among 5
  		# 2. and later chance_q is used for one batch-immediate question-level accuracy counts. 5 * 0.8 = 4
  		if @chance_q == nil
  			@chance_q = 5
  		end

  		@hit_window = params[:hit_window]
  		# two batch-accumulative accuracy counts. Getting 10 * 5 * 0.8 = 40 right will let a worker pass
  		if @hit_window == nil
  			@hit_window = 50
  		end


  		# puts 'loading the number of questions finished...'
  		question_finished = Annotation.by_user_id.key(@worker_id).count#@test_question_finished.to_a.length + @real_question_finished.to_a.length
  		@question_index = question_finished # the current question index before getting to the next question 
  		puts "question finished: #{@question_index}"

  		# the number of sentences in each batch
  		@batch_index = getBatchIndex(@question_index, Batch_distribution)
  		@index_in_batch = getIndexInBatch(@question_index, Batch_distribution)
  		batch_size = Batch_distribution[@batch_index]
  		
  		# the indices of gold questions in a batch	
  		# enter for the first time or for more than one time with more than 20 questions answered
  		# puts 'loading the test question index in batch...'
		if (@batch_index == 0) | (params[:test_question_index_in_batch] == nil)
			@test_question_index_in_batch = getTestQuestionIndex(@batch_index, Batch_distribution[@batch_index])
		else
			@test_question_index_in_batch = []
			for i in 0..(params[:test_question_index_in_batch].length-1)
				@test_question_index_in_batch.push(params[:test_question_index_in_batch][i.to_s].to_i) # question id
			end
		end



  		# present the next question and the next document 
  		# and get the user and the user's annotation
  		if params[:option] == nil
  			### user (the very first) ###
			user = User.get(@worker_id) # get from database
	  		
	  		if !user
	  			# instantiate a user in the controller
	  			user = User.new(
	  				:id => @worker_id, 
	  				:name => @worker_id,
	  				:confirm_codes => nil#[@complete_code]
	  				)
	  			user.save # save to database
	  		else # check up this worker's history and blacklist the worker if necessary 
	  			if (@question_index < 20) & (@question_index > 0) # one that has been filtered out
	  				#@fromWeedOut = 1
  					#render 'complete'
  					#return
	  			end
	  		end

	  		### annotation (the very first) ###
	  		# none

  			### question and document (the very first) ###
  			puts '----------Getting the first question----------'
  			puts "annotation num: #{Annotation.all.count}"
  			isTestQuestion = false 
  			if @test_question_index_in_batch.include?(@index_in_batch)
  				isTestQuestion = true
  			end
		  	@current_question = getQuestion(
		  		@worker_id,
		  		isTestQuestion)
		  	if @current_question == nil # run out of questions
		  		@fromRunOut = 1
		  		@batch_index = -1 # if this worker has already done all the questions, then she should not receive money upon entering the website
		  		render 'complete'
		  		return
		  	end
		  	# puts 'First question obtained!'
		  	@current_sentence = getSentence(@current_question)
		  	# puts 'First sentence obtained!'


		# the worker submitted her answer
  		elsif params[:option] == "submit"
  			
	  		if params[:response] == nil
				['r1', 'r2', 'r3', 'r4', 'r5'].each do |item|
					@messageX[item] = "Please choose one for this relation!"
					@colorX[item] = "color:red"
				end
			else
				@check.each do |key,value| # key: r1, r2, r3, r4, r5
					@check[key] = params[:response][key]
					if @check[key] == nil
						@messageX[key] = "Please choose one for this relation!"
						@colorX[key] = "color:red"
					end
				end		
			end


			if @check == nil || @check.has_value?(nil)
				### question and document (repeated) ###
				
			  	@current_question = Question.find(params[:current_question_id])
			  	@current_sentence = params[:current_sentence]
				@message = "You should make a judgment for every relation."
			

			# all 5 answers are submitted
			else 
		  		### user ###
		  		# puts 'loading the user profile...'
		  		user = User.get(@worker_id)

		  		### annotation ###
		  		puts '----------Saving the annotation----------'
		  		# if it is a question this worker has already answered, then update it's answer (only happens when the worker hits the back button of the browser)
		  		# puts 'writing the annotation...'
		  		annotation, isOld = newAnnotation(user, params[:current_question_id], params[:response])
		  		
		  		# concurrency control
		  		validAnnotation = true
		  		if annotation == nil
		  			validAnnotation = false
		  			@message = "The number of times this question has been annotated has exceeded the threshold because of the annotations that are made before you. We'll replace this question with a new one."
		  		end

		  		# puts 'loading the number of questions finished...'
		  		if validAnnotation & (isOld == false)
		  			@question_index += 1
		  		end
  				puts "question finished: #{@question_index}"

  				# the number of sentences in each batch
		  		@batch_index = getBatchIndex(@question_index, Batch_distribution)
		  		@index_in_batch = getIndexInBatch(@question_index, Batch_distribution)
		  		batch_size = Batch_distribution[@batch_index]


		  		# puts 'check if end of batch'
				@end_of_batch = false
		  		if @index_in_batch == 0 # the start of a new batch
		  			@test_question_index_in_batch = getTestQuestionIndex(@batch_index, batch_size)
		  			@end_of_batch = true
		  		end


		  		# puts 'checking if the question pool is depleted'
		  		if @question_index == Question_amount
		  			@fromEnd = 1
		  			@batch_index_pre = get_batch_index_pre(@worker_id)
		  			@complete_code = getCompletionCode(@batch_index, @worker_id)
		  			render "complete"
		  			return
		  		end


		  		ques = nil
		  		# if the annotation is a nonempty one, then get the question and do the weed-out check
  				if validAnnotation
			  		q = annotation.question_id # belongs_to, equals to params[:current_question_id]
			  		# puts 'loading the question profile...'
			  		ques = Question.get(q)  		

			  		###########################################
			  		# weed-out phase
			  		# puts 'deciding if entering the weed-out phase'
			  		if (@batch_index == 0) && (@question_index <= 5)
			  			answers = checkAnswer(@check, ques.answers_gold[0])
						answers.each do |key,value|
							if value == false
								@messageX[key] = 'X'
							# else
							# 	@messageX[key] = '✓'
							# 	@colorX[key] = "color:green"
							end
						end
					end

			  		###########################################
			  	end

		  		# puts 'checking on correctness'
		  		if @messageX.values().include?('X') # include incorrect answers
		  			@current_question = Question.find(params[:current_question_id])
			  		@current_sentence = params[:current_sentence]
			  		@message = "Please try again."

			  		@chance_q = @chance_q.to_i - 1
			  		puts "chance_q: #{@chance_q}"

			  	else # all answers are correct
			  		@messageX.each do |key,value|
			  			@messageX[key] = nil
			  		end

			  		# concurrency control
			  		if validAnnotation
				  		# handle feedback message
				  		if (@batch_index == 0) && (@question_index <= 5)
				  			@messageUp = "Good job!"
				  			if @question_index == 5
				  				# if the worker accuracy is less than 80%, then the worker is immediately not eligible for more questions
				  				if @chance_q.to_i < 4 
				  					#@fromWeedOut = 1
				  					#render 'complete'
				  					#return
				  				end
				  				@messageUp = @messageUp + "\nFrom now on, you will not get feedbacks on your answers. However, we will spot check. \nIf you stay at a high accuracy, you'll be rewarded $0.50 upon finishing a batch of 20 questions and a bonus of $2.00 after every 10 batches."
				  				# should the worker passes the weed-out, her chances will be reset to 5
				  				@chance_q = 5 
				  			end
				  		end


				  		# handle worker qualification 
						if ques.for_test == '1' # the first batch is the only one in which to exam workers
							# question-level check
							correctAns = checkAnswer_q(@check, ques.answers_gold[0])
							if !correctAns
								@chance_q = @chance_q.to_i - 1
							end

							# relation-level check
							correctAnsRe = checkAnswer(@check, ques.answers_gold[0])
							@hit_window = @hit_window.to_i - correctAnsRe.values.count(false) # subtract the number of wrong answers from the chances
						end

						puts "chance_q: #{@chance_q}"
						puts "hit_window: #{@hit_window}"
					end


			  		# reset answers for the next question
					@check = nil 


			  		### question and document (new) ###	
			  		puts '----------Getting a question----------'
			  		# whether the next question is a test question or a real question
			  		isTestQuestion = false
			  		if @test_question_index_in_batch.include?(@index_in_batch)
			  			isTestQuestion = true
			  		end
			  		puts "index in batch: #{@index_in_batch}"
			  		puts "batch index: #{@batch_index}"
			  		puts "test_question_index_in_batch: #{@test_question_index_in_batch}"
			  		puts "isTestQuestion: #{isTestQuestion}"

				  	@current_question = getQuestion(
				  		@worker_id,
				  		isTestQuestion)
				  	 # run out of questions
				  	if @current_question == nil
				  		@fromRunOut = 1
				  		@batch_index_pre = get_batch_index_pre(@worker_id)
				  		@complete_code = getCompletionCode(@batch_index, @worker_id)
				  		render 'complete'
				  		return
				  	end
				  	@current_sentence = getSentence(@current_question)	  	
				  		

		  			# go to an intermediate checkpoint, and evaluate the performance on the previous batch
			  		if @end_of_batch & validAnnotation
			  			
			  			if false #(@chance_q.to_i < 4) | ((@hit_window.to_i < 46) & ([2, 8, 32, 128, 512].include?(@batch_index-1) ) )
			  				@fromFailure = 1
			  				@batch_index_pre = get_batch_index_pre(@worker_id)
			  				@complete_code = getCompletionCode(@batch_index, @worker_id)
			  				render 'complete'
			  			else
			  				# should the worker passes the 5 gold questions in one batch, her chances will be reset to 5
			  				@chance_q = 5
			  				# should the worker passes the 10 gold questions in two consecutive batches, her accumulative chances will be reset to 50
			  				if [2, 8, 32, 128, 512].include?(@batch_index-1)
			  					@hit_window = 50
			  				end
			  				# the continue page will go back to question page again, so be careful about the changes in variables
			  				# the current question will also be pass to the continue page
			  				@batch_index_pre = get_batch_index_pre(@worker_id)
			  				render 'continue' 
			  			end
			  		end
				  	
			  	end
		  	end

		else # from continue
			if params[:option] == "continue" # "continue"

				### question and document (repeated) ###
			  	@current_question = Question.find(params[:current_question_id])
			  	@current_sentence = params[:current_sentence]

			  	@message = "Welcome back!"
			  	# @check = nil # reset answers for the next question
			else # "finish"
				@fromCheckpoint = 1
				@batch_index_pre = get_batch_index_pre(@worker_id)
				@complete_code = getCompletionCode(@batch_index, @worker_id) # have gone through the continue page that directs to question page
				render 'complete'
			end
		end
  	end


	######################################################  
	def complete
		# @fromCheckpoint
		# @fromTutorial
		# @fromFailure
		# @fromEnd
		# @fromWeedOut
		# @fromRunOut
  	end

  	######################################################  
	def continue
  	end

	######################################################
	def checkAnswer(response, answer)
		binRes = {}
		answer.each do |key,value| # this is a ruby loop
			if answer[key] == "optional"
				binRes[key] = true
			else
				if answer[key] != response[key]
					binRes[key] = false
				else
					binRes[key] = true
				end
			end
		end
		return binRes
	end

	######################################################
	def checkAnswer_q(response, answer)
		answer.each do |key,value| # this is a ruby loop
			if answer[key] != "optional"
				if answer[key] != response[key]
					return false
				end
			end
		end
		return true
	end

	######################################################
	def chanceUp(chance)
		if chance.to_i == 0
			@fromTutorial = 1
			render "complete"
		end
	end



	######################################################
	def getBatchIndex(question_index, batch_distribution) # 20 questions per batch
		index = 0
		residual = question_index - batch_distribution[index]
		while residual >= 0 do
			index += 1
			residual -= batch_distribution[index]
		end
		return index
	end

	######################################################
	def getIndexInBatch(question_index, batch_distribution) # 20 questions per batch
		index = 0
		residual = question_index - batch_distribution[index]
		while residual >= 0 do
			index += 1
			residual -= batch_distribution[index]
		end
		return batch_distribution[index] + residual
	end

	######################################################
	def getTestQuestionIndex(batch_index, batch_size)
		res = []	
		# extended tutorial; weed out
		if batch_index == 0
			res = [0, 1, 2, 3, 4]
		# exponential back off
		elsif [1, 2, 4, 8, 16, 32, 64, 128, 256, 512].include?(batch_index)
			tmp = (0..batch_size-1).to_a.shuffle
			for i in 0..4 # insert 5 gold questions
				test_index = tmp.pop
				res.push(test_index)
			end
			# res.push('0')
			# res.push('19')
		end
		return res
	end


	######################################################
	def get_batch_index_pre(worker_id)
		user = User.get(worker_id)
		codes = user.confirm_codes
		code = codes.pop
		if code == nil
			return 0
		end

		a = code.match(/^[0-9]{17}00[0-9]{1}[a-z]{10}bga[a-z]{7}$/).to_s
		b = code.match(/^[0-9]{16}00[0-9]{2}[a-z]{10}bga[a-z]{7}$/).to_s
		c = code.match(/^[0-9]{15}00[0-9]{3}[a-z]{10}bga[a-z]{7}$/).to_s
		if (a == "") & (b == "") & (c == "")
			return 0
		end

		return code.rpartition('00').last.match(/[0-9]+/).to_s.to_i

	end

	
	######################################################
	def getCompletionCode(batch_index, worker_id)
		complete_code = nil
		user = User.get(worker_id) # get from database

		len = batch_index.to_s.length

		# 50 digits
  		complete_code = # bga means 160
  			(0...(20-2-len)).map { ('0'..'9').to_a[rand(10)] }.join +
  			'00' + batch_index.to_s + (0...10).map { ('a'..'z').to_a[rand(26)] }.join +
  			'bga' + (0...7).map { ('a'..'z').to_a[rand(26)] }.join
  		if user.confirm_codes == nil
  			user.update_attributes(:confirm_codes => [complete_code])
  		else
  			# update user's confirmation code (add the new one)
  			codes = user.confirm_codes
  			codes.push(complete_code)
  			user.update_attributes(:confirm_codes => codes) # update attributes
  		end
		return complete_code
	end

	######################################################
	def newAnnotation(user, questionId, userResponse)
		annotation = nil
		isOld = false

		question = Question.get(questionId)
		response = Array.new
		userResponse.each do |key, value|
			response.push(value)
		end
		
		ann = Annotation.by_user_id_and_question_id.key([user["_id"], questionId])
		if ann.count == 0
			# concurrency control for test questions
			if (Annotation.by_question_id.key(questionId).count >= 9999) & (question.for_test == "0") 
				puts 'already annotated twice!'
				return annotation # nil
			else
				puts 'new annotation!'
				annotation = Annotation.new(:question => question, :user => user, :response => response)
				annotation.save
			end
		else
			puts 'same annotation!'
			isOld = true
			annotation = ann.first
			annotation.update_attributes(:response => response)
		end
		return annotation, isOld
	end


  	##########################################
  	def getSentence(question)
    	docName = question.doc_name
    	current_document = Document.by_doc_name.key(docName).first # the first of all, every of which has the same text field, so doing first does not matter
    	doc_text = current_document.text
    	return doc_text
  	end


  	##########################################
  	def getQuestion(worker_id, isTestQuestion)

  		u_q_grouped = Annotation.by_user_id_and_question_id
    	if isTestQuestion
      		q_all = Test_all_shuffle
      		q_all = q_all.shuffle
      		q_all.each do |q_id|
  				if u_q_grouped.key([worker_id, q_id]).count == 0
  					puts 'question found!'
  					return Question.get(q_id)
  				end
  			end
      	else
      		q_all = Real_all_shuffle
      		q_all = q_all.shuffle
      		q_grouped = Annotation.by_question_id
	  		q_all.each do |q_id|
	  			if q_grouped.key(q_id).length < 9999 # the maximum number of annotations a question can receive 
	  				if u_q_grouped.key([worker_id, q_id]).count == 0
	  					puts 'question found!'
	  					return Question.get(q_id)
	  				end
	  			end
	  		end
      	end
	  	puts 'question not found!'
  		return nil
	end



	######################################################
  	def tutorialPage1
		@worker_id = params[:worker_id]
		if @worker_id == nil
			redirect_to "/mturk"
			return
		end

		@chances = params[:chances]
		@check = {
			"r1" => nil,
			"r2" => nil
		}
		ans = {
			"r1" => "has nationality",
			"r2" => "lived in"
		}

		@message = nil
		messageFb = {
			"r1" => "Assume a national officer has nationality of that country",
			"r2" => "Assume a national officer lives in that country"
		}
		@messageX = {
			"r1" => nil,
			"r2" => nil
		}
		
		@color0 = "color:red"
		@colorX = {
			"r1" => "color:red", 
			"r2" => "color:red"
		}
		
		@correct = false
		
		if params[:option] == nil # not useful here, but same thing useful in later tutorials
			render 'tutorialPage1'
		# upon submission, the option field should be submit, instead of nil
		else
			@question_num = 1	
			if params[:response] == nil
				ans.each do |key,value|
					@messageX[key] = "Please choose one for this relation!"
					@colorX[key] = "color:red"
				end
			else
				@check.each do |key,value| # key: r1, r2
					@check[key] = params[:response][key]
					if @check[key] == nil
						@messageX[key] = "Please choose one for this relation!"
						@colorX[key] = "color:red"
					end
				end
			end
			if @check == nil || @check.has_value?(nil)
				@message = "You should make a judgment for every relation."
			else
				answers = checkAnswer(@check, ans)
				flag = true
				answers.each do |key,value|
					if answers[key] == false
						flag = false
						@messageX[key] = messageFb[key]
					end
				end
				if flag == false
					@chances = @chances.to_i - 1
					chanceUp(@chances)
					@message = "Your answer is not correct. #{@chances} chances left."
				else # get the correct answer
					@correct = true
					@color0 = "color:green"
					@message = "Correct! Now you have completed #{@question_num}/5 of the practice sentences."
				end
			end
		end
  	end
	
	######################################################
  	def tutorialPage2
  		@worker_id = params[:worker_id]
  		if @worker_id == nil
			redirect_to "/mturk"
			return
		end

		@chances = params[:chances]
		@check = {
			"r1" => nil,
			"r2" => nil
		}
		ans = {
			"r1" => "has nationality neg",
			"r2" => "lived in neg"
		}

		@message = nil
		messageFb = {
			"r1" => "Cities can't be a nationality",
			"r2" => "Don't assume he lives where he works"
		}
		@messageX = {
			"r1" => nil,
			"r2" => nil
		}
		
		@color0 = "color:red"
		@colorX = {
			"r1" => "color:red", 
			"r2" => "color:red"
		}
		
		@correct = false

		if params[:option] == nil # used for just being directed in
			render 'tutorialPage2'
		else
			@question_num = 2	
			if params[:response] == nil
				ans.each do |key,value|
					@messageX[key] = "Please choose one for this relation!"
					@colorX[key] = "color:red"
				end
			else
				@check.each do |key,value| # key: r1, r2
					@check[key] = params[:response][key]
					if @check[key] == nil
						@messageX[key] = "Please choose one for this relation!"
						@colorX[key] = "color:red"
					end
				end		
			end
			if @check == nil || @check.has_value?(nil)
				@message = "You should make a judgment for every relation."
			else
				answers = checkAnswer(@check, ans)
				flag = true
				answers.each do |key,value|
					if value == false
						flag = false
						@messageX[key] = messageFb[key] 
					end
				end
				if flag == false
					@chances = @chances.to_i - 1
					chanceUp(@chances)
					@message = "Your answer is not correct. #{@chances} chances left."
				else # get the correct answer
					@correct = true
					@color0 = "color:green"
					@message = "Correct! Now you have completed #{@question_num}/5 of the practice sentences."
				end
			end
		end
	end

	######################################################  
	def tutorialPage3
		@worker_id = params[:worker_id]
		if @worker_id == nil
			redirect_to "/mturk"
			return
		end

		@chances = params[:chances]
		@check = {
			"r1" => nil,
			"r2" => nil,
			"r3" => nil,
			"r4" => nil
		}
		ans = {
			"r1" => "has nationality",
			"r2" => "was born in neg",
			"r3" => "lived in neg",
			"r4" => "died in neg"
		}

		@message = nil
		messageFb = {
			"r1" => "Nationality is explicitly mentioned",
			"r2" => "Nationality does not imply born in the country",
			"r3" => "Don't assume he lived in France",
			"r4" => "Doesn't say that he died in France"
		}
		@messageX = {
			"r1" => nil,
			"r2" => nil,
			"r3" => nil,
			"r4" => nil
		}
		
		@color0 = "color:red"
		@colorX = {
			"r1" => "color:red", 
			"r2" => "color:red",
			"r3" => "color:red", 
			"r4" => "color:red"
		}
		
		@correct = false

		if params[:option] == nil # used for just being directed in
			render 'tutorialPage3'
		else
			@question_num = 3	
			if params[:response] == nil
				ans.each do |key,value|
					@messageX[key] = "Please choose one for this relation!"
					@colorX[key] = "color:red"
				end
			else
				@check.each do |key,value| # key: r1, r2, r3, r4
					@check[key] = params[:response][key]
					if @check[key] == nil
						@messageX[key] = "Please choose one for this relation!"
						@colorX[key] = "color:red"
					end
				end		
			end
			if @check == nil || @check.has_value?(nil)
				@message = "You should make a judgment for every relation."
			else
				answers = checkAnswer(@check, ans)
				flag = true
				answers.each do |key,value|
					if value == false
						flag = false
						@messageX[key] = messageFb[key]
					end
				end
				if flag == false
					@chances = @chances.to_i - 1
					chanceUp(@chances)
					@message = "Your answer is not correct. #{@chances} chances left."
				else # get the correct answer
					@correct = true
					@color0 = "color:green"
					@message = "Correct! Now you have completed #{@question_num}/5 of the practice sentences."
				end
			end
		end
	end

	######################################################  
	def tutorialPage4
		@worker_id = params[:worker_id]
		if @worker_id == nil
			redirect_to "/mturk"
			return
		end

		@chances = params[:chances]
		@check = {
			"r1" => nil,
			"r2" => nil,
			"r3" => nil,
			"r4" => nil
		}
		ans = {
			"r1" => "has nationality neg",
			"r2" => "was born in",
			"r3" => "lived in neg",
			"r4" => "died in neg"
		}

		@message = nil
		messageFb = {
			"r1" => "Cities can't be a nationality",
			"r2" => "Place of birth is explicitly mentioned",
			"r3" => "Don't assume he lived where he was born",
			"r4" => "Doesn't say where he died"
		}
		@messageX = {
			"r1" => nil,
			"r2" => nil,
			"r3" => nil,
			"r4" => nil
		}
		
		@color0 = "color:red"
		@colorX = {
			"r1" => "color:red", 
			"r2" => "color:red",
			"r3" => "color:red", 
			"r4" => "color:red"
		}
		
		@correct = false

		if params[:option] == nil # used for just being directed in
			render 'tutorialPage4'
		else
			@question_num = 4	
			if params[:response] == nil
				ans.each do |key,value|
					@messageX[key] = "Please choose one for this relation!"
					@colorX[key] = "color:red"
				end
			else
				@check.each do |key,value| # key: r1, r2, r3, r4
					@check[key] = params[:response][key]
					if @check[key] == nil
						@messageX[key] = "Please choose one for this relation!"
						@colorX[key] = "color:red"
					end
				end		
			end
			if @check == nil || @check.has_value?(nil)
				@message = "You should make a judgment for every relation."
			else
				answers = checkAnswer(@check, ans)
				flag = true
				answers.each do |key,value|
					if value == false
						flag = false
						@messageX[key] = messageFb[key]
					end
				end
				if flag == false
					@chances = @chances.to_i - 1
					chanceUp(@chances)
					@message = "Your answer is not correct. #{@chances} chances left."
				else # get the correct answer
					@correct = true
					@color0 = "color:green"
					@message = "Correct! Now you have completed #{@question_num}/5 of the practice sentences."
				end
			end
		end
	end

	######################################################  
	def tutorialPage5
  		@worker_id = params[:worker_id]
		if @worker_id == nil
			redirect_to "/mturk"
			return
		end

		@chances = params[:chances]
		@check = {
			"r1" => nil,
			"r2" => nil,
			"r3" => nil,
			"r4" => nil,
			"r5" => nil
		}
		ans = {
			"r1" => "has nationality",
			"r2" => "was born in neg",
			"r3" => "lived in",
			"r4" => "died in neg",
			"r5" => "traveled to neg"
		}

		@message = nil
		messageFb = {
			"r1" => "Assume that a national officer has nationality",
			"r2" => "Nationality doesn't imply she was born in that country",
			"r3" => "Assume that a national officer lives in that country",
			"r4" => "Doesn't say where she died",
			"r5" => "Doesn't say she traveled to the highlighted location (U.S.)"
		}
		@messageX = {
			"r1" => nil,
			"r2" => nil,
			"r3" => nil,
			"r4" => nil,
			"r5" => nil
		}
		
		@color0 = "color:red"
		@colorX = {
			"r1" => "color:red", 
			"r2" => "color:red",
			"r3" => "color:red", 
			"r4" => "color:red",
			"r5" => "color:red"
		}
		
		@correct = false

		if params[:option] == nil # used for just being directed in
			render 'tutorialPage5'
		else
			@question_num = 5	
			if params[:response] == nil
				ans.each do |key,value|
					@messageX[key] = "Please choose one for this relation!"
					@colorX[key] = "color:red"
				end
			else
				@check.each do |key,value| # key: r1, r2, r3, r4, r5
					@check[key] = params[:response][key]
					if @check[key] == nil
						@messageX[key] = "Please choose one for this relation!"
						@colorX[key] = "color:red"
					end
				end		
			end
			if @check == nil || @check.has_value?(nil)
				@message = "You should make a judgment for every relation."
			else
				answers = checkAnswer(@check, ans)
				flag = true
				answers.each do |key,value|
					if value == false
						flag = false
						@messageX[key] = messageFb[key]
					end
				end
				if flag == false
					@chances = @chances.to_i - 1
					chanceUp(@chances)
					@message = "Your answer is not correct. #{@chances} chances left."
				else # get the correct answer
					@correct = true
					@color0 = "color:green"
					@message = "Correct! Now you have completed #{@question_num}/5 of the practice sentences."
				end
			end
		end
	end

end


class String
	def alpha?
		!!match(/^[[:alnum:]]+$/) # all number?
	end
end
