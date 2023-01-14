import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/database%20control/application/on_pressed_functions.dart';
import 'package:ping_store_check/src/generic%20components/my_gridview.dart';

class MyDatabaseControl extends StatelessWidget {
  const MyDatabaseControl({super.key});

  @override
  Widget build(BuildContext context) {
    return MyGridView(
      children: <ElevatedButton>[
        ElevatedButton.icon(
          onPressed: () async => await onShowDuplicatePressed(context),
          icon: const Icon(Icons.view_agenda),
          label: const Text('SHOW DUPLICATE'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await onDeleteDuplicatePressed(context),
          icon: const Icon(Icons.delete),
          label: const Text('DELETE DUPLICATE'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await onBackupDatabasePressed(context),
          icon: const Icon(Icons.backup),
          label: const Text('BACKUP DATABASE'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await onUpdateDatabasePressed(context),
          icon: const Icon(Icons.update),
          label: const Text('UPDATE DATABASE'),
        ),
      ],
    );
  }
}