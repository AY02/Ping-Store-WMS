import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:icheck/constants.dart';
import 'package:icheck/generic_components/select_file_button.dart';
import 'package:icheck/screens/add_goods.dart';
import 'package:icheck/screens/login.dart';
import 'package:icheck/screens/search_goods.dart';
import 'package:icheck/generic_components/text_button.dart';
import 'package:icheck/services/file_manager.dart';
import 'package:icheck/services/local_import_file_path.dart';

class HomepageScreen extends StatefulWidget {
  @override
  _HomepageScreenState createState() => _HomepageScreenState();
}

class _HomepageScreenState extends State<HomepageScreen> {

  final LocalImportFilePath _filePathManager = new LocalImportFilePath();

  FileManager _fileManager;
  String _selectedImportFilePath = '';

  Future<void> checkFilePath() async => await _filePathManager.getFilePath().then(
    (importFilePath) {
      if(importFilePath.isEmpty) {
        setState(() => _selectedImportFilePath = 'SELEZIONA UN FILE');
        return;
      }
      setState(() {
        _fileManager = new FileManager(file: File(importFilePath));
        _selectedImportFilePath = _fileManager.filename;
      });
    }
  );

  @override void initState() {
    super.initState();
    checkFilePath();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            MyTextButton(
              text: 'CONTROLLA FATTURE',
              icon: Icons.inventory,
              onPressed: () async => await Navigator.push(context, MaterialPageRoute(
                builder: (context) => LoginScreen(),
              )),
            ),
            MyTextButton(
              text: 'AGGIUNGI MERCE',
              icon: Icons.add,
              onPressed: () async => await Navigator.push(context, MaterialPageRoute(
                builder: (context) => AddGoodsScreen(fileManager: _fileManager),
              )),
            ),
            MyTextButton(
              text: 'CERCA LA MERCE',
              icon: Icons.settings_overscan,
              onPressed: () async => await Navigator.push(context, MaterialPageRoute(
                builder: (context) => SearchGoodsScreen(fileManager: _fileManager),
              )),
            ),
            Padding(
              padding: EdgeInsets.symmetric(
                vertical: getHeight(context: context, percentage: 10),
              ),
              child: Text(
                _selectedImportFilePath,
                textAlign: TextAlign.center,
              ),
            ),
            SelectFileButton(
              onPressed: () async {
                FilePickerResult result = await FilePicker.platform.pickFiles(
                  type: FileType.custom,
                  allowedExtensions: EXTENSIONS_ALLOWED,
                );
                if(result == null) return;
                _fileManager = new FileManager(file: File(result.files.first.path));
                await _filePathManager.setFilePath(result.files.first.path);
                setState(() => _selectedImportFilePath = result.files.first.name);
              },
            ),
          ],
        ),
      ),
    );
  }
}