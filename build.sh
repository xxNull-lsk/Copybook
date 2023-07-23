#!/bin/bash
DIR=`pwd`
curr=`date +%Y%m%d`

version=1.0.7
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
tar -czf copy_book_x64_${version}_${curr}.tar.gz copybook
mv copy_book_x64_${version}_${curr}.tar.gz ${DIR}/dist/
scp ${DIR}/dist/copy_book_x64_${version}_${curr}.tar.gz allan@10.0.2.9:/mnt/zhanmei/nas/allan/Tools/Android/myself/

cd ${DIR}
sed -i "s/^Version:.*/Version:${version}/g" ./deb/DEBIAN/control
dpkg -b deb dist/copybook_linux_x64_${version}.deb
rm -rf deb/opt/copybook/*
sed -i "s/^Version:.*/Version:0.0.0/g" deb/DEBIAN/control

scp dist/copybook_linux_x64_${version}.deb allan@10.0.2.9:/mnt/zhanmei/nas/allan/Tools/Android/myself/
echo "Upload linux application succeed."

exit 0
