import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

class PinYin {
  Color mLineColor = const Color.fromRGBO(199, 238, 206, 1);
  List<Color> mTextColor = [Colors.grey.shade400, Colors.grey.shade400];
  bool mShowHanzi = false;
  int mMaxPageCount = -1;

  int mColCount = 0;
  int mRowCount = 0;

  double mItemWidth = 1.5;
  double mItemHeight = 1.5;
  double mLineSpace = 0.8;
  double mSideSpace = 1.2;
  double mLineHanzi = 0;
  double mStartX = 0;
  double mStartY = 0;
  double cm = 1;

  double mFontSize = 28;
  double mFontScan = 0.86;

  double mPageWidth = 21;
  double mPageHeight = 29.7;
  double mDocWidth = 0;
  double mDocHeight = 0;

  pw.Document mPdf = pw.Document();

  Future<void> clac() async {
    mPdf = pw.Document();
    var fontData = await rootBundle.load("fonts/拼音/汉语拼音.ttf");
    final font = PdfTtfFont(mPdf.document, fontData);
    mPdf.document.fonts.add(font);
    cm = PdfPageFormat.cm;
    mSideSpace = 0;

    mDocWidth = mPageWidth - mSideSpace * 2;
    mDocHeight = mPageHeight - mSideSpace * 2;

    if (mShowHanzi) {
      mLineHanzi = 2.0;
      mItemWidth = 2.0;
      mFontSize = 18;
      mItemHeight = 0.9;
      mFontScan = 1;
      mLineSpace = 0.2;
    } else {
      mLineHanzi = 0;
      mFontSize = 28;
      mItemHeight = 1.5;
      mItemWidth = 2.5;
      mFontScan = 0.12;
      mLineSpace = 0.8;
    }
    mColCount = mDocWidth ~/ mItemWidth;
    mRowCount = (mDocHeight + mLineSpace) ~/ (mItemHeight + mLineHanzi + mLineSpace);

    mDocWidth = mColCount * mItemWidth;
    mDocHeight = mRowCount * (mItemHeight + mLineHanzi + mLineSpace) - mLineSpace;

    mStartX = (mPageWidth - mDocWidth) / 2;
    mStartY = (mPageHeight - mDocHeight) / 2;
  }

  Future<void> drawMutilateText(List<String> str,
      {bool bSpaceLine = false}) async {
    await clac();
    if (bSpaceLine) {
      int count = mColCount;

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
    int count = mColCount;
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
        begin < str.length && (pageIndex < mMaxPageCount || mMaxPageCount <= 0)) {
      pageIndex++;
      end = begin + mColCount * mRowCount;
      if (end > str.length) {
        end = str.length;
      }
      List<String> strPage = str.sublist(begin, end);
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

  void _drawFang(PdfGraphics canvas, double x_, double y_) {
    var y = mPageHeight - y_ - mLineHanzi;
    // 绘制每列的竖线
    for (int col = 0; col < mColCount; col++) {
      var x = x_ + col * mLineHanzi;
      canvas.drawLine(x * cm, y * cm, x * cm, (y + mLineHanzi) * cm);
    }
    canvas.drawRect(x_ * cm, y * cm, mDocWidth * cm, mLineHanzi * cm);
    canvas.setLineDashPattern([]);
    canvas.strokePath();
  }

  void _drawPinYin(PdfGraphics canvas, double x_, double y_) {
    var x = x_;
    var y = mPageHeight - y_ - mItemHeight;

    canvas.drawLine(x * cm, y * cm, (mDocWidth + x) * cm, y * cm);
    canvas.setLineDashPattern([]);
    canvas.strokePath();

    y += mItemHeight / 3;
    canvas.drawLine(x * cm, y * cm, (mDocWidth + x) * cm, y * cm);
    y += mItemHeight / 3;

    canvas.drawLine(x * cm, y * cm, (mDocWidth + x) * cm, y * cm);
    canvas.setLineDashPattern([3, 3], 0);
    canvas.strokePath();

    y += mItemHeight / 3;
    canvas.drawLine(x * cm, y * cm, (mDocWidth + x) * cm, y * cm);

    y = mPageHeight - y_ - mItemHeight;
    for (int col = 0; col < mColCount + 1; col++) {
      double x = x_ + mItemWidth * col;
      canvas.drawLine(x * cm, y * cm, x * cm, (y + mItemHeight) * cm);
    }
    canvas.setLineDashPattern([]);
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
      var y = mStartY + row * (mItemHeight + mLineHanzi + mLineSpace);
      _drawPinYin(canvas, x, y);
      y += mItemHeight;
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
          mStartX + col * mItemWidth + (mItemWidth - m!.width * mFontSize / cm) / 2;
      var y = mPageHeight -
          row * (mItemHeight + mLineHanzi + mLineSpace) -
          mItemHeight * mFontScan -
          m.maxHeight * mFontSize / cm;

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
