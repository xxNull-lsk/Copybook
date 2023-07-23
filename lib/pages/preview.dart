import 'dart:io';

import 'package:flutter/material.dart';

import '../mydrawer.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

class PreviewPage extends StatefulWidget {
  const PreviewPage(this.title, this.pdf, {super.key});
  final String title;
  final pw.Document pdf;

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  @override
  State<PreviewPage> createState() => _PreviewPageState();
}

class _PreviewPageState extends State<PreviewPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Platform.isLinux || Platform.isWindows || Platform.isMacOS
                ? IconButton(
                    icon: const Icon(Icons.arrow_back),
                    onPressed: () => Navigator.pop(context),
                  )
                : const SizedBox(width: 0),
            Platform.isLinux || Platform.isWindows || Platform.isMacOS
                ? const SizedBox(width: 18)
                : const SizedBox(width: 0),
            Text(widget.title),
          ],
        ),
      ),
      drawer: const MyDrawer(),
      body: PdfPreview(
        build: (format) => widget.pdf.save(),
        canChangePageFormat: false,
        canChangeOrientation: false,
        canDebug: false,
      ),
    );
  }
}