import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/products_management/domain/product_domain.dart';
import 'package:ping_store_check/src/features/socket_connection/data/socket_data.dart';

class MyEditForm extends StatefulWidget {
  const MyEditForm({super.key, required this.foundRecord});
  final List<String> foundRecord;
  @override
  State<MyEditForm> createState() => _MyEditFormState();
}

class _MyEditFormState extends State<MyEditForm> {
  
  final List<TextEditingController> _controllers = List.generate(
    fields.length,
    (i) => TextEditingController(),
  );

  TextFormField textField(int i) {
    _controllers[i].text = widget.foundRecord[i];
    return TextFormField(
      controller: _controllers[i],
      decoration: InputDecoration(hintText: fields[i]),
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
          for(int i=0; i<fields.length; i++) textField(i),
          ElevatedButton(
            onPressed: () {
              String record = '';
              for(int i=0; i<fields.length; i++) {
                record += _controllers[i].text;
                if(i < fields.length-1) {
                  record += ';';
                }
              }
              subscription.onData((data) async => await showDialog(
                context: context,
                builder: (context) => Dialog(
                  child: Text(utf8.decode(data)),
                ),
              ));
              client.write('!edit ${_controllers[0].text} $record');
              Navigator.pop(context);
            },
            child: const Text('Edit'),
          ),
        ],
      ),
    );
  }
}