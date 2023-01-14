import 'package:flutter/material.dart';

Future<void> myShowDialogLog({
  required BuildContext context,
  required String log,
}) async {
  await showDialog(
    context: context,
    builder: ((context) {
      return MyDialogLog(log: log);
    })
  );
}

class MyDialogLog extends StatelessWidget {

  final String log;

  const MyDialogLog({
    super.key,
    required this.log,
  });

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Text(log),
    );
  }

}
