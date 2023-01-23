import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:ping_store_check/constants.dart';
import 'package:ping_store_check/src/features/socket%20connection/application/socket_connection.dart';
import 'package:ping_store_check/src/generic%20components/my_dialog_log.dart';

Future<void> onShowDuplicatePressed(BuildContext context) async {
  List<String> records = [];
  await sendTo(
    context: context,
    msg: commands['show_duplicate']!,
    recordsMode: true,
    onData: (data) async {
      try {
        List<dynamic> chunk = json.decode(utf8.decode(data));
        for(String record in chunk) {
          records.add(record);
        }
      } catch(e) {
        String message = utf8.decode(data);
        if(message == logs['not_found']) {
          await myShowDialogLog(
            context: context,
            log: 'No duplicates found',
          );
        } else if(message == logs['success']) {
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
        }
      }
    },
  );
}

Future<void> onDeleteDuplicatePressed(BuildContext context) async {
  await sendTo(
    context: context,
    msg: commands['delete_duplicate']!,
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
    msg: commands['backup']!,
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
    msg: commands['update_database']!,
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

Future<void> onSyncDatabaseLocallyPressed(BuildContext context) async {
  List<int> buffer = [];
  Directory? directory = await getExternalStorageDirectory();
  File file = File('${directory!.path}/import.csv');
  await sendTo(
    context: context,
    msg: commands['get_database_file']!,
    recordsMode: true,
    onData: (data) async {
      String message = utf8.decode(data);
      if(logs['success']!.contains(message)) {
        if(message != logs['success']) {
          message.replaceAll(logs['success']!, '');
          buffer += utf8.encode(message);
        }
        file.writeAsBytesSync(buffer);
        await myShowDialogLog(
          context: context,
          log: 'Database update completed successfully',
        );
      } else {
        buffer += data;
      }
    },
  );
}