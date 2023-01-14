import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/products%20management/application/on_pressed_functions.dart';
import 'package:ping_store_check/src/features/products%20management/data/products_data.dart';

class MyRecordForm extends StatefulWidget {
  final List<String> record;
  final bool mode;
  const MyRecordForm({
    super.key,
    required this.record,
    required this.mode,
  });
  @override
  State<MyRecordForm> createState() => _MyRecordFormState();
}

class _MyRecordFormState extends State<MyRecordForm> {
  
  final List<TextEditingController> _controllers = List.generate(
    fields.length,
    (i) => TextEditingController(),
  );

  TextFormField _field(int i) {
    _controllers[i].text = widget.record[i];
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
          for(int i=0; i<fields.length; i++) _field(i),
          ElevatedButton(
            onPressed: () async => await onSendRecord(context, widget.mode, _controllers),
            child: Text(widget.mode == addMode ? 'Add' : 'Edit'),
          ),
        ],
      ),
    );
  }
}