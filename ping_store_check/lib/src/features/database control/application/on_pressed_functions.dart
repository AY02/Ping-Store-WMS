import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:ping_store_check/constants.dart';
import 'package:ping_store_check/src/features/socket%20connection/application/socket_connection.dart';
import 'package:ping_store_check/src/generic%20components/my_dialog_log.dart';

Future<void> onShowDuplicatePressed(BuildContext context) async {
  await sendTo(
    context: context,
    msg: '${commands['show_duplicate']}',
    onData: (data) async {
      dynamic records;
      try{
        records = json.decode(utf8.decode(data));
        await showDialog(
          context: context, 
          builder: (context) {
            return Dialog(
              child: ListView.builder(
                itemCount: records.length,
                itemBuilder: (BuildContext context, int index) => Text(records[index]),
              )
            );
          },
        );
      } catch(e) {
        await myShowDialogLog(context: context, log: 'No duplicates found');
      }
    },
  );
}

Future<void> onDeleteDuplicatePressed(BuildContext context) async {
  await sendTo(
    context: context,
    msg: '${commands['delete_duplicate']}',
    onData: (data) async {
      String response = utf8.decode(data);
      if(response == logs['not_found']) {
        await myShowDialogLog(
          context: context,
          log: 'No duplicates found',
        );
      } else if(response == logs['success']) {
        await myShowDialogLog(
          context: context,
          log: 'Duplicates successfully deleted',
        );
      }
    },
  );
}

Future<void> onBackupDatabasePressed(BuildContext context) async {
  await sendTo(
    context: context,
    msg: '${commands['backup']}',
    onData: (data) async {
      String response = utf8.decode(data);
      if(response == logs['success']) {
        await myShowDialogLog(
          context: context,
          log: 'Backup done successfully',
        );
      }
    },
  );
}

Future<void> onUpdateDatabasePressed(BuildContext context) async {
  await sendTo(
    context: context,
    msg: '${commands['update_database']}',
    onData: (data) async {
      String response = utf8.decode(data);
      if(response == logs['success']) {
        await myShowDialogLog(
          context: context,
          log: 'Database update completed successfully',
        );
      }
    },
  );
}
