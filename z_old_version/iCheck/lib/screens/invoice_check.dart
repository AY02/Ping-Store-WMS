import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:icheck/constants.dart';
import 'package:icheck/generic_components/scan_button.dart';
import 'package:icheck/generic_components/search_button.dart';
import 'package:icheck/generic_components/select_file_button.dart';
import 'package:icheck/screens/show_good.dart';
import 'package:icheck/services/file_manager.dart';
import 'package:icheck/services/scan.dart';

class InvoiceCheckScreen extends StatefulWidget {
  @override
  _InvoiceCheckScreenState createState() => _InvoiceCheckScreenState();
}

class _InvoiceCheckScreenState extends State<InvoiceCheckScreen> {

  final TextEditingController _barcodeController = TextEditingController();
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  List<FileManager> _fileManagers = [];
  List<String> _filenames = [];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Container(
              color: Colors.blue,
              width: getWidth(context: context, percentage: 80),
              height: getHeight(context: context, percentage: 20),
              child: ListView.separated(
                itemCount: _filenames.length,
                physics: BouncingScrollPhysics(),
                separatorBuilder: (context, index) => Divider(color: Colors.black),
                padding: EdgeInsets.symmetric(
                  horizontal: getWidth(context: context, percentage: 5),
                  vertical: getHeight(context: context, percentage: 1),
                ),
                itemBuilder: (context, index) => Text(
                  _filenames[index],
                  textAlign: TextAlign.center,
                ),
              ),
            ),
            SelectFileButton(
              onPressed: () async {
                FilePickerResult result = await FilePicker.platform.pickFiles(
                  allowMultiple: true,
                  type: FileType.custom,
                  allowedExtensions: EXTENSIONS_ALLOWED,
                );
                log(result.paths[0]);
                if(result == null) return;
                for(int i=0; i<result.count; i++) {
                  _fileManagers.add(FileManager(
                    file: File(result.paths[i]),
                  ));
                  setState(() =>_filenames.add(_fileManagers[i].filename));
                }
              },
            ),
            Form(
              key: _formKey,
              child: Column(
                children: <Widget>[
                  TextFormField(
                    controller: _barcodeController,
                    decoration: InputDecoration(hintText: FIELDS[0]),
                    validator: (value) => (value.isEmpty) ? 'Il campo è vuoto' : null,
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: <Widget>[ 
                      ScanButton(
                        onPressed: () async => setState(
                          () async => _barcodeController.text = await scan(),
                        ),
                      ),
                      SearchButton(
                        onPressed: () async {
                          if(!_formKey.currentState.validate()) return;
                          String _good = '';
                          String _barcode = _barcodeController.text;
                          for(int i=0; i<_fileManagers.length; i++)
                            if(_fileManagers[i].contains(_barcode)) {
                              _good = _fileManagers[i].lineFromText(_barcode);
                              _fileManagers[i].removeLineFromText(_barcode);
                              String externalPath = await getAccessExternalPath();
                              _fileManagers[i].copyTo(externalPath + '/${_fileManagers[i].filename}');
                              break;
                            }
                          await Navigator.push(context, MaterialPageRoute(
                            builder: (context) => ShowGoodScreen(good: _good),
                          ));
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}