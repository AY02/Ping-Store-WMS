import 'package:flutter/material.dart';

double getHeight({
  @required BuildContext context, 
  @required double percentage,
}) => MediaQuery.of(context).size.height*percentage/100;

double getWidth({
  @required BuildContext context, 
  @required double percentage,
}) => MediaQuery.of(context).size.width*percentage/100;

void log(
  String str, 
  {String type='General'}
) => print('log $type --> $str');

const List<String> FIELDS = [
  'Barcode', 'Descrizione', 
  'Quantità', 'Reparto', 
  'Scorta', 'Fornitore', 
  'Costo', 'Prezzo 1', 
  'Prezzo 2', 'Prezzo 3', 
  'Note', 'Immagini',
];

const Map<String, dynamic> CREDENTIALS = {
  'host': '192.168.1.42',
  'port': 3000,
  'username': 'ysd',
  'password': '1974',
};

const String IMPORT_FILE_KEY = 'IMPORT_FILE';

const List<String> EXTENSIONS_ALLOWED = ['txt'];