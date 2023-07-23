import 'package:flutter/material.dart';

import 'pages/hanzi.dart';
import 'pages/number.dart';
import 'pages/pinyin.dart';
import 'pages/preview.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '字帖生成器',
      theme: ThemeData(
        // This is the theme of your application.
        //
        // Try running your application with "flutter run". You'll see the
        // application has a blue toolbar. Then, without quitting the app, try
        // changing the primarySwatch below to Colors.green and then invoke
        // "hot reload" (press "r" in the console where you ran "flutter run",
        // or simply save your changes to "hot reload" in a Flutter IDE).
        // Notice that the counter didn't reset back to zero; the application
        // is not restarted.
        primarySwatch: Colors.blue,
      ),
      home: const HanZiPage("汉字"),
        routes: {
          "汉字":(context) => const HanZiPage("汉字"),
          "拼音":(context) => const PinYinPage("拼音"),
          "数字":(context) => const NumberPage("数字"),
          "preview":(context) {
            Map<String,dynamic>? argv =
                ModalRoute.of(context)?.settings.arguments as Map<String,dynamic>?;
                
            return PreviewPage(argv!["title"], argv["pdf"]);
          }
        }
    );
  }
}