import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:timeago/timeago.dart' as timeago;

import '../providers/alerts_provider.dart';
import '../models/alert.dart';

// Main page widget that displays the list of alerts and filtering options
class AlertsPage extends StatefulWidget {
  const AlertsPage({super.key});

  @override
  State<AlertsPage> createState() => _AlertsPageState();
}

class _AlertsPageState extends State<AlertsPage> {
  String _selectedSeverity = 'All';

  @override
  void initState() {
    super.initState();
    // Fetch alerts when the page is first loaded
    Future.microtask(() => Provider.of<AlertsProvider>(context, listen: false).fetchAlerts());
  }

  // Helper function to get a color based on severity
  Color _getSeverityColor(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.critical:
        return Colors.red[800]!;
      case AlertSeverity.high:
        return Colors.orange[700]!;
      case AlertSeverity.medium:
        return Colors.amber[600]!;
      case AlertSeverity.low:
        return Colors.blue[600]!;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final alertsProvider = Provider.of<AlertsProvider>(context);

    final filteredAlerts = alertsProvider.alerts.where((alert) {
      if (_selectedSeverity == 'All') {
        return true;
      }
      return alert.severity.toString().split('.').last.toLowerCase() == _selectedSeverity.toLowerCase();
    }).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Security Alerts'),
        actions: [
          // Refresh button
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => alertsProvider.fetchAlerts(),
          ),
        ],
      ),
      body: Column(
        children: [
          _buildFilterChips(),
          Expanded(
            child: alertsProvider.isLoading
                ? const Center(child: CircularProgressIndicator())
                : filteredAlerts.isEmpty
                    ? const Center(child: Text('No alerts found.'))
                    : ListView.builder(
                        itemCount: filteredAlerts.length,
                        itemBuilder: (ctx, i) => AlertListItem(
                          alert: filteredAlerts[i],
                          severityColor: _getSeverityColor(filteredAlerts[i].severity),
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  // Helper method to parse selected severity string to AlertSeverity enum
  AlertSeverity _parseSelectedSeverity(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return AlertSeverity.critical;
      case 'high':
        return AlertSeverity.high;
      case 'medium':
        return AlertSeverity.medium;
      case 'low':
      default:
        return AlertSeverity.low;
    }
  }

  // Builds the filter chips for alert severity
  Widget _buildFilterChips() {
    final severities = ['All', 'Low', 'Medium', 'High', 'Critical'];
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0),
      child: Wrap(
        spacing: 8.0,
        children: severities.map((severity) {
          return ChoiceChip(
            label: Text(severity),
            selected: _selectedSeverity == severity,
            onSelected: (isSelected) {
              if (isSelected) {
                setState(() {
                  _selectedSeverity = severity;
                });
              }
            },
            selectedColor: severity == 'All' ? Colors.blue.withOpacity(0.3) : _getSeverityColor(_parseSelectedSeverity(severity)).withOpacity(0.3),
          );
        }).toList(),
      ),
    );
  }
}

// Widget for a single item in the alerts list
class AlertListItem extends StatelessWidget {
  final Alert alert;
  final Color severityColor;

  const AlertListItem({
    super.key,
    required this.alert,
    required this.severityColor,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      elevation: 2,
      child: InkWell(
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => AlertDetailsPage(alert: alert),
            ),
          );
        },
        child: Row(
          children: [
            // Severity indicator bar
            Container(
              width: 5,
              height: 80,
              color: severityColor,
            ),
            Expanded(
              child: ListTile(
                title: Text(
                  alert.title,
                  style: TextStyle(
                    fontWeight: alert.isRead ? FontWeight.normal : FontWeight.bold,
                  ),
                ),
                subtitle: Text('${alert.source} • ${timeago.format(alert.timestamp)}'),
                trailing: const Icon(Icons.chevron_right),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Page to show the full details of a selected alert
class AlertDetailsPage extends StatelessWidget {
  final Alert alert;

  const AlertDetailsPage({super.key, required this.alert});

  // Helper function to get a color based on severity
  Color _getSeverityColor(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.critical: return Colors.red[800]!;
      case AlertSeverity.high: return Colors.orange[700]!;
      case AlertSeverity.medium: return Colors.amber[600]!;
      case AlertSeverity.low: return Colors.blue[600]!;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(alert.title),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDetailItem('Severity', alert.severity.toString().split('.').last.toUpperCase(), 
              valueColor: _getSeverityColor(alert.severity)),
            _buildDetailItem('Timestamp', 
              DateFormat.yMMMd().add_jms().format(alert.timestamp)),
            _buildDetailItem('Source', alert.source),
            _buildDetailItem('Description', alert.description),
            const Divider(height: 32),
            Text(
              'Technical Details',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            // Dynamically build the details view based on the alert 'type'
            _buildDetailsView(alert.details),
          ],
        ),
      ),
    );
  }

  // Builds a consistent key-value display for detail items
  Widget _buildDetailItem(String title, String value, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.grey),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(fontSize: 16, color: valueColor),
          ),
        ],
      ),
    );
  }

  // Renders the specific details based on the alert type from the backend
  Widget _buildDetailsView(Map<String, dynamic> details) {
    final type = details['type'];
    final recommendation = details['recommendation'] as String?;

    List<Widget> detailWidgets = [];

    // Add specific details based on type
    switch (type) {
      case 'phishing':
        detailWidgets.add(_buildDetailItem('Confidence', '${(details['confidence'] * 100).toStringAsFixed(2)}%'));
        detailWidgets.add(_buildDetailItem('Text Analyzed', details['text_analyzed']));
        break;
      case 'code_injection':
        detailWidgets.add(_buildDetailItem('Threat Score', details['score'].toString()));
        detailWidgets.add(_buildDetailItem('Vulnerable String', details['vulnerable_string']));
        break;
      case 'malicious_file':
        detailWidgets.add(_buildDetailItem('File Name', details['file_name']));
        detailWidgets.add(_buildDetailItem('Threat Type', details['threat_type']));
        break;
      case 'network_anomaly':
        detailWidgets.add(_buildDetailItem('Reason', details['reason']));
        break;
      case 'sensitive_data':
         detailWidgets.add(_buildDetailItem('Data Types Found', (details['data_types_found'] as List).join(', ')));
        break;
      default:
        // Fallback for any other type
        details.forEach((key, value) {
          if (key != 'type' && key != 'recommendation') {
            detailWidgets.add(_buildDetailItem(key, value.toString()));
          }
        });
    }

    // Add recommendation card if it exists
    if (recommendation != null) {
      detailWidgets.add(
        Card(
          color: Colors.blueGrey[800],
          margin: const EdgeInsets.only(top: 16),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Recommendation', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 8),
                Text(recommendation),
              ],
            ),
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: detailWidgets,
    );
  }
}