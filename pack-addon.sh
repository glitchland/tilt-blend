#!/usr/bin/env bash

# sync submodule
git submodule update --remote 

# copy dependency from submodule 
cp tilt-brush-toolkit/Python/tiltbrush/tilted.py tiltblend/

# create the addon archive (its just a simple zip)
rm tiltblend.zip 2>/dev/null
zip -r tiltblend.zip tiltblend -x "tiltblend/__pycache__/*"