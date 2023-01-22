import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:ping_store_check/constants.dart';
import 'package:ping_store_check/src/features/products%20management/application/barcode_scan.dart';
import 'package:ping_store_check/src/features/products%20management/data/products_data.dart';
import 'package:ping_store_check/src/features/products%20management/presentation/components/barcode_form.dart';
import 'package:ping_store_check/src/features/products%20management/presentation/components/record_form.dart';
import 'package:ping_store_check/src/features/socket%20connection/application/socket_connection.dart';
import 'package:ping_store_check/src/generic%20components/my_dialog_log.dart';

Future<void> onAdd(BuildContext context) async {
  List<String> record = List<String>.filled(fields.length, '');
  record[0] = await scanBarcode();
  await showDialog(
    context: context,
    builder: (context) {
      return Dialog(
        child: MyRecordForm(record: record, mode: addMode),
      );
    }
  );
}

Future<void> onEdit(BuildContext context) async {
  String barcode = await scanBarcode();
  await sendTo(
    context: context,
    msg: '${commands['find']} $barcode',
    onData: (data) async {
      String response = utf8.decode(data);
      if(response == logs['not_found']) {
        await myShowDialogLog(
          context: context,
          log: 'Record not found',
        );
      } else {
        await showDialog(
          context: context,
          builder: (context) {
            return Dialog(
              child: MyRecordForm(record: response.split(';'), mode: editMode),
            );
          }
        );
      }
    }
  );
}

Future<void> onSearch(BuildContext context, String mode) async {
  String barcode = await scanBarcode();
  await showDialog(
    context: context,
    builder: (context) {
      return Dialog(
        child: MyBarcodeForm(barcode: barcode, mode: mode),
      );
    }
  );
}

Future<void> onDelete(BuildContext context) async {
  String barcode = await scanBarcode();
  await showDialog(
    context: context,
    builder: (context) {
      return Dialog(
        child: MyBarcodeForm(barcode: barcode, mode: deleteMode),
      );
    }
  );
}

Future<void> onSendRecord(
  BuildContext context,
  bool mode,
  List<TextEditingController> controllers,
) async {
  String record;
  if(mode == addMode) {
    record = List.generate(fields.length, (i) => controllers[i].text).join(';');
    await sendTo(
      context: context,
      msg: '${commands['add']} $record',
      onData: (data) async {
        Navigator.pop(context);
        String response = utf8.decode(data);
        if(response == logs['success']) {
          await myShowDialogLog(
            context: context,
            log: 'Record successfully sent and saved',
          );
        }
      }
    );
  } else if(mode == editMode) {
    record = mergeFields(
      List.generate(fields.length, (i) => controllers[i].text),
    );
    if(!record.endsWith('\n')) record += '\n';
    await sendTo(
      context: context,
      msg: '${commands['edit']} ${controllers[0].text} $record',
      onData: (data) async {
        Navigator.pop(context);
        String response = utf8.decode(data);
        if(response == logs['success']) {
          await myShowDialogLog(
            context: context,
            log: 'Record successfully edited and saved',
          );
        } else if(response == logs['not_found']) {
          await myShowDialogLog(
            context: context,
            log: 'Record not found',
          );
        }
      }
    );
  }
}

Future<void> onSendBarcode(BuildContext context, String mode, String barcode) async {
  if(mode == searchMode) {
    await sendTo(
      context: context,
      msg: '${commands['find']} $barcode',
      onData: (data) async {
        Navigator.pop(context);
        String response = utf8.decode(data);
        if(response == logs['not_found']) {
          await myShowDialogLog(
            context: context,
            log: 'Record not found',
          );
        } else {
          await myShowDialogLog(
            context: context,
            log: response,
          );
        }
      }
    );
  } else if(mode == deleteMode) {
    await sendTo(
      context: context,
      msg: '${commands['remove']} $barcode',
      onData: (data) async {
        Navigator.pop(context);
        String response = utf8.decode(data);
        if(response == logs['not_found']) {
          await myShowDialogLog(
            context: context,
            log: 'Record not found',
          );
        } else if(response == logs['success']) {
          await myShowDialogLog(
            context: context,
            log: 'Record successfully deleted',
          );
        }
      }
    );
  } else if(mode == searchLocallyMode) {
    getApplicationDocumentsDirectory().then((dir) async {
      File f = File('${dir.path}/import.csv');
      if(!f.existsSync()) {
        await myShowDialogLog(context: context, log: 'File does not exist');
        return;
      }
      List<String> records = f.readAsLinesSync();
      for(int i=0; i<records.length; i++) {
        String tmpBarcode = records[i].split(';')[0];
        if(barcode == tmpBarcode) {
          await myShowDialogLog(context: context, log: records[i]);
          return;
        }
      }
      await myShowDialogLog(context: context, log: 'Record not found');
    });
    Navigator.pop(context);
  }
}
