# credentials should be root keys, and are now stored in ~/.boto as globally accessible 

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,QuestionForm,Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer

def PublishTasks(hitNum, maxAssignments):
  # sandbox in which to simulate: mechanicalturk.sandbox.amazonaws.com
  # real environment: mechanicalturk.amazonaws.com
  mtc = MTurkConnection(host='mechanicalturk.amazonaws.com')

  # print mtc.APIVersion
  # print mtc.get_account_balance()
  # print mtc.get_reviewable_hits()
  # print mtc.get_all_hits()


  #---------------  BUILD OVERVIEW -------------------

	# jbragg: Modified maximum reward description.
  #title = '(Maximum reward possible: $70) Identify the relation between two entities in English sentences'
  title = 'Identify the relation between two entities in English sentences'
  #description = 'You will be given English sentences in which your task is to identify the relation between two designated entities. Your reward will depend on how many questions you have answered. The maximum reward you can earn is $70.'
  description = 'You will be given English sentences in which your task is to identify the relation between two designated entities. Your reward will depend on how many questions you have answered. The maximum reward you can earn is approximately $5.'
  keywords = 'English sentences, relation identification'


   
  ratings =[('Very Bad','-2'),
           ('Bad','-1'),
           ('Not bad','0'),
           ('Good','1'),
           ('Very Good','1')]
   
  #---------------  BUILD OVERVIEW -------------------
   
  overview = Overview()
  overview_title = 'Exercise link (please copy the link and paste it in your browser if it cannot be opened directly.)'
  link = '<a target="_blank"'' href="http://128.208.3.167:3000/mturk">'' http://128.208.3.167:3000/mturk</a>'
	# jbragg: Commented out long-term bonus.
  instructions = '<p>Instructions:</p><ul><li>You will be presented with sentences that have a person and a location highlighted.</li><li>Your task is to determine which of the 5 designated relations are expressed between the person and location.</li><li>You&#39;ll get paid $0.50 after each successful set of 20 questions<!-- -- plus a bonus of $2.00 after every 10 batches (equal to 200 questions)-->.</li><li>We know the correct answers to some of these sentence questions, and you can stay if you get these questions right.</li><li>You can start by going to the external link above now. After you finish all the questions, you will be provided with a confirm code, used for authentication and determining the appropriate amount of money as the payment.</li><li>In very rare cases where the website crashes, you could click backward and then forward on your browser to reload the question. It won\'t affect the payment because all the questions you have answered are recorded, on which the amount of payment is based. So please don\'t worry about that.</li></ul>'
  overview_content = link + instructions
  overview.append_field('Title', overview_title)
  overview.append(FormattedContent(overview_content))
   
  #---------------  BUILD QUESTION 1 -------------------
   
  qc1 = QuestionContent()
  qc1.append_field('Title','How looks the design ?')
   
  fta1 = SelectionAnswer(min=1, max=1,style='dropdown',
                        selections=ratings,
                        type='text',
                        other=False)
   
  q1 = Question(identifier='design',
                content=qc1,
                answer_spec=AnswerSpecification(fta1),
                is_required=True)
   
  #---------------  BUILD QUESTION 2 -------------------
   
  qc2 = QuestionContent()
  qc2.append_field('Title','Confirm code \n1. The code will be provided to you as you finish from the exercise link. \n2. The code will be verified before paying. \n3. By the end of every 20 questions (as a batch), You can choose to finish and get a confirm code, or continue.')
   
  fta2 = FreeTextAnswer()
   
  q2 = Question(identifier="Confirm_code",
                content=qc2,
                answer_spec=AnswerSpecification(fta2))
   
  #--------------- BUILD THE QUESTION FORM -------------------
   
  question_form = QuestionForm()
  question_form.append(overview)
  # question_form.append(q1)
  question_form.append(q2)
   
  #--------------- CREATE HITs -------------------

  HIT_num = hitNum
  for i in range(HIT_num):
  	# max_assignments: how many replicas this HIT has
  	mtc.create_hit(questions=question_form,
  	               max_assignments=maxAssignments,
  	               title=title,
  	               description=description,
  	               keywords=keywords,
  	               duration = 60*60*10,
  	               reward=0.50)

#PublishTasks(50, 1)
