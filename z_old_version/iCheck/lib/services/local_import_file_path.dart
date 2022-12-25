import 'package:icheck/constants.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LocalImportFilePath {

  final String _importFileKey = IMPORT_FILE_KEY;

  Future<void> clear() async => await SharedPreferences.getInstance().then(
    (prefs) => prefs.clear()
  );
  
  Future<String> getFilePath() async => await SharedPreferences.getInstance().then(
    (prefs) => (prefs.getString(_importFileKey) != null) ? prefs.getString(_importFileKey) : '',
  );

  Future<void> setFilePath(String filePath) async => await SharedPreferences.getInstance().then(
    (prefs) async => await getFilePath().then(
      (path) async {
        if(path.isNotEmpty)
          await prefs.remove(_importFileKey);
        await prefs.setString(_importFileKey, filePath);
      }
    ),
  );

}