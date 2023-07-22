import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

enum GridType {
  gridTypeMi,
  gridTypeTian,
  gridTypeFang,
  gridTypeHui,
  gridTypeVertical,
}

class HanZi {
  String fontName = "楷体";
  double fontSize = 28;
  double fontScan = 1.0;
  double pageWidth = 21;
  double pageHeight = 29.7;
  int colCount = 0;
  int rowCount = 0;

  int maxPageCount = -1;
  double itemWidth = 1.5;
  double itemHeight = 1.5;
  double lineSpace = 0.2;
  double sideSpace = 1.2;
  double linePinyin = 0;
  double startX = 0;
  double startY = 0;
  double cm = 1;

  double docWidth = 0;
  double docHeight = 0;

  bool showPinyin = false;
  GridType gridType = GridType.gridTypeFang;
  Color lineColor = const Color.fromRGBO(199, 238, 206, 1);
  List<Color> textColor = [Colors.grey.shade400, Colors.grey.shade400];

  pw.Document pdf = pw.Document();
  final Map<String, dynamic> fonts;

  HanZi(this.fonts);

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
    rowCount = 0;

    if (gridType == GridType.gridTypeVertical) {
      linePinyin = 0;
      lineSpace = 0;
      showPinyin = false;
    }

    if (showPinyin) {
      if (cfg.containsKey("line_pinyin")) {
        linePinyin = cfg["line_pinyin"].toDouble();
      } else {
        linePinyin = 0.8;
      }
    }
    rowCount = (docHeight + lineSpace) ~/ (itemHeight + linePinyin + lineSpace);

    docWidth = colCount * itemWidth;
    docHeight = rowCount * (itemHeight + linePinyin + lineSpace) - lineSpace;

    startX = (pageWidth - docWidth) / 2;
    startY = (pageHeight - docHeight) / 2;
  }

  void _drawFang(PdfGraphics canvas, double x_, double y_) {
    var y = y_;
    // 绘制每列的竖线
    for (int col = 0; col < colCount; col++) {
      var x = x_ + col * itemWidth;
      canvas.drawLine(x * cm, y * cm, x * cm, (y + itemHeight) * cm);
    }
    canvas.drawRect(x_ * cm, y * cm, docWidth * cm, itemHeight * cm);
    canvas.setLineDashPattern([]);
    canvas.strokePath();
  }

  void _drawTian(PdfGraphics canvas, double x_, double y_) {
    // 绘制每格的中心水平虚线
    double x = x_;
    double y = y_ + itemHeight / 2;
    canvas.drawLine(x * cm, y * cm, (docWidth + x) * cm, y * cm);

    // 绘制每列中间的竖线
    y = y_ + itemHeight;
    for (int index = 0; index < colCount; index++) {
      x = x_ + (index + 0.5) * itemWidth;
      canvas.drawLine(x * cm, (y - itemHeight) * cm, x * cm, y * cm);
    }
    canvas.setLineDashPattern([2, 2]);
    canvas.strokePath();

    _drawFang(canvas, x_, y_);
  }

  void _drawMi(PdfGraphics canvas, double x_, double y_) {
    // 绘制每格的斜线
    double y = y_;
    for (int index = 0; index < colCount; index++) {
      double x = x_ + index * itemWidth;
      canvas.drawLine(
          x * cm, y * cm, (x + itemWidth) * cm, (y + itemHeight) * cm);
      canvas.drawLine(
          (x + itemWidth) * cm, y * cm, x * cm, (y + itemHeight) * cm);
    }
    canvas.setLineDashPattern([2, 2]);
    canvas.strokePath();
    _drawTian(canvas, x_, y_);
  }

  void _drawPinYin(PdfGraphics canvas, double x_, double y_) {
    var x = x_;
    var y = pageHeight - y_;

    y += linePinyin / 3;
    canvas.drawLine(x * cm, y * cm, (docWidth + x) * cm, y * cm);
    y += linePinyin / 3;
    canvas.drawLine(x * cm, y * cm, (docWidth + x) * cm, y * cm);
    y += linePinyin / 3;
    canvas.setLineDashPattern(<int>[3, 3], 0);
    canvas.strokePath();

    canvas.drawLine(x * cm, y * cm, (docWidth + x) * cm, y * cm);
    y += linePinyin / 3;
    canvas.setLineDashPattern([]);
    canvas.strokePath();
  }

  void _drawHui(PdfGraphics canvas, double x_, double y_) {
    // 绘制内框
    var height = itemHeight * 0.7; // 该比例不一定正确。没有找到相关资料。该比例是量出来的。
    var width = height * 0.618;
    var y = y_ + itemHeight - (itemHeight - height) / 2;
    for (var col = 0; col < colCount; col++) {
      var x = x_ + col * itemWidth + (itemWidth - width) / 2;
      canvas.drawRect(x * cm, y * cm, width * cm, -height * cm);
    }
    _drawFang(canvas, x_, y_);
  }

  void drawVertical(PdfGraphics canvas, double x_, double y_) {
    // 绘制每列的竖线
    double y = y_ + itemHeight / 4;
    for (var col = 0; col < colCount + 1; col++) {
      double x = x_ + col * itemWidth;
      canvas.drawLine(x * cm, y * cm, x * cm, (y + itemHeight) * cm);
    }
    canvas.setLineDashPattern([]);
    canvas.strokePath();
  }

  void drawBank(PdfGraphics canvas) {
    for (int row = 0; row < rowCount; row++) {
      var x = startX;
      var y = startY + row * (itemHeight + linePinyin + lineSpace);
      canvas
        ..setStrokeColor(PdfColor(lineColor.red / 255.0,
            lineColor.green / 255.0, lineColor.blue / 255.0, lineColor.opacity))
        ..setLineWidth(0.5)
        ..setFillColor(PdfColors.black);
      if (showPinyin) {
        _drawPinYin(canvas, x, y);
        y += linePinyin;
      }
      switch (gridType) {
        case GridType.gridTypeFang:
          _drawFang(canvas, x, y);
          break;
        case GridType.gridTypeHui:
          _drawHui(canvas, x, y);
          break;
        case GridType.gridTypeTian:
          _drawTian(canvas, x, y);
          break;
        case GridType.gridTypeMi:
          _drawMi(canvas, x, y);
          break;
        case GridType.gridTypeVertical:
          drawVertical(canvas, x, y);
          break;
        default:
      }
    }
  }

  List<int> _pos(int index) {
    int row = 0, col = 0;
    if (gridType == GridType.gridTypeVertical) {
      row = (index % rowCount);
      col = colCount - index ~/ rowCount - 1;
    } else {
      row = index ~/ colCount;
      col = (index % colCount);
    }
    index++;
    return [row, col];
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
          (itemWidth - m!.maxWidth * fontSize / cm) / 2;
      var y = pageHeight - (row + 1) * (itemHeight + linePinyin + lineSpace);

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

  Future<void> drawTextPreLine(String str, {double repeat = 0}) async {
    await clac();
    int count = colCount;
    if (gridType == GridType.gridTypeVertical) {
      count = rowCount;
    }
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

  Future<void> drawMutilateText(String str, {bool bSpaceLine = false}) async {
    await clac();
    if (bSpaceLine) {
      int count = colCount;
      if (gridType == GridType.gridTypeVertical) {
        count = rowCount;
      }

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
        if (gridType == GridType.gridTypeVertical) {
          lineText += spaceLine;
          lineText += str.substring(i, end);
        } else {
          lineText += str.substring(i, end);
          lineText += spaceLine;
        }
      }
      str = lineText;
    }
    doDrawText(str);
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
}
