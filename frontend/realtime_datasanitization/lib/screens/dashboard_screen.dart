import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/dashboard_provider.dart';
import '../providers/alerts_provider.dart';
import '../providers/system_status_provider.dart';
import '../models/alert.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<DashboardProvider>().fetchDashboardData();
      context.read<AlertsProvider>().fetchAlerts();
      context.read<SystemStatusProvider>().fetchSystemStatus();
    });
  }

  Widget _buildStatusIndicator(String status) {
    final color = status.toLowerCase() == 'healthy' 
        ? Colors.green 
        : status.toLowerCase() == 'degraded' 
            ? Colors.orange 
            : Colors.red;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            status.toUpperCase(),
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(BuildContext context, String title, String value, IconData icon, Color color) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(icon, color: color, size: 20),
                  ),
                  const Spacer(),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                value,
                style: TextStyle(
                  color: isDark ? Colors.white : Colors.black87,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                title,
                style: TextStyle(
                  color: isDark ? Colors.grey[400] : Colors.grey[600],
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getSystemStatusMessage(String status) {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return 'All systems operational';
      case 'degraded':
        return 'Some systems may be experiencing issues';
      case 'critical':
      case 'error':
        return 'Critical system issues detected';
      default:
        return 'Unknown system status';
    }
  }

  List<Widget> _buildComponentStatus(BuildContext context, Map<String, dynamic> components) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final List<Widget> statusWidgets = [];
    
    components.forEach((key, value) {
      final status = value?.toString().toLowerCase() ?? 'unknown';
      Color statusColor;
      IconData statusIcon;
      String displayStatus = status;
      
      if (key == 'Database' && status.contains('error:')) {
        statusColor = Colors.red;
        statusIcon = Icons.error_outline;
        displayStatus = 'error';
      } else if (status == 'ok' || status == 'true' || status == 'enabled' || status == 'loaded') {
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        displayStatus = 'ok';
      } else if (status == 'degraded' || status == 'warning') {
        statusColor = Colors.orange;
        statusIcon = Icons.warning_amber_rounded;
      } else if (status == 'error' || status == 'false' || status == 'disabled') {
        statusColor = Colors.red;
        statusIcon = Icons.error_outline;
      } else {
        statusColor = Colors.grey;
        statusIcon = Icons.help_outline;
      }
      
      final displayKey = key.split('_')
          .map((word) => '${word[0].toUpperCase()}${word.substring(1)}')
          .join(' ');
      
      statusWidgets.add(
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 4.0),
          child: Row(
            children: [
              Icon(statusIcon, color: statusColor, size: 20),
              const SizedBox(width: 8),
              Text(
                displayKey,
                style: TextStyle(
                  color: isDark ? Colors.white70 : Colors.black87,
                  fontSize: 14,
                ),
              ),
              const Spacer(),
              Text(
                displayStatus.toUpperCase(),
                style: TextStyle(
                  color: statusColor,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      );
    });
    
    return statusWidgets;
  }

  @override
  Widget build(BuildContext context) {
    final dashboardProvider = context.watch<DashboardProvider>();
    final alertsProvider = context.watch<AlertsProvider>();
    final systemStatusProvider = context.watch<SystemStatusProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: () async {
          await Future.wait([
            dashboardProvider.fetchDashboardData(),
            alertsProvider.fetchAlerts(),
            systemStatusProvider.fetchSystemStatus(),
          ]);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Dashboard',
                          style: TextStyle(
                            color: isDark ? Colors.white : Colors.black87,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Welcome back!',
                          style: TextStyle(
                            color: isDark ? Colors.grey : Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                    IconButton(
                      icon: Icon(
                        Icons.refresh,
                        color: isDark ? Colors.white : Colors.black87,
                      ),
                      onPressed: () {
                        dashboardProvider.fetchDashboardData();
                        alertsProvider.fetchAlerts();
                        systemStatusProvider.fetchSystemStatus();
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 25),

                // System Status Card
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'System Status',
                          style: TextStyle(
                            color: isDark ? Colors.white : Colors.black87,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            _buildStatusIndicator(
                              systemStatusProvider.systemStatus?['status'] ?? 'unknown',
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                systemStatusProvider.systemStatus?['details'] ?? 'Checking system status...',
                                style: TextStyle(
                                  color: isDark ? Colors.white : Colors.black87,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Component Status',
                          style: TextStyle(
                            color: isDark ? Colors.white70 : Colors.black54,
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        ..._buildComponentStatus(context, {
                          'Database': systemStatusProvider.systemStatus?['components']?['database'] ?? 'unknown',
                          'Orchestrator': systemStatusProvider.systemStatus?['components']?['orchestrator'] ?? 'unknown',
                          'Network Traffic': systemStatusProvider.systemStatus?['components']?['network_traffic'] ?? 'unknown',
                          'Data Classification': systemStatusProvider.systemStatus?['components']?['data_classification'] ?? 'unknown',
                        }),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // System Metrics Grid
                Row(
                  children: [
                    _buildStatCard(
                      context,
                      'Data Classification',
                      (systemStatusProvider.systemStatus?['components']?['data_classification']?.toString() ?? 'UNKNOWN').toUpperCase(),
                      Icons.security,
                      (systemStatusProvider.systemStatus?['components']?['data_classification']?.toString().toLowerCase() ?? '') == 'ok' 
                          ? Colors.green 
                          : Colors.orange,
                    ),
                    const SizedBox(width: 16),
                    _buildStatCard(
                      context,
                      'Database',
                      (systemStatusProvider.systemStatus?['components']?['database']?.toString() ?? 'UNKNOWN').toUpperCase(),
                      Icons.storage,
                      (systemStatusProvider.systemStatus?['components']?['database']?.toString().toLowerCase() ?? '') == 'ok' 
                          ? Colors.green 
                          : Colors.red,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _buildStatCard(
                      context,
                      'Orchestrator',
                      (systemStatusProvider.systemStatus?['components']?['orchestrator']?.toString() ?? 'UNKNOWN').toUpperCase(),
                      Icons.sync,
                      (systemStatusProvider.systemStatus?['components']?['orchestrator']?.toString().toLowerCase() ?? '') == 'loaded' 
                          ? Colors.blue 
                          : Colors.red,
                    ),
                    const SizedBox(width: 16),
                    _buildStatCard(
                      context,
                      'Network',
                      (systemStatusProvider.systemStatus?['components']?['network_traffic']?.toString() ?? 'UNKNOWN').toUpperCase(),
                      Icons.network_check,
                      (systemStatusProvider.systemStatus?['components']?['network_traffic']?.toString().toLowerCase() ?? '') == 'ok' 
                          ? Colors.teal 
                          : Colors.orange,
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Recent Alerts
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Recent Alerts',
                      style: TextStyle(
                        color: isDark ? Colors.white : Colors.black87,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    TextButton(
                      onPressed: () {
                        // Navigate to alerts screen
                      },
                      child: const Text(
                        'View All',
                        style: TextStyle(color: Colors.blue),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                ...alertsProvider.alerts.take(3).map((alert) => _buildAlertItem(context, alert)).toList(),
                if (alertsProvider.alerts.isEmpty)
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        'No recent alerts',
                        style: TextStyle(
                          color: isDark ? Colors.grey : Colors.grey[600],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAlertItem(BuildContext context, Alert alert) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final severityStr = alert.severity.toString().split('.').last;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: _getSeverityColor(severityStr).withOpacity(0.5),
          width: 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: _getSeverityColor(severityStr).withOpacity(0.2),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _getSeverityIcon(severityStr),
                color: _getSeverityColor(severityStr),
                size: 20,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    alert.title,
                    style: TextStyle(
                      color: isDark ? Colors.white : Colors.black87,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    alert.description ?? 'No description',
                    style: TextStyle(
                      color: isDark ? Colors.grey[400] : Colors.grey[600],
                      fontSize: 14,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _formatTimeAgo(alert.timestamp),
                    style: TextStyle(
                      color: isDark ? Colors.grey[600] : Colors.grey[500],
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            IconButton(
              icon: Icon(
                Icons.chevron_right,
                color: isDark ? Colors.grey : Colors.grey[600],
              ),
              onPressed: () {
                // Handle alert tap
              },
            ),
          ],
        ),
      ),
    );
  }

  String _formatTimeAgo(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      final minutes = difference.inMinutes;
      return '$minutes ${minutes == 1 ? 'minute' : 'minutes'} ago';
    } else if (difference.inDays < 1) {
      final hours = difference.inHours;
      return '$hours ${hours == 1 ? 'hour' : 'hours'} ago';
    } else if (difference.inDays < 7) {
      final days = difference.inDays;
      return '$days ${days == 1 ? 'day' : 'days'} ago';
    } else {
      return DateFormat('MMM d, y').format(dateTime);
    }
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Colors.red;
      case 'high':
        return Colors.orange;
      case 'medium':
        return Colors.yellow;
      case 'low':
      default:
        return Colors.blue;
    }
  }

  IconData _getSeverityIcon(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Icons.error;
      case 'high':
        return Icons.warning_amber_rounded;
      case 'medium':
        return Icons.warning_amber_outlined;
      case 'low':
      default:
        return Icons.info_outline;
    }
  }
}