class Annotation < CouchRest::Model::Base
	belongs_to :question # associations
	belongs_to :user

	property :response, []

	timestamps! # a special property macro is available called timestamps! that will create the created_at and updated_at accessors. These are updated automatically when creating and saving a document and are set as Time objects

	design do
		view :by_question_id
		view :by_user_id
		view :by_user_id_and_question_id
	end
end
