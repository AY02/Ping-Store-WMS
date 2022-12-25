import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/socket_connection/application/socket_connection.dart';
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
  
  final ipController = TextEditingController();
  final portController = TextEditingController();

  Future<void> _loadSocketData() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      ipController.text = prefs.getString('ip') ?? '';
      portController.text = prefs.getString('port') ?? '';
    });
  }
  
  Future<void> _saveSocketData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('ip', ipController.text);
    await prefs.setString('port', portController.text);
  }

  @override
  void initState() {
    super.initState();
    _loadSocketData();
  }

  @override
  void dispose() {
    ipController.dispose();
    portController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
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
            controller: ipController,
          ),
          TextFormField(
            enabled: !connected,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(hintText: 'Port'),
            controller: portController,
          ),
          ElevatedButton(
            onPressed: connected ? () async => await disconnectFromServer(context) : () async {
              bool success = await connectToServer(
                context,
                ipController.text,
                int.parse(portController.text),
              );
              if(success) {
                await _saveSocketData();
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