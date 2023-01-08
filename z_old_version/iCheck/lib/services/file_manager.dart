import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';

class FileManager {

  final File file;

  FileManager({@required this.file});
  
  bool get fileExists => file.existsSync();
  bool get fileNotExists => !file.existsSync();
  bool contains(String str) => read.contains(new RegExp(str, caseSensitive: false));

  String get read => this.file.readAsStringSync();
  String get filename => basename(this.file.path);
  String get path => this.file.path;

  String lineFromText(String str) {
    for(String i in this.file.readAsLinesSync(encoding: utf8))
      if(i.toLowerCase().contains(str.toLowerCase()))
        return i;
    return null;
  }
  
  void removeLineFromText(String str) {
    List<String> lines = file.readAsLinesSync();
    for(int i=0; i<lines.length; i++)
      if(lines[i].contains(str)) {
        lines.removeAt(i);
        file.writeAsStringSync(lines.join('\n'));
        return;
      }
  }

  void copyTo(String path) => file.copySync(path);

}

Future<String> getAccessExternalPath() async => await getExternalStorageDirectory().then(
  (path) => path.path,
);