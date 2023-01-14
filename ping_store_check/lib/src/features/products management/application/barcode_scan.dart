import 'package:flutter_barcode_scanner/flutter_barcode_scanner.dart';

Future<String> scanBarcode() async {
  String result = await FlutterBarcodeScanner.scanBarcode(
    '#ff6666',
    'Cancel',
    true,
    ScanMode.BARCODE,
  );
  if(result == '-1') {
    result = '';
  }
  return result;
}
