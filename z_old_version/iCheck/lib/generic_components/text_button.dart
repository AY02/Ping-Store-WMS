import 'package:flutter/material.dart';

class MyTextButton extends StatelessWidget {
  
  final String text;
  final IconData icon;
  final void Function() onPressed;

  MyTextButton({
    @required this.text,
    @required this.icon,
    @required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return TextButton.icon(
      icon: Icon(icon, color: Colors.white),
      label: Text(text, style: TextStyle(color: Colors.white)),
      style: TextButton.styleFrom(backgroundColor: Colors.blue),
      onPressed: onPressed,
    );
  }
}