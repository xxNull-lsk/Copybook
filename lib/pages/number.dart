import 'dart:convert';
import 'dart:io';

import 'package:copybook/engine/number.dart';
import 'package:copybook/mydrawer.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:printing/printing.dart';

class NumberPage extends StatefulWidget {
  const NumberPage(this.title, {super.key});
  final String title;

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  @override
  State<NumberPage> createState() => _NumberPageState();
}

class _NumberPageState extends State<NumberPage> {
  Map<String, Color> mLineColorItems = {
    '粉色': Colors.pinkAccent,
    '浅绿': Colors.lightGreen,
    '黑色': Colors.black,
  };
  Map<String, List<Color>> mTextColorsItems = {
    '全部粉色': [Colors.pink, Colors.pink],
    '首列粉色，其余浅灰': [Colors.pink, Colors.grey.shade400],
    '全部浅绿': [Colors.lightGreen, Colors.lightGreen],
    '首列浅绿，其余浅灰': [Colors.lightGreen, Colors.grey.shade400],
    '全部黑色': [Colors.black, Colors.black],
    '首列黑色，其余浅灰': [Colors.black, Colors.grey.shade400],
    '全部浅灰': [Colors.grey.shade400, Colors.grey.shade400],
  };

  Number mNumber = Number(<String, dynamic>{});
  List<DropdownMenuItem<String>> mFontItems = [];
  Map<String, dynamic> mConfig = {};
  Map<String, dynamic> mFonts = {};

  String mFontName = '楷体';
  String mLineColor = '粉色';
  String mTextColor = "全部粉色";
  String mCopybookType = '常规';
  bool mShowHanzi = false;
  String mText = "";
  String mShengDiao = "ā á ǎ à    ō ó ǒ ò\n"
      "ē é ě è    ī  í  ǐ  ì\n"
      "ū ú ǔ ù    ǖ ǘ ǚ ǜ";

  Uint8List mImageData = ByteData(0).buffer.asUint8List();
  final TextEditingController mTextEditingController = TextEditingController();
  @override
  void initState() {
    super.initState();
    rootBundle.load("res/pdf.jpg").then((value) {
      mImageData = value.buffer.asUint8List();
      setState(() {});
    });

    rootBundle.loadString("fonts/数字.json").then((value) {
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
            padding: const EdgeInsets.only(left: 20, right: 20, top: 10),
            child: SizedBox(
              width: MediaQuery.of(context).size.width,
              child: layout,
            ));
      }),
    );
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

  Widget getTextField() {
    return Container(
      padding: const EdgeInsets.fromLTRB(0, 24, 0, 12),
      child: TextField(
        maxLines: null,
        keyboardType: TextInputType.number,
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

  Container getPreviewImage({double? maxWidthImage}) {
    return Container(
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
      child: mImageData.isNotEmpty ? Image.memory(mImageData) : Container(),
    );
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
            Row(children: buildTextColor()),
            Row(children: buildCopybookType()),
            Row(children: buildTextFont()),
            getTextField(),
          ]),
        ),
        getPreviewImage(maxWidthImage: maxWidthImage)
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
            Row(children: buildTextColor()),
            Row(children: buildCopybookType()),
            Row(children: buildTextFont()),
            getTextField(),
          ]),
        ),
        Expanded(flex: 1, child: getPreviewImage())
      ],
    );
  }

  // 竖屏布局
  Widget getPortraitLayout() {
    return Column(children: [
      getPreviewImage(),
      Row(children: buildLineColor()),
      Row(children: buildTextColor()),
      Row(children: buildCopybookType()),
      Row(children: buildTextFont()),
      getTextField(),
    ]);
  }

  void doSave() {
    flushImage(maxPageCount: -1);
    Navigator.pushNamed(context, "preview", arguments: {
      "title": widget.title,
      "pdf": mNumber.mPdf,
    });
  }

  void flushImage({maxPageCount = 1}) async {
    mNumber = Number(mFonts);
    mNumber.mFontName = mFontName;
    mNumber.mLineColor = mLineColorItems[mLineColor]!;
    mNumber.mTextColor = mTextColorsItems[mTextColor]!;
    mNumber.mMaxPageCount = maxPageCount;
    switch (mCopybookType) {
      case "不描字":
        await mNumber.drawTextPreLine(mText);
        break;
      case "全描字":
        await mNumber.drawTextPreLine(mText, repeat: 1);
        break;
      case "半描字":
        await mNumber.drawTextPreLine(mText, repeat: 0.5);
        break;
      case "隔行":
        {
          await mNumber.drawMutilateText(mText, bSpaceLine: true);
        }
        break;

      default: //"常规"
        {
          await mNumber.drawMutilateText(mText);
        }
    }
    var pdfData = await mNumber.mPdf.save();
    await for (var page in Printing.raster(pdfData, pages: [0])) {
      mImageData = await page.toPng();
      setState(() {});
    }
  }
}
