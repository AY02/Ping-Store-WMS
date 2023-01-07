import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/socket_connection/domain/socket_provider.dart';
import 'package:provider/provider.dart';

Future<bool> connectToServer(BuildContext context, String ip, int port) async {
  try {
    var socketProvider =  context.read<SocketProvider>();
    socketProvider.client = await Socket.connect(ip, port);
    socketProvider.connected = true;
    socketProvider.subscription = socketProvider.client.listen(((event) {}));
    Timer.periodic(const Duration(seconds: 5), (timer) {
      if(socketProvider.connected) {
        socketProvider.client.write('!ping');
      } else {
				timer.cancel();
			}
    });
    return true;
  } on SocketException {
    return false;
  }
}

Future<void> disconnectFromServer(BuildContext context) async {
  var socketProvider =  context.read<SocketProvider>();
  await socketProvider.subscription.cancel();
  await socketProvider.client.close();
  socketProvider.client.destroy();
  socketProvider.connected = false;
}