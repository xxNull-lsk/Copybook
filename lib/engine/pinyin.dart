import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

class PinYin {
  Color lineColor = const Color.fromRGBO(199, 238, 206, 1);
  List<Color> textColor = [Colors.grey.shade400, Colors.grey.shade400];
  bool mShowHanzi = false;
  int maxPageCount = -1;

  int colCount = 0;
  int rowCount = 0;

  double itemWidth = 1.5;
  double itemHeight = 1.5;
  double lineSpace = 0.8;
  double sideSpace = 1.2;
  double lineHanzi = 0;
  double startX = 0;
  double startY = 0;
  double cm = 1;

  double fontSize = 28;
  double fontScan = 0.86;

  double pageWidth = 21;
  double pageHeight = 29.7;
  double docWidth = 0;
  double docHeight = 0;

  pw.Document pdf = pw.Document();

  Future<void> clac() async {
    pdf = pw.Document();
    var fontData = await rootBundle.load("fonts/拼音/汉语拼音.ttf");
    final font = PdfTtfFont(pdf.document, fontData);
    pdf.document.fonts.add(font);
    cm = PdfPageFormat.cm;
    sideSpace = 0;

    docWidth = pageWidth - sideSpace * 2;
    docHeight = pageHeight - sideSpace * 2;

    if (mShowHanzi) {
      lineHanzi = 2.0;
      itemWidth = 2.0;
      fontSize = 18;
      itemHeight = 0.9;
      fontScan = 1;
      lineSpace = 0.2;
    } else {
      lineHanzi = 0;
      fontSize = 28;
      itemHeight = 1.5;
      itemWidth = 2.5;
      fontScan = 0.12;
      lineSpace = 0.8;
    }
    colCount = docWidth ~/ itemWidth;
    rowCount = (docHeight + lineSpace) ~/ (itemHeight + lineHanzi + lineSpace);

    docWidth = colCount * itemWidth;
    docHeight = rowCount * (itemHeight + lineHanzi + lineSpace) - lineSpace;

    startX = (pageWidth - docWidth) / 2;
    startY = (pageHeight - docHeight) / 2;
  }

  Future<void> drawMutilateText(List<String> str,
      {bool bSpaceLine = false}) async {
    await clac();
    if (bSpaceLine) {
      int count = colCount;

      List<String> lineText = [];
      List<String> spaceLine = [];
      for (var c = 0; c < count; c++) {
        spaceLine.add(' ');
      }
      for (var i = 0; i < str.length; i += count) {
        int end = i + count;
        if (end > str.length) {
          end = str.length;
        }
        lineText += str.sublist(i, end);
        lineText.addAll(spaceLine);
      }
      str = lineText;
    }
    doDrawText(str);
  }

  Future<void> drawTextPreLine(List<String> txt, {double repeat = 0}) async {
    await clac();
    int count = colCount;
    // 填充，每行数据
    List<String> lineText = [];
    for (var i = 0; i < txt.length; i++) {
      lineText.add(txt[i]);
      for (var c = 0; c < count - 1; c++) {
        if (c + 1 >= count * repeat) {
          lineText.add(' ');
        } else {
          lineText.add(txt[i]);
        }
      }
    }
    doDrawText(lineText);
  }

  void doDrawText(List<String> str) {
    int begin = 0, end = 0;
    int pageIndex = 0;
    while (
        begin < str.length && (pageIndex < maxPageCount || maxPageCount <= 0)) {
      pageIndex++;
      end = begin + colCount * rowCount;
      if (end > str.length) {
        end = str.length;
      }
      List<String> strPage = str.sublist(begin, end);
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

  void _drawFang(PdfGraphics canvas, double x_, double y_) {
    var y = pageHeight - y_ - lineHanzi;
    // 绘制每列的竖线
    for (int col = 0; col < colCount; col++) {
      var x = x_ + col * lineHanzi;
      canvas.drawLine(x * cm, y * cm, x * cm, (y + lineHanzi) * cm);
    }
    canvas.drawRect(x_ * cm, y * cm, docWidth * cm, lineHanzi * cm);
    canvas.setLineDashPattern([]);
    canvas.strokePath();
  }

  void _drawPinYin(PdfGraphics canvas, double x_, double y_) {
    var x = x_;
    var y = pageHeight - y_ - itemHeight;

    canvas.drawLine(x * cm, y * cm, (docWidth + x) * cm, y * cm);
    canvas.setLineDashPattern([]);
    canvas.strokePath();

    y += itemHeight / 3;
    canvas.drawLine(x * cm, y * cm, (docWidth + x) * cm, y * cm);
    y += itemHeight / 3;

    canvas.drawLine(x * cm, y * cm, (docWidth + x) * cm, y * cm);
    canvas.setLineDashPattern(<int>[3, 3], 0);
    canvas.strokePath();

    y += itemHeight / 3;
    canvas.drawLine(x * cm, y * cm, (docWidth + x) * cm, y * cm);

    y = pageHeight - y_ - itemHeight;
    for (int col = 0; col < colCount + 1; col++) {
      double x = x_ + itemWidth * col;
      canvas.drawLine(x * cm, y * cm, x * cm, (y + itemHeight) * cm);
    }
    canvas.setLineDashPattern([]);
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
      var y = startY + row * (itemHeight + lineHanzi + lineSpace);
      if (row == 0) {
        canvas.setStrokeColor(PdfColors.amber);
      } else {
        canvas.setStrokeColor(PdfColors.red);
      }
      _drawPinYin(canvas, x, y);
      y += itemHeight;
      if (mShowHanzi) {
        _drawFang(canvas, x, y);
      }
    }
  }

  void onDrawMutilateText(List<String> str, PdfGraphics canvas, PdfPoint size) {
    drawBank(canvas);
    for (int index = 0; index < str.length; index++) {
      var pos = _pos(index);
      var row = pos[0];
      var col = pos[1];
      var m = canvas.defaultFont?.stringMetrics(str[index]);
      var x =
          startX + col * itemWidth + (itemWidth - m!.width * fontSize / cm) / 2;
      var y = pageHeight -
          row * (itemHeight + lineHanzi + lineSpace) -
          itemHeight * fontScan -
          m!.maxHeight * fontSize / cm;

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
