import 'package:copybook/pages/mynavigationinfo.dart';
import 'package:flutter/material.dart';

class MyDrawer extends StatefulWidget {
  const MyDrawer({Key? key}) : super(key: key);

  @override
  State<MyDrawer> createState() => _MyDrawerState();
}

class _MyDrawerState extends State<MyDrawer> with MyNavigationInfo {
  @override
  void initState() {
    super.initState();
    init().then((value) {
      setState(() {});
    });
  }

  Widget buildItem(BuildContext context, int index) {
    String pageName = pages[index];
    return Container(
      color: Colors.white,
      margin: const EdgeInsets.all(5),
      child: ListTile(
          leading: pagesInfo[pageName]["icon"],
          title: Text(pageName),
          onTap: () {
            if (pageName == "关于"){
              showAbout(context);
              return;
            }
            Navigator.pushNamed(context, pageName);
          }),
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
