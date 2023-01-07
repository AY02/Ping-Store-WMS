import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_barcode_scanner/flutter_barcode_scanner.dart';
import 'package:ping_store_check/src/features/products_management/presentation/components/edit_form.dart';
import 'package:ping_store_check/src/features/products_management/presentation/components/send_form.dart';
import 'package:ping_store_check/src/features/socket_connection/domain/socket_provider.dart';
import 'package:ping_store_check/utils.dart';
import 'package:provider/provider.dart';


class MyProductManagement extends StatelessWidget {
  const MyProductManagement({super.key});

  Future<String> scanBarcodeNormal() async {
    try {
      String barcodeScanRes = await FlutterBarcodeScanner.scanBarcode(
        '#ff6666',
        'Cancel',
        true,
        ScanMode.BARCODE,
      );
      if(barcodeScanRes == '-1') {
        return '';
      }
      return barcodeScanRes;
    } on Error {
      return 'Error';
    }
  }

  Future<void> pressedFunction(BuildContext context, String util) async {
    var socketProvider =  context.read<SocketProvider>();
    if(!socketProvider.connected) return;
    String barcode = await scanBarcodeNormal();
    if(barcode.isEmpty) return;
    if(util == 'ADD') {
      socketProvider.subscription.onData((data) async => await showDialog(
        context: context,
        builder: (context) => Dialog(
          child: Text(utf8.decode(data)),
        ),
      ));
      await showDialog(context: context,
        builder: (context) => Dialog(child: MySendForm(barcode: barcode)),
      );
    } else if(util == 'EDIT') {
      socketProvider.subscription.onData((data) async {
        if(utf8.decode(data) == 'Record not found') {
          await showDialog(
            context: context,
            builder: (context) => Dialog(
              child: Text(utf8.decode(data)),
            ),
          );
        } else {
          List<String> foundRecord = utf8.decode(data).split(';');
          await showDialog(context: context,
            builder: (context) => Dialog(child: MyEditForm(foundRecord: foundRecord))
          );
        }
      });
      socketProvider.client.write('!find $barcode');
    } else if(util == 'SEARCH') {
      socketProvider.subscription.onData((data) async => await showDialog(
        context: context,
        builder: (context) => Dialog(child: Text(utf8.decode(data))),
      ));
      socketProvider.client.write('!find $barcode');
    } else if(util == 'DELETE') {
      socketProvider.subscription.onData((data) async => await showDialog(
        context: context,
        builder: (context) => Dialog(child: Text(utf8.decode(data))),
      ));
      socketProvider.client.write('!delete $barcode');
    }
  }

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      padding: EdgeInsets.symmetric(
        vertical: heigthPercentage(context, 6),
        horizontal: widthPercentage(context, 12),
      ),
      crossAxisCount: 2,
      mainAxisSpacing: heigthPercentage(context, 3),
      crossAxisSpacing: widthPercentage(context, 6),
      children: [
        ElevatedButton.icon(
          onPressed: () async => await pressedFunction(context, 'ADD'),
          icon: const Icon(Icons.add),
          label: const Text('ADD'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await pressedFunction(context, 'EDIT'),
          icon: const Icon(Icons.edit),
          label: const Text('EDIT'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await pressedFunction(context, 'SEARCH'),
          icon: const Icon(Icons.search),
          label: const Text('SEARCH'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await pressedFunction(context, 'DELETE'),
          icon: const Icon(Icons.delete),
          label: const Text('DELETE'),
        ),
      ],
    );
  }
}