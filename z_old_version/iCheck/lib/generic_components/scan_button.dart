import 'package:flutter/material.dart';
import 'package:icheck/generic_components/text_button.dart';

class ScanButton extends StatelessWidget {
  
  final void Function() onPressed;

  ScanButton({
    @required this.onPressed,
  });
  
  @override
  Widget build(BuildContext context) {
    return MyTextButton(
      text: 'SCAN', 
      icon: Icons.settings_overscan,
      onPressed: onPressed,
    );
  }
}