import 'dart:convert';
import 'dart:io';

import 'package:copybook/engine/hanzi.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:printing/printing.dart';

import '../mydrawer.dart';

class HanZiPage extends StatefulWidget {
  const HanZiPage(this.title, {super.key});
  final String title;

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  @override
  State<HanZiPage> createState() => _HanZiPageState();
}

class _HanZiPageState extends State<HanZiPage> {
  Map<String, dynamic> mConfig = {};
  Map<String, dynamic> mFonts = {};
  List<DropdownMenuItem<String>> mFontItems = [];
  String mText = "";
  HanZi mHanZi = HanZi(<String, dynamic>{});
  Map<String, List<Color>> mTextColorsItems = {
    '全部粉色': [Colors.pink, Colors.pink],
    '首列粉色，其余浅灰': [Colors.pink, Colors.grey.shade400],
    '全部浅绿': [Colors.lightGreen, Colors.lightGreen],
    '首列浅绿，其余浅灰': [Colors.lightGreen, Colors.grey.shade400],
    '全部黑色': [Colors.black, Colors.black],
    '首列黑色，其余浅灰': [Colors.black, Colors.grey.shade400],
    '全部浅灰': [Colors.grey.shade400, Colors.grey.shade400],
  };

  Map<String, Color> mLineColorItems = {
    '粉色': Colors.pinkAccent,
    '浅绿': Colors.lightGreen,
    '黑色': Colors.black,
  };

  String mFontName = '楷体';
  String mLineColor = '粉色';
  GridType mGridType = GridType.gridTypeFang;
  String mTextColor = "全部粉色";
  String mCopybookType = '常规';
  bool mShowPinyin = false;
  Uint8List mImageData = ByteData(0).buffer.asUint8List();
  final TextEditingController mTextEditingController = TextEditingController();
  @override
  void initState() {
    super.initState();
    mTextEditingController.text = mText;
    rootBundle.load("res/pdf.jpg").then((value) {
      mImageData = value.buffer.asUint8List();
      setState(() {});
    });

    rootBundle.loadString("fonts/手写.json").then((value) {
      mConfig = jsonDecode(value);
      mFonts = mConfig["fonts"];
      mText = mConfig["text"];
      mFontName = mConfig["default"];
      mFontItems.clear();
      mTextEditingController.text = mText;
      for (var item in mFonts.keys) {
        mFontItems.add(DropdownMenuItem(
          value: item,
          child: Text(item),
        ));
      }
      flushImage();
    });
  }

  void doSave() {
    flushImage(maxPageCount: -1);
    Navigator.pushNamed(context, "preview", arguments: {
      "title": widget.title,
      "pdf": mHanZi.mPdf,
    });
  }

  dynamic getLineColors() {
    List<DropdownMenuItem<String>> dropItems = [];
    for (var item in mLineColorItems.keys) {
      dropItems.add(DropdownMenuItem(
        value: item,
        child: Text(
          item,
          style: TextStyle(color: mLineColorItems[item]),
        ),
      ));
    }
    return dropItems;
  }

  List<Widget> buildLineColor() {
    return [
      const Text("线条颜色："),
      DropdownButton<String>(
        hint: const Text('请选择线条颜色'),
        items: getLineColors(),
        value: mLineColor,
        onChanged: (String? value) {
          setState(() {
            mLineColor = value!;
          });
          flushImage();
        },
      ),
    ];
  }

  dynamic getGridTypes() {
    Map<String, GridType> items = {
      '方格': GridType.gridTypeFang,
      '田字格': GridType.gridTypeTian,
      '米字格': GridType.gridTypeMi,
      '回字格': GridType.gridTypeHui,
      '竖线格': GridType.gridTypeVertical,
    };
    List<DropdownMenuItem<GridType>> dropItems = [];
    for (var item in items.keys) {
      dropItems.add(DropdownMenuItem(
        value: items[item],
        child: Text(item),
      ));
    }
    return dropItems;
  }

  List<Widget> buildGridType() {
    return [
      const Text("方格类型："),
      DropdownButton<GridType>(
        hint: const Text('请选择方格类型'),
        items: getGridTypes(),
        value: mGridType,
        onChanged: (GridType? value) {
          setState(() {
            mGridType = value!;
          });
          flushImage();
        },
      ),
    ];
  }

  List<DropdownMenuItem<dynamic>> getTextColors() {
    List<DropdownMenuItem<String>> dropItems = [];
    for (var item in mTextColorsItems.keys) {
      dropItems.add(DropdownMenuItem(
        value: item,
        child: Text(item),
      ));
    }
    return dropItems;
  }

  List<Widget> buildTextColor() {
    return [
      const Text("文字颜色："),
      DropdownButton<dynamic>(
        hint: const Text('请选择文字颜色'),
        items: getTextColors(),
        value: mTextColor,
        onChanged: (dynamic value) {
          setState(() {
            mTextColor = value!;
          });
          flushImage();
        },
      ),
    ];
  }

  List<Widget> buildTextFont() {
    return [
      const Text("文字字体："),
      DropdownButton<String>(
        hint: const Text('请选择字体'),
        items: mFontItems,
        value: mFontName,
        onChanged: (String? value) {
          setState(() {
            mFontName = value!;
          });
          flushImage();
        },
      ),
    ];
  }

  List<DropdownMenuItem<String>> getCopybookTypes() {
    List<String> items = ['常规', '不描字', '半描字', '全描字', '隔行'];
    List<DropdownMenuItem<String>> dropItems = [];
    for (var item in items) {
      dropItems.add(DropdownMenuItem(
        value: item,
        child: Text(item),
      ));
    }
    return dropItems;
  }

  List<Widget> buildCopybookType() {
    return [
      const Text("字帖样式："),
      DropdownButton<dynamic>(
        hint: const Text('请选择字帖样式'),
        items: getCopybookTypes(),
        value: mCopybookType,
        onChanged: (dynamic value) {
          setState(() {
            mCopybookType = value!;
          });
          flushImage();
        },
      ),
    ];
  }

  List<Widget> buildPinyin() {
    return [
      Row(children: [
        const Text("看汉字写拼音："),
        Switch(
            value: mShowPinyin,
            onChanged: (bool? value) {
              setState(() {
                mShowPinyin = value!;
              });
              flushImage();
            })
      ]),
    ];
  }

  void flushImage({maxPageCount = 1}) async {
    mHanZi = HanZi(mFonts);
    mHanZi.mFontName = mFontName;
    mHanZi.mGridType = mGridType;
    mHanZi.mLineColor = mLineColorItems[mLineColor]!;
    mHanZi.mTextColor = mTextColorsItems[mTextColor]!;
    mHanZi.mShowPinyin = mShowPinyin;
    mHanZi.mMaxPageCount = maxPageCount;
    switch (mCopybookType) {
      case "不描字":
        await mHanZi.drawTextPreLine(mText);
        break;
      case "全描字":
        await mHanZi.drawTextPreLine(mText, repeat: 1);
        break;
      case "半描字":
        await mHanZi.drawTextPreLine(mText, repeat: 0.5);
        break;
      case "隔行":
        {
          await mHanZi.drawMutilateText(mText, bSpaceLine: true);
        }
        break;

      default: //"常规"
        {
          await mHanZi.drawMutilateText(mText);
        }
    }
    var pdfData = await mHanZi.mPdf.save();
    await for (var page in Printing.raster(pdfData, pages: [0])) {
      mImageData = await page.toPng();
      setState(() {});
    }
  }

  Widget getTextField() {
    return Container(
      padding: const EdgeInsets.all(12),
      child: TextField(
        maxLines: null,
        controller: mTextEditingController,
        onChanged: (value) {
          mText = value;
          mTextEditingController.value = TextEditingValue(
            text: value,
            selection: TextSelection.fromPosition(TextPosition(
                affinity: TextAffinity.downstream, offset: value.length)),
          );
          flushImage();
        },
        decoration: const InputDecoration(
          labelText: "字帖内容",
          border: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(8)),
          ),
        ),
      ),
    );
  }

  Container getPreviewImage({double? maxWidthImage}) {
    return mImageData.isNotEmpty ? Container(
      width: maxWidthImage,
      margin: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(
          color: Colors.grey,
          width: 1,
        ),
        borderRadius: BorderRadius.circular(8.0),
        boxShadow: const [
          BoxShadow(
            color: Colors.black,
            offset: Offset(
              5.0,
              5.0,
            ), //Offset
            blurRadius: 10.0,
            spreadRadius: 2.0,
          ), //BoxShadow
          BoxShadow(
            color: Colors.white,
            offset: Offset(0.0, 0.0),
            blurRadius: 0.0,
            spreadRadius: 0.0,
          ), //BoxShadow
        ],
      ),
      alignment: Alignment.topCenter,
      child: Image.memory(mImageData),
    ) : Container();
  }

  // 桌面布局
  Widget getDesktopLayout() {
    double maxWidth = MediaQuery.of(context).size.width - 700;
    double maxWidthImage = 500;
    if (maxWidth < 400) {
      maxWidth = MediaQuery.of(context).size.width;
      maxWidthImage = MediaQuery.of(context).size.width;
    }
    return Wrap(
      spacing: 30,
      children: [
        ConstrainedBox(
          constraints: BoxConstraints(minWidth: 400, maxWidth: maxWidth),
          child: Wrap(children: [
            Row(children: buildLineColor()),
            Row(children: buildGridType()),
            Row(children: buildTextColor()),
            Row(children: buildTextFont()),
            Row(children: buildCopybookType()),
            Row(children: buildPinyin()),
            getTextField(),
          ]),
        ),
        getPreviewImage(maxWidthImage:maxWidthImage)
      ],
    );
  }

  // 横屏布局
  Widget getLandscapeLayout() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 1,
          child: Column(children: [
            Row(children: buildLineColor()),
            Row(children: buildGridType()),
            Row(children: buildTextColor()),
            Row(children: buildTextFont()),
            Row(children: buildCopybookType()),
            Row(children: buildPinyin()),
            getTextField(),
          ]),
        ),
        Expanded(flex: 1, child: getPreviewImage())
      ],
    );
  }

  // 竖屏布局
  Widget getPortraitLayout() {
    return Column(
      children: [
        getPreviewImage(),
        Row(children: buildLineColor()),
        Row(children: buildGridType()),
        Row(children: buildTextColor()),
        Row(children: buildTextFont()),
        Row(children: buildCopybookType()),
        Row(children: buildPinyin()),
        getTextField(),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            onPressed: doSave,
            icon: const Icon(Icons.save),
          ),
          const SizedBox(
            width: 20,
          )
        ],
      ),
      drawer: const MyDrawer(),
      body: OrientationBuilder(
          builder: (BuildContext context, Orientation orientation) {
        Widget layout;
        if (Platform.isAndroid || Platform.isIOS || Platform.isFuchsia) {
          layout = orientation == Orientation.landscape
              ? getLandscapeLayout()
              : getPortraitLayout();
        } else {
          layout = getDesktopLayout();
        }
        return SingleChildScrollView(
            padding:
                const EdgeInsets.only(left: 20, right: 20, top: 10, bottom: 20),
            child: SizedBox(
              width: MediaQuery.of(context).size.width,
              child: layout,
            ));
      }),
    );
  }
}