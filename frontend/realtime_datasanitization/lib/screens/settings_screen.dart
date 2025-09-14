import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/system_status_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<SystemStatusProvider>().fetchSystemStatus();
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSectionHeader('Appearance'),
            _buildThemeSetting(context),
            const Divider(),
            
            _buildSectionHeader('Notifications'),
            _buildNotificationSetting(
              'Security Alerts',
              'Get notified about security events',
              true,
            ),
            _buildNotificationSetting(
              'System Updates',
              'Be notified about app updates',
              true,
            ),
            const Divider(),
            
            _buildSectionHeader('Security'),
            _buildSecuritySetting(
              'Enable Biometric Authentication',
              'Use fingerprint or face ID to secure the app',
              false,
            ),
            _buildSecuritySetting(
              'Auto-lock',
              'Lock app after 5 minutes of inactivity',
              true,
            ),
            const Divider(),
            
            _buildSectionHeader('About'),
            ListTile(
              title: const Text('Version'),
              subtitle: const Text('1.0.0'),
              trailing: IconButton(
                icon: const Icon(Icons.info_outline),
                onPressed: () {
                  _showAboutDialog(context);
                },
              ),
            ),
            const SizedBox(height: 32),
            
            // Logout button
            Center(
              child: ElevatedButton.icon(
                onPressed: () {
                  // TODO: Implement logout
                },
                icon: const Icon(Icons.logout),
                label: const Text('Sign Out'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 12,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: Colors.blue,
        ),
      ),
    );
  }

  Widget _buildThemeSetting(BuildContext context) {
    return SwitchListTile(
      title: const Text('Dark Mode'),
      subtitle: const Text('Use dark theme'),
      value: Theme.of(context).brightness == Brightness.dark,
      onChanged: (bool value) {
        // TODO: Implement theme switching
      },
    );
  }

  Widget _buildNotificationSetting(String title, String subtitle, bool value) {
    return SwitchListTile(
      title: Text(title),
      subtitle: Text(subtitle),
      value: value,
      onChanged: (bool newValue) {
        // TODO: Implement notification settings
      },
    );
  }

  Widget _buildSecuritySetting(String title, String subtitle, bool value) {
    return SwitchListTile(
      title: Text(title),
      subtitle: Text(subtitle),
      value: value,
      onChanged: (bool newValue) {
        // TODO: Implement security settings
      },
    );
  }

  void _showAboutDialog(BuildContext context) {
    showAboutDialog(
      context: context,
      applicationName: 'AI Cybersecurity',
      applicationVersion: '1.0.0',
      applicationIcon: const Icon(
        Icons.security,
        size: 50,
        color: Colors.blue,
      ),
      children: const [
        SizedBox(height: 16),
        Text('A powerful cybersecurity app for threat detection and prevention.'),
        SizedBox(height: 8),
        Text('© 2023 AI Cybersecurity. All rights reserved.'),
      ],
    );
  }
}
