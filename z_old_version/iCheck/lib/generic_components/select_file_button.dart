import 'package:flutter/material.dart';
import 'package:icheck/generic_components/text_button.dart';

class SelectFileButton extends StatelessWidget {

  final void Function() onPressed;

  SelectFileButton({
    @required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return MyTextButton(
      text: 'SELEZIONA FILE', 
      icon: Icons.upload_file,
      onPressed: onPressed,
    );
  }
}