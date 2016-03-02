#!/bin/sh

cd /projects/WebWare6/anglil/MultirExperiments/MultiR/multir-release/MultirFramework
~/bin/sbt "runMain edu.washington.multirframework.featuregeneration.DefaultFeatureGenerator $1 $2"
