Rails.application.routes.draw do
 
  #get 'mturk/complete'

  #get 'mturk/login'

  #get 'mturk/tutorialPage1'

  #get 'mturk/tutorialPage2'

  #get 'mturk/consentPage'

  #get 'mturk/question'

 
	# in app/models
 
	#resources :annotations
  #resources :documents
  #resources :experiments
  #resources :questions
  #resources :users

	#get '/' => 'praxeng#firstPage'
	#post '/' => 'praxeng#firstPage'
	#post '/practice-english' => 'praxeng#secondPage'
	#post '/english-practice' => 'praxeng#thirdPage'
	#get '/privacy' => 'praxeng#privacy'
	#get '/about' => 'praxeng#about'

	root :to => redirect('/mturk')	
	#post '/mturk/consent' => "mturk#consentPage" # name that goes after # is a view
	post '/mturk/tutorial1' => "mturk#tutorialPage1"
	get '/mturk/tutorial1' => "mturk#tutorialPage1"
	post '/mturk/tutorial2' => "mturk#tutorialPage2"
  get '/mturk/tutorial2' => "mturk#tutorialPage2"	
	post '/mturk/tutorial3' => "mturk#tutorialPage3"
  get '/mturk/tutorial3' => "mturk#tutorialPage3"
	post '/mturk/tutorial4' => "mturk#tutorialPage4"	
  get '/mturk/tutorial4' => "mturk#tutorialPage4"  
	post '/mturk/tutorial5' => "mturk#tutorialPage5"
  get '/mturk/tutorial5' => "mturk#tutorialPage5"
	post '/mturk' => "mturk#login"
	get '/mturk' => "mturk#login"
	post '/mturk/question' => "mturk#question"
  get '/mturk/question' => "mturk#question"
	post '/mturk/complete' => "mturk#complete"
  post '/mturk/continue' => "mturk#continue"

	#get '/english-comprehension-practice' => "main#task"
	#post '/english-comprehension' => "main#question"
	#post '/english-comprehension-practice/question' => "main#create2"
	#post '/english-comprehension-practice/response' => "main#create"

  # The priority is based upon order of creation: first created -> highest priority.
  # See how all your routes lay out with "rake routes".

  # You can have the root of your site routed with "root"
  # root 'welcome#index'

  # Example of regular route:
  #   get 'products/:id' => 'catalog#view'

  # Example of named route that can be invoked with purchase_url(id: product.id)
  #   get 'products/:id/purchase' => 'catalog#purchase', as: :purchase

  # Example resource route (maps HTTP verbs to controller actions automatically):
  #   resources :products

  # Example resource route with options:
  #   resources :products do
  #     member do
  #       get 'short'
  #       post 'toggle'
  #     end
  #
  #     collection do
  #       get 'sold'
  #     end
  #   end

  # Example resource route with sub-resources:
  #   resources :products do
  #     resources :comments, :sales
  #     resource :seller
  #   end

  # Example resource route with more complex sub-resources:
  #   resources :products do
  #     resources :comments
  #     resources :sales do
  #       get 'recent', on: :collection
  #     end
  #   end

  # Example resource route with concerns:
  #   concern :toggleable do
  #     post 'toggle'
  #   end
  #   resources :posts, concerns: :toggleable
  #   resources :photos, concerns: :toggleable

  # Example resource route within a namespace:
  #   namespace :admin do
  #     # Directs /admin/products/* to Admin::ProductsController
  #     # (app/controllers/admin/products_controller.rb)
  #     resources :products
  #   end
end
