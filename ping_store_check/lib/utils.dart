import 'package:flutter/material.dart';

double widthPercentage(BuildContext context, double percentage) =>
  MediaQuery.of(context).size.width*percentage/100;

double heigthPercentage(BuildContext context, double percentage) =>
  MediaQuery.of(context).size.height*percentage/100;
