# 安装方法

## 安装依赖包

```bash
pip3 install -r requirements.txt
```

## 运行程序

```bas
python3 main.py
```



# 拼音字帖

按照要求生成拼音字帖。

![拼音界面](./readme.res/pinyin.png)

1. 线条颜色

   可以指定四线格的颜色。

2. 文字颜色

   四线格中拼音的颜色。

3. 样式

   生成PDF的样式

   - 全描字：除首列，整行都会生成拼音。
   - 半描字：除首列，一半生成拼音，一半留空。
   - 不描字：除首列，全部留空。
   - 普通：一个格子一个拼音依次输出。

4. 声调

   方便生成带声调的拼音。

5. 拼音

   生成的PDF中的拼音内容，每个拼音已空格隔开。

   ## 生成的拼音字帖

   ![](./readme.res/pinyin-pdf.png)

# 汉字字帖

![](./readme.res/hanzi.png)

1. 线条颜色

   可以指定方格的颜色。

2. 文字颜色

   可以指定文字的颜色。

3. 字体

   可以指定文字的字体。

3. 样式

   生成PDF的样式

   - 全描字：除首列，整行都会生成文字。
   - 半描字：除首列，一半生成文字，一半留空。
   - 不描字：除首列，全部留空。
   - 普通：一个格子一个汉字依次输出。

   

4. 内容

   生成的PDF中的文字内容。
   
   ![](./readme.res/hanzi-pdf1.png)

![](./readme.res/hanzi-pdf2.png)



# 开发

http://home.mydata.top:8093/?cat=10