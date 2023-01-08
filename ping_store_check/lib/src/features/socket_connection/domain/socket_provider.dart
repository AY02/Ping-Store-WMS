import 'package:flutter/material.dart';

class SocketProvider with ChangeNotifier {
  
  bool _connected = false;

  bool get connected => _connected;
  
  set connected(bool connected) {
    _connected = connected;
    notifyListeners();
  }

}