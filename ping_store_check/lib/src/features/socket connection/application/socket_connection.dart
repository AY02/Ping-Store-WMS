import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:ping_store_check/constants.dart';
import 'package:ping_store_check/src/features/socket%20connection/data/socket_data.dart';
import 'package:ping_store_check/src/generic%20components/my_dialog_log.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<void> sendTo({
  required BuildContext context,
  required String msg,
  bool recordsMode = false,
  Future<void> Function(Uint8List)? onData,
}) async {
  SharedPreferences prefs = await SharedPreferences.getInstance();
  String ip = prefs.getString(ipKey) ?? '';
  String port = prefs.getString(portKey) ?? '';
  if(ip.isEmpty || port.isEmpty) {
    await myShowDialogLog(
      context: context,
      log: 'IP address or port not defined',
    );
    return;
  }
  try {
    Socket client = await Socket.connect(ip, int.parse(port));
    client.listen((data) async {
      await onData!(data);
      if(recordsMode) {
        if(utf8.decode(data) == logs['success']) {
          client.destroy();
          await client.close();
        } else {
          client.write(logs['ping']);
        }
      } else {
        client.destroy();
        await client.close();
      }
    });
    client.write(msg);
  } catch(e) {
    await myShowDialogLog(
      context: context,
      log: 'Socket Connection error: ${e.toString()}',
    );
  }
}