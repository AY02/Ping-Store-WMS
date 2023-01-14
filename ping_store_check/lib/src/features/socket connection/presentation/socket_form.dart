import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/socket%20connection/data/socket_data.dart';
import 'package:ping_store_check/src/generic%20components/my_dialog_log.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MySocketForm extends StatefulWidget {
  const MySocketForm({super.key});
  @override
  State<MySocketForm> createState() => _MySocketFormState();
}

class _MySocketFormState extends State<MySocketForm> {

  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  
  final TextEditingController _ipController = TextEditingController();
  final TextEditingController _portController = TextEditingController();

  Future<void> _loadSocketData() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    String ip = prefs.getString(ipKey) ?? '';
    String port = prefs.getString(portKey) ?? '';
    if(ip.isNotEmpty || port.isNotEmpty) {
      setState(() {
        _ipController.text = prefs.getString(ipKey) ?? '';
        _portController.text = prefs.getString(portKey) ?? '';
      });
    }
  }
  
  Future<void> _saveSocketData() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString(ipKey, _ipController.text);
    await prefs.setString(portKey, _portController.text);
  }

  @override
  void initState() {
    super.initState();
    _loadSocketData();
  }

  @override
  void dispose() {
    _ipController.dispose();
    _portController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          TextFormField(
            validator: (value) {
              RegExp ipValidator = RegExp(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$');
              if(!ipValidator.hasMatch(value!)) return 'Invalid IP Address';
              return null;
            },
            decoration: const InputDecoration(hintText: 'IP Address'),
            controller: _ipController,
          ),
          TextFormField(
            validator: (value) {
              RegExp portValidator = RegExp(r'^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$');
              if(!portValidator.hasMatch(value!)) return 'Invalid Port';
              return null;
            },
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(hintText: 'Port'),
            controller: _portController,
          ),
          ElevatedButton(
            onPressed: () async {
              if(!_formKey.currentState!.validate()) return;
              await _saveSocketData().then((_) async {
                await myShowDialogLog(
                  context: context,
                  log: 'IP address and port saved successfully',
                );
              });
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}