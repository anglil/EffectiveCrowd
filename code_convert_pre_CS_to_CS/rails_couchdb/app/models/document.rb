class Document < CouchRest::Model::Base
	property :doc_name, String
	property :text, String
	# property :nel_annotations, []

	design do
		view :by_doc_name
	end
end
