import 'package:flutter/material.dart';
import 'package:copybook/pages/hanzi.dart';
import 'package:copybook/pages/number.dart';
import 'package:copybook/pages/pinyin.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:package_info_plus/package_info_plus.dart';

class MyNavigationInfo {
  List pages = ["汉字", "拼音", "数字", "关于"];
  Map<String, dynamic> pagesInfo = {
    "汉字": {
      "title": "汉字字帖",
      "icon": Image.asset("res/han1.png"),
      "page": const HanZiPage("汉字字帖"),
    },
    "拼音": {
      "title": "拼音字帖",
      "icon": Image.asset("res/pin1.png"),
      "page": const PinYinPage("拼音字帖"),
    },
    "数字": {
      "title": "数字字帖",
      "icon": Image.asset("res/number1.png"),
      "page": const NumberPage("数字字帖"),
    },
    "关于": {
      "title": "关于",
      "icon": const Icon(
        Icons.info,
        color: Colors.blue,
      ), //Image.asset("res/app.png", width: 32, height: 32),
      "page": null,
    },
  };
  String mAppName = "";
  String mAppVersion = "";

  Future<void> init() async {
    var value = await PackageInfo.fromPlatform();
    mAppName = value.appName;
    mAppVersion = "${value.version} (${value.buildNumber})";
    mAppName = value.appName;
  }

  void showAbout(BuildContext context) {
    showAboutDialog(
        applicationName: mAppName,
        applicationVersion: mAppVersion,
        applicationIcon: Image.asset("res/app.png"),
        applicationLegalese: "这是一款免费开源的字帖生成软件。",
        children: [
          IconButton(
            onPressed: () {
              final Uri url = Uri.parse('http://cloud.mydata.top:8080');
              launchUrl(url);
            },
            icon: const Text("关于我"),
          ),
          IconButton(
            onPressed: () {
              final Uri url =
                  Uri.parse('mailto:xxnull@163.com?subject=copybook');
              launchUrl(url);
            },
            icon: const Text("联系我"),
          )
        ],
        context: context);
  }
}
