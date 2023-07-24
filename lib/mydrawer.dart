import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';

class MyDrawer extends StatefulWidget {
  const MyDrawer({Key? key}) : super(key: key);

  @override
  State<MyDrawer> createState() => _MyDrawerState();
}

class _MyDrawerState extends State<MyDrawer> {
  List pages = ["汉字", "拼音", "数字"];
  Map<String, String> pageIcon = {
    "汉字": "res/han1.png",
    "拼音": "res/pin1.png",
    "数字": "res/number1.png"
  };
  String mAppName = "";
  String mAppVersion = "";
  @override
  void initState() {
    super.initState();
    PackageInfo.fromPlatform().then((value) {
      mAppName = value.appName;
      mAppVersion = "${value.version} (${value.buildNumber})";
      mAppName = value.appName;
      setState(() {});
    });
  }

  Widget buildItem(BuildContext context, int index) {
    if (index >= pages.length) {
      return Container(
        color: Colors.white,
        margin: const EdgeInsets.all(5),
        child: ListTile(
            leading: const Icon(Icons.info),
            title: const Text("关于"),
            onTap: () {
              showAboutDialog(
                  applicationName: mAppName,
                  applicationVersion: mAppVersion,
                  applicationIcon: Image.asset("res/app.png"),
                  applicationLegalese: "这是一款免费开源的字帖生成软件。",
                  children: [
                    IconButton(
                      onPressed: () {
                        final Uri url =
                            Uri.parse('http://cloud.mydata.top:8080');
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
            }),
      );
    }
    String pageName = pages[index];
    return Container(
      color: Colors.white,
      margin: const EdgeInsets.all(5),
      child: ListTile(
          leading: Image.asset(pageIcon[pageName]!),
          title: Text(pageName),
          onTap: () => Navigator.pushNamed(context, pageName)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Drawer(
        child: Flex(direction: Axis.vertical, children: <Widget>[
      Expanded(
        child: ListView.builder(
            itemBuilder: buildItem, itemCount: pages.length + 1),
      ),
    ]));
  }
}
