class Question < CouchRest::Model::Base
	# property :answers, []
	property :args, []
	property :doc_name, String
	property :for_test, String
	property :answers_gold, []

	design do
		view :by_doc_name
		view :by_for_test
	end
end
