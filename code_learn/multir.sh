#!/bin/sh

cd /projects/WebWare6/anglil/MultirExperiments/MultiR/multir-release/

sh run.sh $1 $2

mv results $3
echo "trained"