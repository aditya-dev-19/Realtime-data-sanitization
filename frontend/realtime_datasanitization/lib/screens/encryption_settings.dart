import 'package:flutter/material.dart';

class EncryptionSettingsScreen extends StatelessWidget {
  const EncryptionSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Encryption Settings")),
      body: const Center(
        child: Text("Encryption Settings Page"),
      ),
    );
  }
}
