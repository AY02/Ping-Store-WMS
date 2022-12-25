import 'package:flutter/material.dart';
import 'package:icheck/constants.dart';
import 'package:icheck/generic_components/scan_button.dart';
import 'package:icheck/generic_components/search_button.dart';
import 'package:icheck/services/scan.dart';
import 'package:icheck/services/file_manager.dart';
import 'package:icheck/screens/show_good.dart';

class SearchGoodsScreen extends StatefulWidget {
  
  final FileManager fileManager;

  SearchGoodsScreen({
    @required this.fileManager,
  });

  @override
  _SearchGoodsScreenState createState() => _SearchGoodsScreenState();
}

class _SearchGoodsScreenState extends State<SearchGoodsScreen> {

  final TextEditingController _barcodeController = TextEditingController();
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Form(
        key: _formKey,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
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
                    String good = (widget.fileManager.contains(_barcodeController.text)) ? 
                      widget.fileManager.lineFromText(_barcodeController.text) : '';
                    await Navigator.push(context, MaterialPageRoute(
                      builder: (context) => ShowGoodScreen(good: good),
                    ));
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}