import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:crypto/crypto.dart' as cy;
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:encrypt/encrypt.dart';
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
  static Future<Response> getStroke(String s) async {
    List<String> characters = [];
    for (var i = 0; i < s.length; i++) {
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
    return response;
  }
}
