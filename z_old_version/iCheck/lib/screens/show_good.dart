import 'package:flutter/material.dart';
import 'package:icheck/constants.dart';

class ShowGoodScreen extends StatelessWidget {

  final String good;

  ShowGoodScreen({
    @required this.good,
  });

  @override
  Widget build(BuildContext context) {
    List<String> fieldContent = (good.isNotEmpty) ? good.split(';') : 
      List.generate(FIELDS.length, (index) => '');
    return Scaffold(
      body: Center(
        child: Table(
          border: TableBorder.all(width: 1),
          children: List.generate(
            fieldContent.length, 
            (index) => TableRow(
              children: <TableCell>[
                TableCell(child: Text(FIELDS[index])),
                TableCell(child: Text(fieldContent[index])),
              ],
            ),
          ),
        ),
      ),
    );
  }
}