import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:platform_device_id_v3/platform_device_id.dart';
import 'package:package_info_plus/package_info_plus.dart';

class Utils {
  static void doTick() async {
    PackageInfo packageInfo = await PackageInfo.fromPlatform();
    String? deviceId = await PlatformDeviceId.getDeviceId;
    final dio = Dio();
    (dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      HttpClient client = HttpClient();
      client.badCertificateCallback =
          (X509Certificate cert, String host, int port) => true;
      return client;
    };
    var deviceInfo = await DeviceInfoPlugin().deviceInfo;
    if (deviceId == null || deviceId.isEmpty) {
      if (Platform.isAndroid) {
        var deviceInfo = await DeviceInfoPlugin().androidInfo;
        deviceId = deviceInfo.id;
      } else if (Platform.isLinux) {
        var deviceInfo = await DeviceInfoPlugin().linuxInfo;
        deviceId = deviceInfo.machineId;
      } else if (Platform.isWindows) {
        var deviceInfo = await DeviceInfoPlugin().windowsInfo;
        deviceId = deviceInfo.deviceId;
      } else if (Platform.isIOS) {
        var deviceInfo = await DeviceInfoPlugin().iosInfo;
        deviceId = deviceInfo.identifierForVendor;
      } else if (Platform.isMacOS) {
        var deviceInfo = await DeviceInfoPlugin().macOsInfo;
        deviceId = deviceInfo.systemGUID;
      }
    }
    Map<String, dynamic> body = {
      "app": {
        "name": packageInfo.appName,
        "version": "${packageInfo.version}(${packageInfo.buildNumber})",
        "md5sum": "",
        "statistics": {},
      },
      "host": {
        "mac": deviceId ?? "no_id",
        "os": Platform.operatingSystem,
        "ext": {
          "os_version": Platform.operatingSystemVersion,
          "localeName": Platform.localeName,
          "localHostname": Platform.localHostname,
          "deviceInfo": deviceInfo.data,
        },
      }
    };
    String data = json.encode(
      body,
      toEncodable: (object) {
        if (object is DateTime) {
          return object.toString();
        }
        return object;
      },
    );
    final response =
        await dio.post('https://blog.mydata.top:8681/api/common/tick_20230701',
            data: data,
            options: Options(
              sendTimeout: const Duration(seconds: 10),
              receiveTimeout: const Duration(seconds: 10),
              headers: {
                "Content-Type": "application/json",
                'Content-Length': data.length.toString()
              },
            ));
    if (response.data["code"] != 0) {
      exit(0);
    }
  }
}
