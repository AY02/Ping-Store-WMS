import 'package:barcode_scan/barcode_scan.dart';
import 'package:flutter/services.dart';
import 'package:icheck/constants.dart';

Future<String> scan() async {
  String barcode = '';
  try {
    ScanResult scanResult = await BarcodeScanner.scan();
    barcode = scanResult.rawContent;
  } on PlatformException catch (e) {
    (e.code == BarcodeScanner.cameraAccessDenied) ?
      log('Camera Access Denied', type: 'Error Check')
      : log('Unknown Error: $e', type: 'Error Check');
  }
  return barcode;
}