import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/socket_connection/application/socket_connection.dart';
import 'package:ping_store_check/src/features/socket_connection/data/socket_data.dart';
import 'package:ping_store_check/utils.dart';
import 'package:ping_store_check/src/features/socket_connection/domain/socket_provider.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';


class MyDatabaseControl extends StatelessWidget {
  const MyDatabaseControl({super.key});

  Future<void> _onPressed(BuildContext context, String command) async {
    var socketProvider =  context.read<SocketProvider>();
    if(!socketProvider.connected) {
      final prefs = await SharedPreferences.getInstance();
      String ip = prefs.getString('ip') ?? '';
      String port = prefs.getString('port') ?? '';
      if(port.isNotEmpty && ip.isNotEmpty) {
        // ignore: use_build_context_synchronously
        await connectToServer(context, ip, int.parse(port));
      }
      return;
    }
    subscription.onData((data) async {
      await showDialog(
        context: context,
        builder: (context) {
          if(command == '!show_duplicate') {
            List<dynamic> records = json.decode(utf8.decode(data));
            return Dialog(
              child: ListView.builder(
                itemCount: records.length,
                itemBuilder: (BuildContext context, int index) => Text(records[index]),
              )
            );
          } else {
            return Dialog(
              child: Text(utf8.decode(data)),
            );
          }
        }
      );
    });
    client.write(command);
  }

  @override
  Widget build(BuildContext context) {
    subscription.onDone(() async => await disconnectFromServer(context));
    return GridView.count(
      padding: EdgeInsets.symmetric(
        vertical: heigthPercentage(context, 6),
        horizontal: widthPercentage(context, 12),
      ),
      crossAxisCount: 2,
      mainAxisSpacing: heigthPercentage(context, 3),
      crossAxisSpacing: widthPercentage(context, 6),
      children: [
        ElevatedButton.icon(
          onPressed: () async => await _onPressed(context, '!show_duplicate'),
          icon: const Icon(Icons.view_agenda),
          label: const Text('SHOW DUPLICATE'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await _onPressed(context, '!delete_duplicate'),
          icon: const Icon(Icons.delete),
          label: const Text('DELETE DUPLICATE'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await _onPressed(context, '!backup'),
          icon: const Icon(Icons.backup),
          label: const Text('BACKUP DATABASE'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await _onPressed(context, '!update_database'),
          icon: const Icon(Icons.update),
          label: const Text('UPDATE DATABASE'),
        ),
      ],
    );
  }
}