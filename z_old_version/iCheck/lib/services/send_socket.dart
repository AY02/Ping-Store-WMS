import 'dart:io';
import 'package:flutter/material.dart';
import 'package:icheck/constants.dart';

Future<bool> sendTo({
  @required String line, 
  @required String host, 
  @required int port,
}) async {
  log('Connect to the server $host:$port...', type: 'Socket Check');
  try {
    Socket s = await Socket.connect(host, port);
    log('Successful connection to the server, I submit the record $line...', type: 'Socket Check');
    s.write(line);
    log('Record sent, I close the socket ...', type: 'Socket Check');
    s.close();
    log('Successful closure', type: 'Socket Check');
    return true;
  } catch(e) {
    log('Socket connection error: $e', type: 'Socket Error');
  }
  return false;
}