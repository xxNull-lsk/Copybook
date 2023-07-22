import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

class Number {
  Color lineColor = const Color.fromRGBO(199, 238, 206, 1);
  List<Color> textColor = [Colors.grey.shade400, Colors.grey.shade400];
  int maxPageCount = -1;

  int colCount = 0;
  int rowCount = 0;

  double itemWidth = 1.5;
  double itemHeight = 1.5;
  double lineSpace = 0.8;
  double sideSpace = 1.2;
  double startX = 0;
  double startY = 0;
  double cm = 1;

  String fontName = "楷体";
  double fontSize = 28;
  double fontScan = 0;

  double pageWidth = 21;
  double pageHeight = 29.7;
  double docWidth = 0;
  double docHeight = 0;

  pw.Document pdf = pw.Document();
  final Map<String, dynamic> fonts;

  Number(this.fonts);

  Future<void> clac() async {
    pdf = pw.Document();
    var fontConfig = fonts[fontName];
    var fontData = await rootBundle.load("fonts/手写/${fontConfig["font_file"]}");
    final font = PdfTtfFont(pdf.document, fontData);
    pdf.document.fonts.add(font);
    cm = PdfPageFormat.cm;
    sideSpace = 0;

    Map<String, dynamic> cfg = fonts[fontName];
    if (cfg.containsKey("font_size")) {
      fontSize = cfg["font_size"].toDouble();
    }
    if (cfg.containsKey("font_scan")) {
      fontScan = cfg["font_scan"].toDouble();
    }

    docWidth = pageWidth - sideSpace * 2;
    docHeight = pageHeight - sideSpace * 2;

    colCount = docWidth ~/ itemWidth;
    rowCount = (docHeight + lineSpace) ~/ (itemHeight + lineSpace);

    docWidth = colCount * itemWidth;
    docHeight = rowCount * (itemHeight + lineSpace) - lineSpace;

    startX = (pageWidth - docWidth) / 2;
    startY = (pageHeight - docHeight) / 2;
  }

  Future<void> drawMutilateText(String str, {bool bSpaceLine = false}) async {
    await clac();
    if (bSpaceLine) {
      int count = colCount;
      String lineText = "";
      String spaceLine = "";
      for (var c = 0; c < count; c++) {
        spaceLine += ' ';
      }
      for (var i = 0; i < str.length; i += count) {
        int end = i + count;
        if (end > str.length) {
          end = str.length;
        }
        lineText += str.substring(i, end);
        lineText += spaceLine;
      }
      str = lineText;
    }
    doDrawText(str);
  }

  Future<void> drawTextPreLine(String str, {double repeat = 0}) async {
    await clac();
    int count = colCount;
    // 填充，每行数据
    String lineText = "";
    for (var i = 0; i < str.length; i++) {
      lineText += str[i];
      for (var c = 0; c < count - 1; c++) {
        if (c + 1 >= count * repeat) {
          lineText += ' ';
        } else {
          lineText += str[i];
        }
      }
    }
    doDrawText(lineText);
  }

  void doDrawText(String str) {
    int begin = 0, end = 0;
    int pageIndex = 0;
    while (
        begin < str.length && (pageIndex < maxPageCount || maxPageCount <= 0)) {
      pageIndex++;
      end = begin + colCount * rowCount;
      if (end > str.length) {
        end = str.length;
      }
      String strPage = str.substring(begin, end);
      pdf.addPage(pw.Page(
        build: (pw.Context context) {
          return pw.ConstrainedBox(
              constraints: const pw.BoxConstraints.expand(),
              child: pw.FittedBox(
                child: pw.CustomPaint(
                    size: PdfPoint(context.page.pageFormat.width,
                        context.page.pageFormat.height),
                    painter: (canvas, size) =>
                        onDrawMutilateText(strPage, canvas, size)),
              ));
        },
      ));
      begin = end;
    }
  }

  List<int> _pos(int index) {
    int row = 0, col = 0;
    row = index ~/ colCount;
    col = (index % colCount);
    index++;
    return [row, col];
  }

  void _drawNumber(PdfGraphics canvas, double x_, double y_) {
    // 绘制每列的竖线
    for (int col = 0; col < colCount; col++) {
      var y = pageHeight - y_ - itemHeight;
      var x = x_ + col * itemWidth;
      canvas.drawRect(x * cm, y * cm, itemWidth / 2 * cm, itemHeight * cm);
      canvas.setLineDashPattern([]);
      canvas.strokePath();
      y += itemHeight / 2;
      canvas.drawLine(x * cm, y * cm, (x + itemWidth / 2) * cm, y * cm);
      canvas.setLineDashPattern([2, 2], 0);
      canvas.strokePath();
    }
    canvas.strokePath();
  }

  void drawBank(PdfGraphics canvas) {
    canvas
      ..setStrokeColor(PdfColor(lineColor.red / 255.0, lineColor.green / 255.0,
          lineColor.blue / 255.0, lineColor.opacity))
      ..setLineWidth(0.5)
      ..setFillColor(PdfColors.black);
    for (int row = 0; row < rowCount; row++) {
      var x = startX;
      var y = startY + row * (itemHeight + lineSpace);
      _drawNumber(canvas, x, y);
    }
  }

  void onDrawMutilateText(String str, PdfGraphics canvas, PdfPoint size) {
    drawBank(canvas);
    for (int index = 0; index < str.length; index++) {
      var pos = _pos(index);
      var row = pos[0];
      var col = pos[1];
      var m = canvas.defaultFont?.stringMetrics(str[index]);
      var x = startX +
          col * itemWidth +
          (itemWidth / 2 - m!.advanceWidth * fontSize / cm) / 2;
      var y = pageHeight -
          row * (itemHeight + lineSpace) -
          itemHeight;

      // 设置文字颜色
      Color color;
      if (col < textColor.length) {
        color = textColor[col];
      } else {
        color = textColor[textColor.length - 1];
      }
      canvas.setFillColor(
          PdfColor(color.red / 255.0, color.green / 255.0, color.blue / 255.0));

      canvas.drawString(
          canvas.defaultFont!, fontSize, str[index], x * cm, y * cm);
    }
  }
}
