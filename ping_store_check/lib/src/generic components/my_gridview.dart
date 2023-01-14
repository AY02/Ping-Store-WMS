import 'package:flutter/material.dart';
import 'package:ping_store_check/utils.dart';

class MyGridView extends StatelessWidget {

  final List<Widget> children;

  const MyGridView({
    super.key,
    required this.children
  });

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      padding: EdgeInsets.symmetric(
        vertical: getHeight(context: context, percentage: 6),
        horizontal: getWidth(context: context, percentage: 12),
      ),
      crossAxisCount: 2,
      mainAxisSpacing: getHeight(context: context, percentage: 3),
      crossAxisSpacing: getWidth(context: context, percentage: 6),
      children: children,
    );
  }
}
