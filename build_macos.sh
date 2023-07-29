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
cd ./dist
tar -czf copybook_${version}_macos_x64.tar.gz 字帖生成器.app
scp copybook_1.0.1083_macos_x64.tar.gz allan@10.0.2.9:/media/zhanmei/nas/allan/我的软件/copybook
exit 0
