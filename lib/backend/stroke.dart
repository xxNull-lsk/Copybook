import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'dart:ui';
import 'package:bitmap/bitmap.dart';
import 'package:crypto/crypto.dart' as cy;
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:encrypt/encrypt.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pointycastle/asymmetric/api.dart';

Future<String> getEncryptData(
    String path, String timestamp, String nonce, String data) async {
  var content = "POST\n$path\n$timestamp\n$nonce\n$data\n";
  var sum = cy.sha256.convert(utf8.encode(content));
  final pubKey =
      await rootBundle.loadString("res/resource_center_rsa_public.pem");
  final parser = RSAKeyParser();
  final publicKey = parser.parse(pubKey) as RSAPublicKey;
  final encrypter = Encrypter(RSA(publicKey: publicKey));
  return encrypter.encryptBytes(sum.bytes).base64;
}

class Backend {
  static Map<String, dynamic> mStrokes = {};
  static List<dynamic>? getCharStroke(String c) {
    Map<String, dynamic>? dataStroke = mStrokes[c];
    if (dataStroke == null || !dataStroke.keys.contains("stroke")) {
      return null;
    }
    return jsonDecode(dataStroke["stroke"]);
  }

  static String ignore = "，。？！——《》【】；‘’“”";
  static bool containStroke(String s) {
    for (var i = 0; i < s.length; i++) {
      var c = s[i];
      if (ignore.contains(c)) {
        continue;
      }
      if (!mStrokes.keys.contains(c)) {
        return false;
      }
    }
    return true;
  }

  static Future<bool> getStrokeFromServer(String s) async {
    List<String> characters = [];
    for (var i = 0; i < s.length; i++) {
      var c = s[i];
      if (ignore.contains(c)) {
        continue;
      }
      if (mStrokes.keys.contains(c)) {
        continue;
      }
      characters.add(s[i]);
    }
    Map<String, dynamic> body = {"character": characters};

    final dio = Dio();
    (dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      HttpClient client = HttpClient();
      client.badCertificateCallback =
          (X509Certificate cert, String host, int port) => true;
      return client;
    };

    String data = json.encode(body);

    var nonce = Random.secure().nextInt(10000).toString();
    var timestamp =
        (DateTime.now().millisecondsSinceEpoch / 1000).round().toString();

    var path = "/res/stroke";
    var enc = await getEncryptData(path, timestamp, nonce, data);
    var begin = DateTime.now();
    final response = await dio.post('https://blog.mydata.top:8681$path',
        data: data,
        options: Options(
          sendTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 10),
          headers: {
            "Content-Type": "application/json",
            'Content-Length': data.length.toString(),
            "Authorization_type": "AUTH-SHA256-RSA-ENC",
            "Authorization_nonce": nonce,
            "Authorization_timestamp": timestamp,
            "Authorization_enc": enc
          },
        ));
    //print(response.data.toString());
    var used = DateTime.now().difference(begin);
    print("get stroke used: ${used.toString()}");

    if (response.statusCode != 200 || response.data["code"] != 0) {
      return false;
    }
    Map<String, dynamic> strokes = response.data["data"];
    mStrokes.addAll(strokes);
    return true;
  }

  static int charStrokeLength(String c) {
    var dataStroke = mStrokes[c];
    if (dataStroke == null) {
      return 0;
    }

    List<dynamic> stroke = jsonDecode(dataStroke["stroke"]);
    return stroke.length;
  }

  static Future<Bitmap?> charStrokeToImage(
      String c, int step, int width, int height) async {
    var dataStroke = mStrokes[c];
    if (dataStroke == null) {
      return null;
    }

    List<dynamic> stroke = jsonDecode(dataStroke["stroke"]);
    return strokeToImage(stroke, step, width, height);
  }

  static Future<Bitmap?> strokeToImage(
      List<dynamic> stroke, int step, int width, int height) async {
    var h = 900;
    final recorder = PictureRecorder();
    Canvas canvas = Canvas(recorder);
    var paint = Paint();

    paint.color = Colors.black; //mTextColor[1];
    paint.style = PaintingStyle.fill;
    for (var strokeItem in stroke) {
      var path = Path();
      var items = strokeItem.split(" ");
      for (var i = 0; i < items.length; i++) {
        switch (items[i]) {
          case "M":
            path.moveTo(
                double.parse(items[i + 1]), h - double.parse(items[i + 2]));
            i += 2;
            break;
          case "L":
            path.lineTo(
                double.parse(items[i + 1]), h - double.parse(items[i + 2]));
            i += 2;
            break;
          case "Q":
            path.quadraticBezierTo(
                double.parse(items[i + 1]),
                h - double.parse(items[i + 2]),
                double.parse(items[i + 3]),
                h - double.parse(items[i + 4]));
            i += 4;
            break;
          case "Z":
            canvas.drawPath(path, paint);
            break;
          default:
        }
      }
      step--;
      if (step <= 0) {
        break;
      }
    }

    var picture = recorder.endRecording();

    var image = picture.toImageSync(1000, 1000);
    var imageData = await image.toByteData();
    if (imageData == null) {
      return null;
    }

    var bmp = Bitmap.fromHeadless(
        image.width, image.height, imageData.buffer.asUint8List());
    return bmp.apply(BitmapResize.to(width: width, height: height));
  }
}
