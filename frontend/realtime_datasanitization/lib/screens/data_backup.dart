import 'package:flutter/material.dart';

class DataBackupScreen extends StatelessWidget {
  const DataBackupScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Data Backup")),
      body: const Center(
        child: Text("Data Backup Page"),
      ),
    );
  }
}
