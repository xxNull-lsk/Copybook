#!/bin/bash

echo "build for android..."
flutter build apk --release --build-number ${curr} --build-name=${version}
if [ $? -ne 0 ]; then
    echo "Error: Do build for android failed!"
    exit 1
fi

cp build/app/outputs/apk/release/app-release.apk dist/copybook_${version}.apk


echo "build for linux..."
flutter build linux --release --build-number ${curr} --build-name=${version}
if [ $? -ne 0 ]; then
    echo "Error: Do Build failed!"
    exit 1
fi

cp -rf build/linux/x64/release/bundle/* ./deb/opt/copybook
cp ./LICENSE ./deb/opt/copybook
cd ./deb/opt/
tar -czf copybook_${version}_linux_x64.tar.gz copybook
mv copybook_${version}_linux_x64.tar.gz ${DIR}/dist/

cd ${DIR}
sed -i "s/^Version:.*/Version:${version}/g" ./deb/DEBIAN/control
dpkg -b deb dist/copybook_${version}_linux_x64.deb
rm -rf deb/opt/copybook/*
sed -i "s/^Version:.*/Version:0.0.0/g" deb/DEBIAN/control


exit 0
