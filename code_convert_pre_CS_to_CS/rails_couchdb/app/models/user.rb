class User < CouchRest::Model::Base
	property :src, String 
	property :name, String
	# property :email, String
	# property :password, String
	# property :ip_address, String
	property :confirm_codes, [] # the user submits a confirm code to ensure she finishes the session

	# timestamps create the created_at and updated_at accessors. 
	# These are updated automatically when creating and saving a document and are set as Time objects
	timestamps! 

	design do
		view :by_name
		view :by_src
	end 
end
