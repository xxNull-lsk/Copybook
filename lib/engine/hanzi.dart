import 'package:copybook/backend/stroke.dart';
import 'package:copybook/global.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:image/image.dart' as im;

enum GridType {
  gridTypeMi,
  gridTypeTian,
  gridTypeFang,
  gridTypeHui,
  gridTypeVertical,
}

class HanZiEvent {
  int pageIndex;
  int indexInPage;
  HanZiEvent(this.pageIndex, this.indexInPage);
}

class HanZi {
  String mFontName = "楷体";
  double mFontSize = 28;
  double mFontScan = 1.0;
  double mPageWidth = 21;
  double mPageHeight = 29.7;
  int mColCount = 0;
  int mRowCount = 0;

  int mMaxPageCount = -1;
  double mItemWidth = 1.5;
  double mItemHeight = 1.5;
  double mLineSpace = 0.2;
  double mSideSpace = 0;
  double mLinePinyin = 0;
  double mStartX = 0;
  double mStartY = 0;
  double cm = PdfPageFormat.cm;

  double mDocWidth = 0;
  double mDocHeight = 0;

  bool mShowPinyin = false;
  GridType mGridType = GridType.gridTypeFang;
  Color mLineColor = const Color.fromRGBO(199, 238, 206, 1);
  List<Color> mTextColor = [Colors.grey.shade400, Colors.grey.shade400];

  pw.Document mPdf = pw.Document();
  final Map<String, dynamic> fonts;

  HanZi(this.fonts);

  Future<void> clac() async {
    //mPageWidth = PdfPageFormat.a4.width;
    //mPageHeight = PdfPageFormat.a4.height;
    Map<String, dynamic> cfg = {};
    mPdf = pw.Document();
    var fontConfig = fonts[mFontName];
    if (fontConfig != null) {
      var fontData =
          await rootBundle.load("fonts/手写/${fontConfig["font_file"]}");
      final font = PdfTtfFont(mPdf.document, fontData);
      mPdf.document.fonts.add(font);

      cfg = fonts[mFontName];
      if (cfg.containsKey("font_size")) {
        mFontSize = cfg["font_size"].toDouble();
      }
      if (cfg.containsKey("font_scan")) {
        mFontScan = cfg["font_scan"].toDouble();
      }
    }
    mSideSpace = 0;

    mDocWidth = mPageWidth - mSideSpace * 2;
    mDocHeight = mPageHeight - mSideSpace * 2;

    mColCount = mDocWidth ~/ mItemWidth;
    mRowCount = 0;

    if (mGridType == GridType.gridTypeVertical) {
      mLinePinyin = 0;
      mLineSpace = 0;
      mShowPinyin = false;
    }

    if (mShowPinyin) {
      if (cfg.containsKey("line_pinyin")) {
        mLinePinyin = cfg["line_pinyin"].toDouble();
      } else {
        mLinePinyin = 0.8;
      }
    }
    mRowCount =
        (mDocHeight + mLineSpace) ~/ (mItemHeight + mLinePinyin + mLineSpace);

    mDocWidth = mColCount * mItemWidth;
    mDocHeight =
        mRowCount * (mItemHeight + mLinePinyin + mLineSpace) - mLineSpace;

    mStartX = (mPageWidth - mDocWidth) / 2;
    mStartY = (mPageHeight - mDocHeight) / 2;
  }

  void _drawFang(PdfGraphics canvas, double x_, double y_) {
    var y = y_;
    // 绘制每列的竖线
    for (int col = 0; col < mColCount; col++) {
      var x = x_ + col * mItemWidth;
      canvas.drawLine(x * cm, y * cm, x * cm, (y + mItemHeight) * cm);
    }
    canvas.drawRect(x_ * cm, y * cm, mDocWidth * cm, mItemHeight * cm);
    canvas.setLineDashPattern([]);
    canvas.strokePath();
  }

  void _drawTian(PdfGraphics canvas, double x_, double y_) {
    // 绘制每格的中心水平虚线
    double x = x_;
    double y = y_ + mItemHeight / 2;
    canvas.drawLine(x * cm, y * cm, (mDocWidth + x) * cm, y * cm);

    // 绘制每列中间的竖线
    y = y_ + mItemHeight;
    for (int index = 0; index < mColCount; index++) {
      x = x_ + (index + 0.5) * mItemWidth;
      canvas.drawLine(x * cm, (y - mItemHeight) * cm, x * cm, y * cm);
    }
    canvas.setLineDashPattern([2, 2]);
    canvas.strokePath();

    _drawFang(canvas, x_, y_);
  }

  void _drawMi(PdfGraphics canvas, double x_, double y_) {
    // 绘制每格的斜线
    double y = y_;
    for (int index = 0; index < mColCount; index++) {
      double x = x_ + index * mItemWidth;
      canvas.drawLine(
          x * cm, y * cm, (x + mItemWidth) * cm, (y + mItemHeight) * cm);
      canvas.drawLine(
          (x + mItemWidth) * cm, y * cm, x * cm, (y + mItemHeight) * cm);
    }
    canvas.setLineDashPattern([2, 2]);
    canvas.strokePath();
    _drawTian(canvas, x_, y_);
  }

  void _drawPinYin(PdfGraphics canvas, double x_, double y_) {
    var x = x_;
    var y = mPageHeight - y_;

    y += mLinePinyin / 3;
    canvas.drawLine(x * cm, y * cm, (mDocWidth + x) * cm, y * cm);
    y += mLinePinyin / 3;
    canvas.drawLine(x * cm, y * cm, (mDocWidth + x) * cm, y * cm);
    y += mLinePinyin / 3;
    canvas.setLineDashPattern(<int>[3, 3], 0);
    canvas.strokePath();

    canvas.drawLine(x * cm, y * cm, (mDocWidth + x) * cm, y * cm);
    y += mLinePinyin / 3;
    canvas.setLineDashPattern([]);
    canvas.strokePath();
  }

  void _drawHui(PdfGraphics canvas, double x_, double y_) {
    // 绘制内框
    var height = mItemHeight * 0.7; // 该比例不一定正确。没有找到相关资料。该比例是量出来的。
    var width = height * 0.618;
    var y = y_ + mItemHeight - (mItemHeight - height) / 2;
    for (var col = 0; col < mColCount; col++) {
      var x = x_ + col * mItemWidth + (mItemWidth - width) / 2;
      canvas.drawRect(x * cm, y * cm, width * cm, -height * cm);
    }
    _drawFang(canvas, x_, y_);
  }

  void drawVertical(PdfGraphics canvas, double x_, double y_) {
    // 绘制每列的竖线
    double y = y_ + mItemHeight / 4;
    for (var col = 0; col < mColCount + 1; col++) {
      double x = x_ + col * mItemWidth;
      canvas.drawLine(x * cm, y * cm, x * cm, (y + mItemHeight) * cm);
    }
    canvas.setLineDashPattern([]);
    canvas.strokePath();
  }

  void drawBank(PdfGraphics canvas) {
    for (int row = 0; row < mRowCount; row++) {
      var x = mStartX;
      var y = mStartY + row * (mItemHeight + mLinePinyin + mLineSpace);
      canvas
        ..setStrokeColor(PdfColor(
            mLineColor.red / 255.0,
            mLineColor.green / 255.0,
            mLineColor.blue / 255.0,
            mLineColor.opacity))
        ..setLineWidth(0.5)
        ..setFillColor(PdfColors.black);
      if (mShowPinyin) {
        _drawPinYin(canvas, x, y);
        y += mLinePinyin;
      }
      switch (mGridType) {
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

  int mCurrIndex = 0;
  List<int> _pos(int indexInPage) {
    int row = 0, col = 0;
    if (mGridType == GridType.gridTypeVertical) {
      row = (indexInPage % mRowCount);
      col = mColCount - indexInPage ~/ mRowCount - 1;
    } else {
      row = indexInPage ~/ mColCount;
      col = (indexInPage % mColCount);
    }
    return [row, col];
  }

  List<int> _next() {
    var pos = _pos(mCurrIndex);
    mCurrIndex++;
    return pos;
  }

  List<int> mDrawingStroke = [];
  Future<bool> onDrawStroke(List<dynamic>? stroke, PdfGraphics pdfCanvas,
      PdfPoint size, int pageIndex, int indexInPage) async {
    if (stroke == null) {
      return false;
    }
    for (int indexInStroke = 0;
        indexInStroke < stroke.length;
        indexInStroke++) {
      var bmp = await Backend.strokeToImage(stroke, indexInStroke + 1,
          (mFontSize * 3).round(), (mFontSize * 3).round());
      if (bmp == null) {
        continue;
      }
      var img = im.Image.fromBytes(
          width: bmp.width,
          height: bmp.height,
          bytes: bmp.content.buffer,
          order: im.ChannelOrder.rgba);

      var pdfImage = PdfImage.fromImage(mPdf.document, image: img);

      var pos = _pos(indexInPage + indexInStroke);
      var row = pos[0];
      var col = pos[1] - 1;
      var x = mStartX + (col + 0) * mItemWidth - 0.3;
      var y =
          mStartY + (row + 0) * (mItemHeight + mLinePinyin + mLineSpace) - 0.7;
      pdfCanvas.drawImage(
          pdfImage,
          x * cm + PdfPageFormat.standard.marginLeft,
          (mPageHeight - y) * cm - PdfPageFormat.standard.marginTop,
          mFontSize * 0.8,
          mFontSize * 0.8);
    }
    Global.eventBus.fire(HanZiEvent(pageIndex, indexInPage));
    mDrawingStroke.remove(pageIndex * mColCount * mRowCount + indexInPage);
    return true;
  }

  Future<void> onDrawMutilateText(int pageIndex, String str, PdfGraphics canvas,
      PdfPoint size, bool bStroke) async {
    drawBank(canvas);
    for (int index = 0; index < str.length; index++) {
      var pos = _next();
      var row = pos[0];
      var col = pos[1];
      final String c = str[index];
      var m = canvas.defaultFont?.stringMetrics(c);
      var x = mStartX +
          col * mItemWidth +
          (mItemWidth - m!.maxWidth * mFontSize / cm) / 2;
      var y =
          mPageHeight - (row + 1) * (mItemHeight + mLinePinyin + mLineSpace);

      // 设置文字颜色
      Color color;
      if (col < mTextColor.length) {
        color = mTextColor[col];
      } else {
        color = mTextColor[mTextColor.length - 1];
      }
      canvas.setFillColor(
          PdfColor(color.red / 255.0, color.green / 255.0, color.blue / 255.0));

      canvas.drawString(canvas.defaultFont!, mFontSize, c, x * cm, y * cm);
      canvas.saveContext();
      if (bStroke) {
        var strokes = Backend.getCharStroke(c);
        if (strokes != null) {
          mDrawingStroke.add(pageIndex * mColCount * mRowCount + mCurrIndex);
          onDrawStroke(strokes, canvas, size, pageIndex, mCurrIndex);
          mCurrIndex += strokes.length;
        }
        // 补齐笔画的空格，以达到行对齐的目的
        mCurrIndex = (mCurrIndex.toDouble() / mColCount).ceil() * mColCount;
      }
    }
  }

  Future<void> drawTextPreLine(String str, {var repeat = 0}) async {
    int count = mColCount;
    count = mColCount;
    if (mGridType == GridType.gridTypeVertical) {
      count = mRowCount;
    }
    int repeatCount = 0;
    if (repeat.runtimeType == double) {
      repeatCount = (count * repeat as double).round();
    } else if (repeat.runtimeType == int) {
      repeatCount = repeat as int;
    }
    // 填充，每行数据
    String lineText = "";
    for (var i = 0; i < str.length; i++) {
      lineText += str[i];
      for (var c = 0; c < count - 1; c++) {
        if (c + 1 >= repeatCount) {
          lineText += ' ';
        } else {
          lineText += str[i];
        }
      }
    }
    await doDrawText(lineText);
  }

  Future<void> drawMutilateText(
    String str, {
    bool bSpaceLine = false,
    bool bStroke = false,
  }) async {
    if (bStroke) {
    } else if (bSpaceLine) {
      int count = mColCount;
      if (mGridType == GridType.gridTypeVertical) {
        count = mRowCount;
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
        if (mGridType == GridType.gridTypeVertical) {
          lineText += spaceLine;
          lineText += str.substring(i, end);
        } else {
          lineText += str.substring(i, end);
          lineText += spaceLine;
        }
      }
      str = lineText;
    }
    await doDrawText(str, bStroke: bStroke);
  }

  Future<void> doDrawText(String str, {bool bStroke = false}) async {
    int begin = 0, end = 0;
    int pageIndex = 0;

    while (begin < str.length &&
        (pageIndex < mMaxPageCount || mMaxPageCount <= 0)) {
      pageIndex++;
      end = begin + mColCount * mRowCount;

      if (end > str.length) {
        end = str.length;
      }
      if (bStroke) {
        int indexInPage = 0;
        end = begin;
        while (end < str.length) {
          String c = str.substring(end, end + 1);
          indexInPage++;
          var strokes = Backend.getCharStroke(c);
          if (strokes != null) {
            indexInPage += strokes.length;
          }
          indexInPage = (indexInPage / mColCount).ceil() * mColCount;
          if (indexInPage > mColCount * mRowCount) {
            break;
          }
          end++;
        }
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
                    painter: (canvas, size) {
                      mCurrIndex = 0;
                      onDrawMutilateText(
                          pageIndex - 1, strPage, canvas, size, bStroke);
                    }),
              ));
        },
      ));
      begin = end;
    }
  }
}
