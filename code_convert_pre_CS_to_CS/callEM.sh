export MLM_LICENSE_FILE=27000@lmas.engr.washington.edu,27000@nexus.engr.washington.edu,27000@persephone.engr.washington.edu
#cd EM_analysis
( matlab -nodesktop -nosplash -nojvm -nodisplay -r 'try;REturk;catch;end;quit;' ) > matlablog.txt 2> errorlog.txt
#| tail -n +10
#cd ..

