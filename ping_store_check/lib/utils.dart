import 'package:flutter/material.dart';

double getHeight({
  required BuildContext context, 
  required double percentage,
}) => MediaQuery.of(context).size.height*percentage/100;

double getWidth({
  required BuildContext context, 
  required double percentage,
}) => MediaQuery.of(context).size.width*percentage/100;

void log({
  required String text,
  String type='General',
// ignore: avoid_print
}) => print('log $type --> $text');
