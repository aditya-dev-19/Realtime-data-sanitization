import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/cupertino.dart';
import '../providers/system_status_provider.dart';
import '../providers/auth_provider.dart';
import '../providers/theme_provider.dart'; // ADD THIS IMPORT
import 'login_screen.dart';

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
              'Auto-Lock',
              'Automatically lock the app when inactive',
              false,
            ),
            const SizedBox(height: 8),
            
            // Sign Out Button
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16.0),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    final shouldLogout = await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Sign Out'),
                        content: const Text('Are you sure you want to sign out?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(false),
                            child: const Text('CANCEL'),
                          ),
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(true),
                            style: TextButton.styleFrom(
                              foregroundColor: Colors.red,
                            ),
                            child: const Text('SIGN OUT'),
                          ),
                        ],
                      ),
                    );

                    if (shouldLogout == true) {
                      await context.read<AuthProvider>().logout();
                      
                      if (context.mounted) {
                        Navigator.of(context).pushAndRemoveUntil(
                          MaterialPageRoute(builder: (context) => const LoginScreen()),
                          (route) => false,
                        );
                      }
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Colors.red[50],
                    foregroundColor: Colors.red,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: BorderSide(color: Colors.red.shade200),
                    ),
                  ),
                  icon: const Icon(Icons.logout, size: 20),
                  label: const Text(
                    'Sign Out',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            
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
    // Use Consumer to listen to ThemeProvider changes
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        final isDark = themeProvider.themeMode == ThemeMode.dark;
        
        return SwitchListTile(
          title: const Text('Dark Mode'),
          subtitle: const Text('Use dark theme'),
          value: isDark,
          onChanged: (bool value) {
            // Toggle the theme when switch is changed
            themeProvider.toggleTheme();
          },
        );
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