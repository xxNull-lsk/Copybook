#!/bin/bash
export DIR=`pwd`
export curr=`date +%Y%m%d`

if [ ! -f ".major_version" ]; then
    echo "1" > .major_version
fi
major_version=`cat .major_version`
if [ ! -f ".minor_version" ]; then
    echo "0" > .minor_version
fi
minor_version=`cat .minor_version`
if [ ! -f ".fixed_version" ]; then
    echo "0" > .fixed_version
fi
fixed_version=`cat .fixed_version`

export version=${major_version}.${minor_version}.${fixed_version}
mkdir dist > /dev/null 2>&1

os=`uname`
if [ "$os" == "Darwin" ]; then
    bash ./build_macos.sh
    ret=$?
    exit $ret
elif [ "$os" == "Linux" ]; then
    bash ./build_linux.sh
    ret=$?
    exit $ret
fi

next_fixed_version=$((fixed_version+1))
echo $next_fixed_version > .fixed_version
exit 0
