class Comment < CouchRest::Model::Base
	property :body, String
	timestamps! 
end
