import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/products%20management/application/on_pressed_functions.dart';
import 'package:ping_store_check/src/features/products%20management/data/products_data.dart';
import 'package:shared_preferences/shared_preferences.dart';

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

  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  
  final List<TextEditingController> _controllers = List.generate(
    fields.length,
    (i) => TextEditingController(),
  );

  TextFormField _field(int i) {
    if(widget.mode == editMode || i == 0) _controllers[i].text = widget.record[i];
    return TextFormField(
      controller: _controllers[i],
      decoration: InputDecoration(hintText: fields[i]),
      validator: (i==0 || i==7) ? (value) {
        if(i == 0) {
          RegExp barcodeValidator = RegExp(r'^\d{13}$');
          if(!barcodeValidator.hasMatch(value!)) return 'Invalid Barcode';
        } else {
          RegExp priceValidator = RegExp(r'^\d+.\d{2}$');
          if(!priceValidator.hasMatch(value!)) return 'Invalid Price';
        }
        return null;
      } : null,
    );
  }

  Future<void> _loadRecordData() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      for(int i=0; i<fields.length; i++) {
        if([2,4,5,6,7].contains(i)) {
          _controllers[i].text = prefs.getString(fields[i]) ?? '';
        }
      }
    });
  }

  Future<void> _saveRecordData() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    for(int i=0; i<fields.length; i++) {
      if([2,4,5,6,7].contains(i)) {
        await prefs.setString(fields[i], _controllers[i].text);
      }
    }
  }

  Future<void> _clearRecordData() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    for(int i=0; i<fields.length; i++) {
      if([2,4,5,6,7].contains(i)) {
        await prefs.remove(fields[i]);
      }
      _controllers[i].text = '';
    }
  }

  @override
  void initState() {
    super.initState();
    if(widget.mode == addMode) _loadRecordData();
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
      child: Form(
        key: _formKey,
        child: Column(
          children: <Widget>[
            for(int i=0; i<fields.length; i++) _field(i),
            ElevatedButton(
              onPressed: () async {
                if(!_formKey.currentState!.validate()) return;
                await onSendRecord(context, widget.mode, _controllers);
                if(widget.mode == addMode) await _saveRecordData();
              },
              child: Text(widget.mode == addMode ? 'Add' : 'Edit'),
            ),
            if(widget.mode == addMode) ElevatedButton(
              onPressed: () async => await _clearRecordData(),
              child: const Text('Clear'),
            ),
          ],
        ),
      ),
    );
  }
}