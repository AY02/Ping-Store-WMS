import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_barcode_scanner/flutter_barcode_scanner.dart';
import 'package:ping_store_check/src/features/products_management/presentation/components/edit_form.dart';
import 'package:ping_store_check/src/features/products_management/presentation/components/send_form.dart';
import 'package:ping_store_check/src/features/socket_connection/application/socket_connection.dart';
import 'package:ping_store_check/src/features/socket_connection/data/socket_data.dart';
import 'package:ping_store_check/src/features/socket_connection/domain/socket_provider.dart';
import 'package:ping_store_check/utils.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';


class MyProductManagement extends StatelessWidget {
  const MyProductManagement({super.key});

  Future<String> _scanBarcode() async {
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

  Future<void> _onPressed(BuildContext context, String command) async {
    var socketProvider =  context.read<SocketProvider>();
    if(!socketProvider.connected) {
      final prefs = await SharedPreferences.getInstance();
      String ip = prefs.getString('ip') ?? '';
      String port = prefs.getString('port') ?? '';
      if(port.isNotEmpty && ip.isNotEmpty) {
        // ignore: use_build_context_synchronously
        await connectToServer(context, ip, int.parse(port));
      }
      return;
    }
    String barcode = await _scanBarcode();
    if(barcode.isEmpty) return;
    if(command == 'ADD') {
      subscription.onData((data) async => await showDialog(
        context: context,
        builder: (context) => Dialog(
          child: Text(utf8.decode(data)),
        ),
      ));
      await showDialog(context: context,
        builder: (context) => Dialog(child: MySendForm(barcode: barcode)),
      );
    } else if(command == 'EDIT') {
      subscription.onData((data) async {
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
      client.write('!find $barcode');
    } else if(command == 'SEARCH') {
      subscription.onData((data) async => await showDialog(
        context: context,
        builder: (context) => Dialog(child: Text(utf8.decode(data))),
      ));
      client.write('!find $barcode');
    } else if(command == 'DELETE') {
      subscription.onData((data) async => await showDialog(
        context: context,
        builder: (context) => Dialog(child: Text(utf8.decode(data))),
      ));
      client.write('!delete $barcode');
    }
  }

  @override
  Widget build(BuildContext context) {
    subscription.onDone(() async => await disconnectFromServer(context));
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
          onPressed: () async => await _onPressed(context, 'ADD'),
          icon: const Icon(Icons.add),
          label: const Text('ADD'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await _onPressed(context, 'EDIT'),
          icon: const Icon(Icons.edit),
          label: const Text('EDIT'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await _onPressed(context, 'SEARCH'),
          icon: const Icon(Icons.search),
          label: const Text('SEARCH'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await _onPressed(context, 'DELETE'),
          icon: const Icon(Icons.delete),
          label: const Text('DELETE'),
        ),
      ],
    );
  }
}