import 'package:flutter/material.dart';

class DashboardMainPage extends StatelessWidget {
  const DashboardMainPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        "Dashboard Overview",
        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
      ),
    );
  }
}
