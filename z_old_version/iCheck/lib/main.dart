import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:icheck/screens/homepage.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
    ]);
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Flutter iCheck App',
      home: HomepageScreen(),
    );
  }
}