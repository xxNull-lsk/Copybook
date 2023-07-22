import 'package:flutter/material.dart';

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
  @override
  void initState() {
    super.initState();
  }

  Widget buildItem(BuildContext context, int index) {
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
        child:
            ListView.builder(itemBuilder: buildItem, itemCount: pages.length),
      ),
    ]));
  }
}
