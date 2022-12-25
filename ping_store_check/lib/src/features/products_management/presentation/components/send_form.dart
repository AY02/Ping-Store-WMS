import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/products_management/domain/product_domain.dart';
import 'package:ping_store_check/src/features/socket_connection/domain/socket_provider.dart';
import 'package:provider/provider.dart';

class MySendForm extends StatefulWidget {
  const MySendForm({super.key, required this.barcode});
  final String barcode;
  @override
  State<MySendForm> createState() => _MySendFormState();
}

class _MySendFormState extends State<MySendForm> {
  
  final List<TextEditingController> _controllers = List.generate(
    fields.length,
    (i) => TextEditingController(),
  );

  TextFormField barcodeField() {
    _controllers[0].text = widget.barcode;
    return TextFormField(
      controller: _controllers[0],
      decoration: InputDecoration(hintText: fields[0]),
    );
  }

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    for(int i=0; i<_controllers.length; i++) {
      _controllers[i].dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Column(
        children: <Widget>[
          barcodeField(),
          for(int i=1; i<fields.length; i++) TextFormField(
            controller: _controllers[i],
            decoration: InputDecoration(hintText: fields[i]),
          ),
          ElevatedButton(
            onPressed: () {
              String record = '';
              for(int i=0; i<fields.length; i++) {
                record += _controllers[i].text;
                if(i != fields.length-1) {
                  record += ';';
                }
              }
              context.read<SocketProvider>().client.write('!add $record');
              Navigator.pop(context);
            },
            child: const Text('Send'),
          ),
        ],
      ),
    );
  }
}