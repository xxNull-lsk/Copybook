#!/bin/bash
DIR=`pwd`
curr=`date +%Y%m%d`

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


version=${major_version}.${minor_version}.${fixed_version}
mkdir dist > /dev/null 2>&1

flutter build apk --release --build-number ${curr} --build-name=${version}
if [ $? -ne 0 ]; then
    echo "Error: Do build for android failed!"
    exit 1
fi

cp build/app/outputs/apk/release/app-release.apk dist/copybook_${version}_$curr.apk
scp dist/copybook_${version}_$curr.apk allan@10.0.2.9:/mnt/zhanmei/nas/allan/Tools/Android/myself/
echo "Upload android application succeed."


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
scp ${DIR}/dist/copybook_${version}_linux_x64.tar.gz allan@10.0.2.9:/mnt/zhanmei/nas/allan/Tools/Android/myself/

cd ${DIR}
sed -i "s/^Version:.*/Version:${version}/g" ./deb/DEBIAN/control
dpkg -b deb dist/copybook_${version}_linux_x64.deb
rm -rf deb/opt/copybook/*
sed -i "s/^Version:.*/Version:0.0.0/g" deb/DEBIAN/control

scp dist/copybook_${version}_linux_x64.deb allan@10.0.2.9:/mnt/zhanmei/nas/allan/Tools/Android/myself/
echo "Upload linux application succeed."

exit 0
