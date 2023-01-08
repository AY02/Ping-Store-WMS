import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/socket_connection/application/socket_connection.dart';
import 'package:ping_store_check/src/features/socket_connection/data/socket_data.dart';
import 'package:ping_store_check/src/features/socket_connection/domain/socket_provider.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MySocketForm extends StatefulWidget {
  const MySocketForm({super.key});
  @override
  State<MySocketForm> createState() => _MySocketFormState();
}

class _MySocketFormState extends State<MySocketForm> {

  final _formKey = GlobalKey<FormState>();
  
  final _ipController = TextEditingController();
  final _portController = TextEditingController();

  Future<void> _loadSocketData() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _ipController.text = prefs.getString('ip') ?? '';
      _portController.text = prefs.getString('port') ?? '';
    });
  }
  
  Future<void> _saveSocketData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('ip', _ipController.text);
    await prefs.setString('port', _portController.text);
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
    try {
      subscription.onDone(() async => await disconnectFromServer(context));
    // ignore: empty_catches
    } catch(e) {}
    bool connected = context.watch<SocketProvider>().connected;
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TextFormField(
            enabled: !connected,
            decoration: const InputDecoration(hintText: 'IP Address'),
            controller: _ipController,
          ),
          TextFormField(
            enabled: !connected,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(hintText: 'Port'),
            controller: _portController,
          ),
          ElevatedButton(
            onPressed: () async {
              if(connected) {
                await disconnectFromServer(context);
              } else {
                bool success = await connectToServer(
                  context,
                  _ipController.text,
                  int.parse(_portController.text),
                );
                if(success) {
                  await _saveSocketData();
                }
              }
            },
            child: Text(connected ? 'Disconnect' : 'Connect'),
          ),
          Text(connected ? 'Connected' : 'Not connected'),
        ],
      ),
    );
  }
}