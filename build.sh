mv res/bin .
pyinstaller Copybook.spec
mv ./bin res/

cd dist
version=`./CopyBook -v`
cp -f CopyBook ../deb/opt/copy_book
cp ../LICENSE .
tar -czf copy_book_x64_${version}.tar.gz CopyBook LICENSE

cd ..
cp LICENSE deb/opt/copy_book
sed -i "s/^Version:.*/Version:${version}/g" deb/DEBIAN/control
dpkg -b deb dist/copy_book_linux_x64_${version}.deb
rm deb/opt/copy_book/CopyBook
rm deb/opt/copy_book/LICENSE
sed -i "s/^Version:.*/Version:0.0.0/g" deb/DEBIAN/control
