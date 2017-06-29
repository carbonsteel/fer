#!/bin/bash
LogFile='application.log'
LogDir='.'
if [ -e  "$LogDir/$LogFile" ];then   
    timestamp=$(date +%s)
    mv "$LogDir/$LogFile" "$LogDir/$timestamp.$LogFile"
fi
time /usr/bin/python2 -m fer.compiler test.fer 1>>application.log 2>&1
