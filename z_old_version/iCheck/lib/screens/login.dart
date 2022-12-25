import 'package:flutter/material.dart';
import 'package:icheck/constants.dart';
import 'package:icheck/generic_components/text_button.dart';
import 'package:icheck/screens/invoice_check.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {

  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Form(
        key: _formKey,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            TextFormField(
              controller: _usernameController,
              decoration: InputDecoration(hintText: 'Nome Utente'),
              validator: (value) {
                if(value.isEmpty)
                  return 'Il campo è vuoto';
                if(value.toLowerCase() != CREDENTIALS['username'])
                  return 'Nome utente errato';
                return null;
              }
            ),
            TextFormField(
              controller: _passwordController,
              decoration: InputDecoration(hintText: 'Password'),
              validator: (value) {
                if(value.isEmpty)
                  return 'Il campo è vuoto';
                if(value != CREDENTIALS['password'])
                  return 'Password errata';
                return null;
              }
            ),
            MyTextButton(
              text: 'Login',
              icon: Icons.login,
              onPressed: () async {
                if(!_formKey.currentState.validate()) return;
                await Navigator.push(context, MaterialPageRoute(
                  builder: (context) => InvoiceCheckScreen(),
                ));
              },
            ),
          ],
        ),
      ),
    );
  }
}