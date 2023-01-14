import 'package:flutter/material.dart';
import 'package:ping_store_check/src/features/products%20management/application/on_pressed_functions.dart';
import 'package:ping_store_check/src/generic%20components/my_gridview.dart';

class MyProductManagement extends StatelessWidget {
  const MyProductManagement({super.key});
  @override
  Widget build(BuildContext context) {
    return MyGridView(
      children: <ElevatedButton>[
        ElevatedButton.icon(
          onPressed: () async => await onAdd(context),
          icon: const Icon(Icons.add),
          label: const Text('ADD'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await onEdit(context),
          icon: const Icon(Icons.edit),
          label: const Text('EDIT'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await onSearch(context),
          icon: const Icon(Icons.search),
          label: const Text('SEARCH'),
        ),
        ElevatedButton.icon(
          onPressed: () async => await onDelete(context),
          icon: const Icon(Icons.delete),
          label: const Text('DELETE'),
        ),
      ],
    );
  }
}