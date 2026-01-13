import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';

class LoginScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<AuthService>(context, listen: false);

    return Scaffold(
      appBar: AppBar(title: Text("Login")),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text("Subscribo", style: Theme.of(context).textTheme.headlineMedium),
              SizedBox(height: 40),
              // In production, add Google Sign In Button here
              ElevatedButton.icon(
                icon: Icon(Icons.person),
                label: Text("Continue as Guest (Anonymous)"),
                onPressed: () async {
                  await authService.signInAnonymously();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
