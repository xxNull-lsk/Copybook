import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

class Number {
  Color mLineColor = const Color.fromRGBO(199, 238, 206, 1);
  List<Color> mTextColor = [Colors.grey.shade400, Colors.grey.shade400];
  int mMaxPageCount = -1;

  int mColCount = 0;
  int mRowCount = 0;

  double mItemWidth = 1.5;
  double mItemHeight = 1.5;
  double mLineSpace = 0.8;
  double mSideSpace = 1.2;
  double mStartX = 0;
  double mStartY = 0;
  double cm = 1;

  String mFontName = "楷体";
  double mFontSize = 28;
  double mFontScan = 0;

  double mPageWidth = 21;
  double mPageHeight = 29.7;
  double mDocWidth = 0;
  double mDocHeight = 0;

  pw.Document mPdf = pw.Document();
  final Map<String, dynamic> mFonts;

  Number(this.mFonts);

  Future<void> clac() async {
    mPdf = pw.Document();
    var fontConfig = mFonts[mFontName];
    var fontData = await rootBundle.load("fonts/手写/${fontConfig["font_file"]}");
    final font = PdfTtfFont(mPdf.document, fontData);
    mPdf.document.fonts.add(font);
    cm = PdfPageFormat.cm;
    mSideSpace = 0;

    Map<String, dynamic> cfg = mFonts[mFontName];
    if (cfg.containsKey("font_size")) {
      mFontSize = cfg["font_size"].toDouble();
    }
    if (cfg.containsKey("font_scan")) {
      mFontScan = cfg["font_scan"].toDouble();
    }

    mDocWidth = mPageWidth - mSideSpace * 2;
    mDocHeight = mPageHeight - mSideSpace * 2;

    mColCount = mDocWidth ~/ mItemWidth;
    mRowCount = (mDocHeight + mLineSpace) ~/ (mItemHeight + mLineSpace);

    mDocWidth = mColCount * mItemWidth;
    mDocHeight = mRowCount * (mItemHeight + mLineSpace) - mLineSpace;

    mStartX = (mPageWidth - mDocWidth) / 2;
    mStartY = (mPageHeight - mDocHeight) / 2;
  }

  Future<void> drawMutilateText(String str, {bool bSpaceLine = false}) async {
    await clac();
    if (bSpaceLine) {
      int count = mColCount;
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
    int count = mColCount;
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
        begin < str.length && (pageIndex < mMaxPageCount || mMaxPageCount <= 0)) {
      pageIndex++;
      end = begin + mColCount * mRowCount;
      if (end > str.length) {
        end = str.length;
      }
      String strPage = str.substring(begin, end);
      mPdf.addPage(pw.Page(
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
    row = index ~/ mColCount;
    col = (index % mColCount);
    index++;
    return [row, col];
  }

  void _drawNumber(PdfGraphics canvas, double x_, double y_) {
    // 绘制每列的竖线
    for (int col = 0; col < mColCount; col++) {
      var y = mPageHeight - y_ - mItemHeight;
      var x = x_ + col * mItemWidth;
      canvas.drawRect(x * cm, y * cm, mItemWidth / 2 * cm, mItemHeight * cm);
      canvas.setLineDashPattern([]);
      canvas.strokePath();
      y += mItemHeight / 2;
      canvas.drawLine(x * cm, y * cm, (x + mItemWidth / 2) * cm, y * cm);
      canvas.setLineDashPattern([2, 2], 0);
      canvas.strokePath();
    }
    canvas.strokePath();
  }

  void drawBank(PdfGraphics canvas) {
    canvas
      ..setStrokeColor(PdfColor(mLineColor.red / 255.0, mLineColor.green / 255.0,
          mLineColor.blue / 255.0, mLineColor.opacity))
      ..setLineWidth(0.5)
      ..setFillColor(PdfColors.black);
    for (int row = 0; row < mRowCount; row++) {
      var x = mStartX;
      var y = mStartY + row * (mItemHeight + mLineSpace);
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
      var x = mStartX +
          col * mItemWidth +
          (mItemWidth / 2 - m!.advanceWidth * mFontSize / cm) / 2;
      var y = mPageHeight -
          row * (mItemHeight + mLineSpace) -
          mItemHeight;

      // 设置文字颜色
      Color color;
      if (col < mTextColor.length) {
        color = mTextColor[col];
      } else {
        color = mTextColor[mTextColor.length - 1];
      }
      canvas.setFillColor(
          PdfColor(color.red / 255.0, color.green / 255.0, color.blue / 255.0));

      canvas.drawString(
          canvas.defaultFont!, mFontSize, str[index], x * cm, y * cm);
    }
  }
}
