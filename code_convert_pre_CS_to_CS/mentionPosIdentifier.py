import re
import string

def subFinder(myList, pattern):
	startOffset = -1
	endOffset = -1
	lenPattern = len(pattern)
	for i in range(len(myList)):

		if myList[i] == pattern[0] and myList[i:i+lenPattern] == pattern:
			startOffset = i
			endOffset = i + lenPattern
			break
	return startOffset, endOffset

# tokenizer
def mentionTokenize(argTok):
	tokWalker = 0
	while tokWalker < len(argTok):
		tmp = re.findall(r"[\w']+|[.,!?;]", argTok[tokWalker]) # [.,!?;]
		argTok[tokWalker:tokWalker+1] = tmp
		tokWalker += len(tmp)
	return argTok

def get_entity_pos(arg1, arg2, sent):
	arg1StartOffset = -1
	arg1EndOffset = -1
	arg2StartOffset = -1
	arg2EndOffset = -1
	
	arg1Tok = arg1.split(' ')
	arg2Tok = arg2.split(' ')
	sentTok = sent.split(' ')

	# tokenize arguments
	# arg1Tok = mentionTokenize(arg1Tok)
	# arg2Tok = mentionTokenize(arg2Tok)

	sentLen = len(sentTok)
	arg1Len = len(arg1Tok)
	arg2Len = len(arg2Tok)

	# stripping punctuations
	for i in range(arg1Len):
		if nonsense_match(arg1Tok[i]) == False:
			arg1Tok[i] = arg1Tok[i].strip(string.punctuation)
	for i in range(arg2Len):
		if nonsense_match(arg2Tok[i]) == False:
			arg2Tok[i] = arg2Tok[i].strip(string.punctuation)

	arg1Found = False
	arg2Found = False

	# string match
	arg1StartOffset, arg1EndOffset = subFinder(sentTok, arg1Tok)
	if (arg1StartOffset != -1) and (arg1EndOffset != -1):
		arg1Found = True
	arg2StartOffset, arg2EndOffset = subFinder(sentTok, arg2Tok)
	if (arg2StartOffset != -1) and (arg2EndOffset != -1):
		arg2Found = True

	if arg1Found and arg2Found:
		return arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset

	# heuristic match
	i = 0
	while i < sentLen:
		if arg1Found & arg2Found:
			break
		
		matchLen1 = 0
		nonsenseArgLen1 = 0
		nonsenseSentLen1 = 0
		if arg1Found == False:
			while (matchLen1 + nonsenseArgLen1 < arg1Len) & (i + matchLen1 + nonsenseSentLen1 < sentLen):
				while nonsense_match(arg1Tok[matchLen1 + nonsenseArgLen1])&(matchLen1 + nonsenseArgLen1 < arg1Len-1):
					nonsenseArgLen1 += 1
				while nonsense_match(sentTok[i + matchLen1 + nonsenseSentLen1])&(i + matchLen1 + nonsenseSentLen1 < sentLen-1)&(matchLen1!=0):
					nonsenseSentLen1 += 1
				if arg_match(arg1Tok[matchLen1 + nonsenseArgLen1], sentTok[i + matchLen1 + nonsenseSentLen1]):
					matchLen1 += 1
				else: 
					break

		matchLen2 = 0
		nonsenseArgLen2 = 0
		nonsenseSentLen2 = 0
		if arg2Found == False:
			while (matchLen2 + nonsenseArgLen2 < arg2Len) & (i + matchLen2 + nonsenseSentLen2 < sentLen):
				while nonsense_match(arg2Tok[matchLen2 + nonsenseArgLen2])&(matchLen2 + nonsenseArgLen2 < arg2Len-1):
					nonsenseArgLen2 += 1
				while nonsense_match(sentTok[i + matchLen2 + nonsenseSentLen2])&(i + matchLen2 + nonsenseSentLen2 < sentLen-1)&(matchLen2!=0):
					nonsenseSentLen2 += 1
				if arg_match(arg2Tok[matchLen2 + nonsenseArgLen2], sentTok[i + matchLen2 + nonsenseSentLen2]):
					matchLen2 += 1
				else:
					break

		if (arg1Found == False) & (matchLen1 + nonsenseArgLen1 == arg1Len):
			arg1StartOffset = i
			arg1EndOffset = i + arg1Len + nonsenseSentLen1
			i = arg1EndOffset
			arg1Found = True
		elif (arg2Found == False) & (matchLen2 + nonsenseArgLen2 == arg2Len):
			arg2StartOffset = i
			arg2EndOffset = i + arg2Len + nonsenseSentLen2
			i = arg2EndOffset
			arg2Found = True
		else:
			i = i + 1

	# flag = 0
	# if (arg1StartOffset == -1) | (arg1EndOffset == -1):
	# 	print "arg1 provided:", arg1Tok
	# 	flag = 1
	# if (arg2StartOffset == -1) | (arg2EndOffset == -1):
	# 	print "arg2 provided:", arg2Tok
	# 	flag = 1
	# if flag == 1:
	# 	print sentTok

	return arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset

def arg_match(arg, sentTok):
	if arg == sentTok:
		return True
	elif re.match("^[^A-Za-z0-9]*" + arg + "[^A-Za-z0-9]*$", sentTok):
		return True
	elif re.match("^.*[^A-Za-z0-9]+" + arg + "[^A-Za-z0-9]*$", sentTok):
		return True
	elif re.match("^[^A-Za-z0-9]*" + arg + "[^A-Za-z0-9]+.*$", sentTok):
		return True
	return False


def nonsense_match(tok):
	if re.match("^[^A-Za-z0-9]+$", tok):
		return True
	elif tok == '':
		return True
	return False

# ----------------------------
def mentionMatchTest(stdFile):
	countNeg = 0
	with open(stdFile) as f:
		for row in f:
			parts= row.split('\t')
			arg1 = parts[0]
			arg2 = parts[3]
			sent = parts[11]
			arg1StartOffset, arg1EndOffset, arg2StartOffset, arg2EndOffset = get_entity_pos(arg1, arg2, sent)
			
			# only arguments that my program thinks match can go on to the comparison phase
			if (arg1StartOffset != -1) and (arg1EndOffset != -1) and (arg2StartOffset != -1) and (arg2EndOffset != -1):
				sentTok = sent.split(' ')
				lenSentTok = len(sentTok)

				arg1_bucket = []
				arg1_tok = arg1StartOffset
				while (arg1_tok < arg1EndOffset) & (arg1_tok < lenSentTok):
					arg1_bucket.append(sentTok[arg1_tok])
					arg1_tok += 1
				arg1_pred = ' '.join(arg1_bucket)


				arg2_bucket = []
				arg2_tok = arg2StartOffset
				while (arg2_tok < arg2EndOffset) & (arg2_tok < lenSentTok):
					arg2_bucket.append(sentTok[arg2_tok])
					arg2_tok += 1
				arg2_pred = ' '.join(arg2_bucket)


				flag = 0
				if arg1 != arg1_pred:
					flag = 1
					print "arg1 recognized:", arg1_pred
					print "arg1 provided:", arg1
				if arg2 != arg2_pred:
					flag = 1
					print "arg2 recognized:", arg2_pred
					print "arg2 provided:", arg2

				if flag == 1:
					print sent
					countNeg += 1
					print "---------------------------------------"

	print "wrong segmentation:", countNeg

if __name__ == "__main__":
	mentionMatchTest("/home/anglil/WebWare6/anglil/praxeng/myTurk4/sentences/extractions5Relations.shuffled")
