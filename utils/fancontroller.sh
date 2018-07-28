#!/bin/bash

if [ $( nvidia-smi -q | grep -i fan | head -n 1 | awk '{print $4}' ) -eq 0 ] ; then
    nohup X :1 &
    sleep 5
    export DISPLAY=:1
    nvidia-settings -a [gpu:0]/GPUFanControlState=1 -a [fan-0]/GPUTargetFanSpeed=100
    nvidia-settings -a [gpu:1]/GPUFanControlState=1 -a [fan-1]/GPUTargetFanSpeed=100
fi
