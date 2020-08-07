#!/bin/bash -eux
VERSION=${GECKO_VERSION:-v0.27.0}
wget https://github.com/mozilla/geckodriver/releases/download/$VERSION/geckodriver-$VERSION-linux64.tar.gz
mkdir geckodriver
tar -xzf geckodriver-$VERSION-linux64.tar.gz -C geckodriver
./geckodriver/geckodriver --version