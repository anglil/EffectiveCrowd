
# training data
trainingFile=$1
# training data with the full CS set
trainingFileFullCS=$2
# test data
testFile=$3
# test features
testFileTriple=$4
# result data
resFile=$5
# result data with the full CS set
resFileFullCS=$6
# DS or CS 
target=$7


if [ "$target" -eq "DS" ] ; then
	for (( i=0; i<5; i++ ))
	do
		for (( j=0; j<10; j++ ))
		do
			# cd train_CS_and_DS_five_relations/train
			if [ "$i" -le "3" ] ; then
				cat $trainingFile$i$j $trainingFileFullCS > splitDS"$i""$j"_CS
			else
				cp $trainingFile$i$j splitDS"$i""$j"_CS
			fi
			wait
			gzip <splitDS"$i""$j"_CS> splitDS"$i""$j"_CS.gz
			wait
			cd /projects/WebWare6/anglil/MultirExperiments/MultiR/multir-release
			./run.sh /homes/gws/anglil/test/train_CS_and_DS_five_relations/train/splitDS"$i""$j"_CS.gz
			mv results /homes/gws/anglil/test/testTriple
			cd /homes/gws/anglil/test
			echo "$i""$j"
			python eval2.py y_test testFile resFile"$i""$j"
		done
	done
elif [ "$target" -eq "CS" ] ; then
	for (( i=0; i<9; i++ ))
	do
		for (( j=0; j<10; j++ ))
		do
			cd train_CS_and_DS_five_relations/train
			gzip <splitCS"$i""$j"> splitCS"$i""$j".gz
			wait
			cd /projects/WebWare6/anglil/MultirExperiments/MultiR/multir-release
			./run.sh /homes/gws/anglil/test/train_CS_and_DS_five_relations/train/splitCS"$i""$j".gz
			mv results /homes/gws/anglil/test/results
			cd /homes/gws/anglil/test
			echo "$i""$j"
			python eval2.py resCSMultir"$i""$j"
		done
	done
fi

