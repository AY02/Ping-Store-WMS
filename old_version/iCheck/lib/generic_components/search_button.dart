import 'package:flutter/material.dart';
import 'package:icheck/generic_components/text_button.dart';

class SearchButton extends StatelessWidget {

  final void Function() onPressed;

  SearchButton({
    @required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return MyTextButton(
      text: 'CERCA PRODOTTO', 
      icon: Icons.search,
      onPressed: onPressed,
    );
  }
}