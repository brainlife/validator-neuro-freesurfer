#!/bin/bash

set -e

name=brainlife/validator-neuro-freesurfer
tag=1.0

docker build -t $name .
docker tag $name $name:$tag
docker push $name
