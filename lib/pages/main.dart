import 'package:flutter/material.dart';

import 'package:copybook/pages/mynavigationinfo.dart';

class MainPage extends StatefulWidget {
  const MainPage({super.key});

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  @override
  State<MainPage> createState() => _MainPageState();
}

class _MainPageState extends State<MainPage> with MyNavigationInfo {
  int currentIndex = 0;
  @override
  void initState() {
    super.initState();
    init().then((value) {
      setState(() {});
    });
  }

  BottomNavigationBar buildBottomNavigationBar(BuildContext context) {
    List<BottomNavigationBarItem> items = [];
    for (var page in pages) {
      var info = pagesInfo[page];
      items.add(
        BottomNavigationBarItem(
          icon: info["icon"],
          label: info["title"],
          tooltip: info["title"],
        ),
      );
    }
    return BottomNavigationBar(
      items: items,
      currentIndex: currentIndex,
      selectedItemColor: Colors.blue,
      onTap: (int i) {
        if (i == pages.length - 1) {
          showAbout(context);
          return;
        }
        currentIndex = i;
        setState(() {});
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: buildBottomNavigationBar(context),
      body: pagesInfo[pages[currentIndex]]["page"],
    );
  }
}
