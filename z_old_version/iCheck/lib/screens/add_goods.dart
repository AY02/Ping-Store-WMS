import 'package:flutter/material.dart';
import 'package:icheck/constants.dart';
import 'package:icheck/generic_components/scan_button.dart';
import 'package:icheck/generic_components/text_button.dart';
import 'package:icheck/services/file_manager.dart';
import 'package:icheck/services/scan.dart';
import 'package:icheck/services/send_socket.dart';

class AddGoodsScreen extends StatefulWidget {
  
  final FileManager fileManager;

  AddGoodsScreen({
    @required this.fileManager,
  });

  @override
  _AddGoodsScreenState createState() => _AddGoodsScreenState();
}

class _AddGoodsScreenState extends State<AddGoodsScreen> {

  final List<TextEditingController> _controllers = List.generate(
    FIELDS.length,
    (index) => TextEditingController()
  );

  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  Future<Widget> insertSuccess() {
    return showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Record inserito con successo', textAlign: TextAlign.center),
        );
      },
    );
  }

  Future<Widget> insertFailed() {
    return showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(
            'Inserimento del record fallito',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.red),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          physics: BouncingScrollPhysics(),
          child: Form(
            key: _formKey,
            child: Column(
              children: <Widget>[
                for(int i=0; i<FIELDS.length; i++)
                  TextFormField(
                    controller: _controllers[i],
                    decoration: InputDecoration(hintText: FIELDS[i]),
                  ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: <Widget>[
                    ScanButton(
                      onPressed: () async => setState(
                        () async => _controllers[0].text = await scan(),
                      ),
                    ),
                    MyTextButton(
                      text: 'Invia', 
                      icon: Icons.send, 
                      onPressed: () async {
                        if(!_formKey.currentState.validate()) return;
                        String good = '';
                        for(int i=0; i<FIELDS.length; i++) {
                          good += _controllers[i].text;
                          if(i != FIELDS.length-1)
                            good += ';';
                        }
                        await sendTo(
                          host: CREDENTIALS['host'],
                          port: CREDENTIALS['port'],
                          line: good,
                        ).then(
                          (success) async => (success) ? await insertSuccess() : await insertFailed(),
                        );
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}