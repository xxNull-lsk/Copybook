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
git tag v$version
git push --tags
bash ./build.sh


scp dist/copybook_${version}.apk allan@10.0.2.9:/mnt/zhanmei/nas/allan/我的软件/copybook/
scp ${DIR}/dist/copybook_${version}_linux_x64.tar.gz allan@10.0.2.9:/mnt/zhanmei/nas/allan/我的软件/copybook/

scp dist/copybook_${version}_linux_x64.deb allan@10.0.2.9:/mnt/zhanmei/nas/allan/我的软件/copybook/
echo "Upload succeed."

exit 0
