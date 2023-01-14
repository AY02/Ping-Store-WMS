import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/products%20management/application/on_pressed_functions.dart';
import 'package:ping_store_check/src/features/products%20management/data/products_data.dart';

class MyBarcodeForm extends StatefulWidget {
  final String barcode;
  final bool mode;
  const MyBarcodeForm({
    super.key,
    required this.barcode,
    required this.mode,
  });
  @override
  State<MyBarcodeForm> createState() => _MyBarcodeFormState();
}

class _MyBarcodeFormState extends State<MyBarcodeForm> {
  
  final TextEditingController _barcodeController = TextEditingController();

  TextFormField _barcodeField() {
    _barcodeController.text = widget.barcode;
    return TextFormField(
      controller: _barcodeController,
      decoration: InputDecoration(hintText: fields[0]),
    );
  }

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _barcodeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        _barcodeField(),
        ElevatedButton(
          onPressed: () async => await onSendBarcode(
            context,
            widget.mode,
            _barcodeController.text,
          ),
          child: Text(widget.mode == searchMode ? 'Search' : 'Delete'),
        ),
      ],
    );
  }
}