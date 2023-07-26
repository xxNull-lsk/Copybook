#!/bin/bash

echo "build for MacOS..."
flutter build macos --release --build-number ${curr} --build-name=${version}
if [ $? -ne 0 ]; then
    echo "Error: Do build for MacOS failed!"
    exit 1
fi

if [ ! -e ./build/macos/Build/Products/Release/字帖生成器.app ]; then
    echo "Error: Do build for MacOS failed!"
    exit 1
fi

rm -rf ./dist/字帖生成器.app
cp -rf ./build/macos/Build/Products/Release/字帖生成器.app ./dist/

rm -rf ~/Desktop/字帖生成器.app
cp -rf ./dist/字帖生成器.app ~/Desktop
exit 0
