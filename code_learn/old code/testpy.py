
with open('../data_test/test_multiPositive') as f, open('/home/anglil/WebWare6/anglil/MultirExperiments/MultiR/multir-release/results') as f2:
	a = f.read()
	a = a.split('\n')
	b = f2.read()
	b = b.split('\n')
	for item in range(len(a)-1):
		tmp1 = a[item].split('\t')
		arg11 = tmp1[0]
		arg12 = tmp1[3]
		tmp2 = b[item].split('\t')
		arg21 = tmp2[0]
		arg22 = tmp2[1]
		print arg11 == arg21
		print arg12 == arg22