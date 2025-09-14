import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/alerts_provider.dart';
import '../models/alert.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _selectedFilter = 'all';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    // Fetch alerts when the screen loads
    Future.microtask(() => 
      context.read<AlertsProvider>().fetchAlerts(forceRefresh: true)
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // Format timestamp to relative time (e.g., "2 minutes ago")
  String _formatTimeAgo(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays > 30) {
      return '${(difference.inDays / 30).floor()} months ago';
    } else if (difference.inDays > 7) {
      return '${(difference.inDays / 7).floor()} weeks ago';
    } else if (difference.inDays > 0) {
      return '${difference.inDays} days ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} hours ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} minutes ago';
    } else {
      return 'Just now';
    }
  }

  // Get color based on alert severity
  Color _getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return Colors.red[700]!;
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      case 'low':
      default:
        return Colors.blue;
    }
  }

  // Get icon based on alert type
  IconData _getAlertIcon(AlertType type) {
    final typeString = type.toString().split('.').last;
    switch (typeString) {
      case 'threat_detected':
        return Icons.security;
      case 'system_issue':
        return Icons.warning_amber_rounded;
      case 'security_alert':
        return Icons.notification_important;
      case 'performance_issue':
        return Icons.speed;
      case 'configuration_change':
        return Icons.settings;
      default:
        return Icons.notifications;
    }
  }

  // Get status text
  String _getStatusText(AlertStatus status) {
    return status.toString().split('.').last.replaceAll('_', ' ');
  }

  // Build alert item
  Widget _buildAlertItem(Alert alert, AlertsProvider provider) {
    final severityString = alert.severity.toString().split('.').last;
    return Card(
      margin: const EdgeInsets.only(bottom: 12.0),
      color: const Color(0xFF1E2C42),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.0),
        side: BorderSide(
          color: _getSeverityColor(severityString).withOpacity(0.5),
          width: 1.0,
        ),
      ),
      child: InkWell(
        onTap: () {
          // Mark as read on tap if unread
          if (!alert.isRead) {
            provider.markAsRead(alert.id);
          }
          // Show alert details
          _showAlertDetails(alert, provider);
        },
        borderRadius: BorderRadius.circular(12.0),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Alert Icon
              Container(
                padding: const EdgeInsets.all(8.0),
                decoration: BoxDecoration(
                  color: _getSeverityColor(alert.severity.toString().split('.').last).withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _getAlertIcon(alert.type),
                  color: _getSeverityColor(alert.severity.toString().split('.').last),
                  size: 20.0,
                ),
              ),
              const SizedBox(width: 16.0),
              // Alert Details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title and Status
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            alert.title,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16.0,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8.0,
                            vertical: 2.0,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.blueGrey[800],
                            borderRadius: BorderRadius.circular(12.0),
                          ),
                          child: Text(
                            _getStatusText(alert.status),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12.0,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4.0),
                    // Description
                    if (alert.description != null && alert.description!.isNotEmpty)
                      Text(
                        alert.description!,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 14.0,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    const SizedBox(height: 8.0),
                    // Timestamp and Actions
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          _formatTimeAgo(alert.createdAt),
                          style: TextStyle(
                            color: Colors.grey[400],
                            fontSize: 12.0,
                          ),
                        ),
                        // Action buttons
                        Row(
                          children: [
                            if (alert.status == AlertStatus.open)
                              IconButton(
                                icon: const Icon(Icons.check_circle_outline, size: 20.0),
                                color: Colors.green,
                                onPressed: () => provider.updateAlertStatus(
                                  alert.id,
                                  AlertStatus.resolved,
                                ),
                                padding: EdgeInsets.zero,
                                constraints: const BoxConstraints(),
                                tooltip: 'Mark as resolved',
                              ),
                            if (alert.status != AlertStatus.dismissed)
                              IconButton(
                                icon: const Icon(Icons.close, size: 20.0),
                                color: Colors.grey,
                                onPressed: () => provider.updateAlertStatus(
                                  alert.id,
                                  AlertStatus.dismissed,
                                ),
                                padding: EdgeInsets.zero,
                                constraints: const BoxConstraints(),
                                tooltip: 'Dismiss',
                              ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Show alert details dialog
  void _showAlertDetails(Alert alert, AlertsProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E2C42),
        title: Row(
          children: [
            Icon(
              _getAlertIcon(alert.type),
              color: _getSeverityColor(alert.severity.toString().split('.').last),
            ),
            const SizedBox(width: 12.0),
            Expanded(
              child: Text(
                alert.title,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Status and Timestamp
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8.0,
                      vertical: 4.0,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.blueGrey[800],
                      borderRadius: BorderRadius.circular(12.0),
                    ),
                    child: Text(
                      _getStatusText(alert.status),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12.0,
                      ),
                    ),
                  ),
                  Text(
                    '${DateFormat('MMM d, y').format(alert.createdAt)} • ${DateFormat('h:mm a').format(alert.createdAt)}',
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 12.0,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16.0),
              // Description
              if (alert.description != null && alert.description!.isNotEmpty)
                Text(
                  alert.description!,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 14.0,
                  ),
                ),
              const SizedBox(height: 16.0),
              // Metadata
              if (alert.metadata != null && alert.metadata!.isNotEmpty)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Details:',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14.0,
                      ),
                    ),
                    const SizedBox(height: 8.0),
                    Container(
                      padding: const EdgeInsets.all(12.0),
                      decoration: BoxDecoration(
                        color: Colors.black26,
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                      child: Text(
                        alert.metadata.toString(),
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12.0,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('CLOSE'),
          ),
          if (alert.status == AlertStatus.open)
            ElevatedButton(
              onPressed: () {
                provider.updateAlertStatus(alert.id, AlertStatus.resolved);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Alert marked as resolved')),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
              ),
              child: const Text('RESOLVE'),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final alertsProvider = context.watch<AlertsProvider>();
    
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        backgroundColor: const Color(0xFF0A1A2F),
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          title: const Text(
            "Alerts",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          centerTitle: true,
          iconTheme: const IconThemeData(color: Colors.white),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.blue,
            labelColor: Colors.blue,
            unselectedLabelColor: Colors.grey,
            tabs: const [
              Tab(text: 'All'),
              Tab(text: 'Unread'),
              Tab(text: 'Critical'),
            ],
          ),
          actions: [
            if (alertsProvider.unreadCount > 0)
              IconButton(
                icon: const Icon(Icons.checklist_rtl, color: Colors.white),
                onPressed: () {
                  alertsProvider.markAllAsRead();
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('All alerts marked as read')),
                  );
                },
                tooltip: 'Mark all as read',
              ),
          ],
        ),
        body: TabBarView(
          controller: _tabController,
          children: [
            // All Alerts Tab
            _buildAlertsList(
              alerts: alertsProvider.alerts,
              isLoading: alertsProvider.isLoading,
              error: alertsProvider.error,
              onRefresh: () => alertsProvider.fetchAlerts(forceRefresh: true),
            ),
            // Unread Alerts Tab
            _buildAlertsList(
              alerts: alertsProvider.alerts.where((a) => !a.isRead).toList(),
              isLoading: alertsProvider.isLoading,
              error: alertsProvider.error,
              onRefresh: () => alertsProvider.fetchAlerts(forceRefresh: true),
              emptyMessage: 'No unread alerts',
            ),
            // Critical Alerts Tab
            _buildAlertsList(
              alerts: alertsProvider.getCriticalAlerts(),
              isLoading: alertsProvider.isLoading,
              error: alertsProvider.error,
              onRefresh: () => alertsProvider.fetchAlerts(forceRefresh: true),
              emptyMessage: 'No critical alerts',
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildAlertsList({
    required List<Alert> alerts,
    required bool isLoading,
    required String error,
    required VoidCallback onRefresh,
    String emptyMessage = 'No alerts found',
  }) {
    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  "${alerts.length} ${alerts.length == 1 ? 'Alert' : 'Alerts'}",
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (alerts.isNotEmpty && alerts.any((a) => !a.isRead))
                  TextButton(
                    onPressed: () {
                      final provider = context.read<AlertsProvider>();
                      provider.markAllAsRead();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('All alerts marked as read')),
                      );
                    },
                    child: const Text(
                      'Mark all as read',
                      style: TextStyle(color: Colors.blue),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),

            if (isLoading && alerts.isEmpty)
              const Center(
                child: CircularProgressIndicator(),
              )
            else if (error.isNotEmpty)
              Center(
                child: Column(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red, size: 48),
                    const SizedBox(height: 16),
                    Text(
                      'Error loading alerts: $error',
                      style: const TextStyle(color: Colors.white),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => onRefresh(),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              )
            else if (alerts.isEmpty)
              Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.notifications_off, size: 64, color: Colors.grey),
                    const SizedBox(height: 16),
                    Text(
                      emptyMessage,
                      style: const TextStyle(color: Colors.grey, fontSize: 16),
                    ),
                  ],
                ),
              )
            else
              ...alerts.map((alert) => _buildAlertItem(alert, context.read<AlertsProvider>())),
          ],
        ),
      ),
    );
  }
}

