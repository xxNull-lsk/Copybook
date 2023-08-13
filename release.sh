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

read -p "版本号：$version 确定要发布版本？[Y]:"  ret
if [ "$ret" != "Y" ]; then
    echo "已取消"
    exit 1
fi

git add .
git commit -m "Release:$version"
git push
git tag v$version
git push --tags

bash ./build.sh


scp -P 6302 dist/copybook_${version}.apk allan@home.mydata.top:/mnt/zhanmei/nas/allan/我的软件/copybook/
scp -P 6302 ${DIR}/dist/copybook_${version}_linux_x64.tar.gz allan@home.mydata.top:/mnt/zhanmei/nas/allan/我的软件/copybook/

scp -P 6302 dist/copybook_${version}_linux_x64.deb allan@home.mydata.top:/mnt/zhanmei/nas/allan/我的软件/copybook/
echo "Upload succeed."

exit 0
