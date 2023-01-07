import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';

class SocketProvider with ChangeNotifier {

  late Socket client;
  late StreamSubscription subscription;
  
  bool _connected = false;
  
  bool get connected => _connected;

  set connected(bool connected) {
    _connected = connected;
    notifyListeners();
  }
  
}