import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/socket_connection/data/socket_data.dart';
import 'package:ping_store_check/src/features/socket_connection/domain/socket_provider.dart';
import 'package:provider/provider.dart';

Future<bool> connectToServer(BuildContext context, String ip, int port) async {
  try {
    var socketProvider =  context.read<SocketProvider>();
    client = await Socket.connect(ip, port);
    socketProvider.connected = true;
    subscription = client.listen(null);
    subscription.onDone(() async => await disconnectFromServer(context));
    return true;
  } catch(e) {
    return false;
  }
}

Future<void> disconnectFromServer(BuildContext context) async {
  try {
    var socketProvider =  context.read<SocketProvider>();
    await subscription.cancel();
    await client.close();
    client.destroy();
    socketProvider.connected = false;
  } catch(e) {
    return;
  }
}