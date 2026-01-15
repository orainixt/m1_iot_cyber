#!/bin/bash

SIMUL=ACGui.py

if [ $# -eq 0 ]
  then
      echo "No arguments supplied"
	  exit -1
fi

if [[ $1 != *.yaml ]]
then
	echo "The first argument should be an yaml file"
	exit -1
fi

make view
python $SIMUL $@
