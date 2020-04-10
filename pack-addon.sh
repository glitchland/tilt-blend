#!/usr/bin/env bash

# sync submodule
git submodule update --remote 

# copy dependency from submodule 
cp tilt-brush-toolkit/Python/tiltbrush/tilted.py tiltblend/