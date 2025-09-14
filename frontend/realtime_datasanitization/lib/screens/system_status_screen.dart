import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/system_status_provider.dart';

class SystemStatusScreen extends StatefulWidget {
  const SystemStatusScreen({super.key});

  @override
  State<SystemStatusScreen> createState() => _SystemStatusScreenState();
}

class _SystemStatusScreenState extends State<SystemStatusScreen> {
  @override
  void initState() {
    super.initState();
    // Fetch system status when the screen loads
    Future.microtask(() => 
      context.read<SystemStatusProvider>().fetchSystemStatus()
    );
  }

  List<Widget> _buildServiceStatusList(Map<String, dynamic> statusData) {
    final services = <Widget>[];
    
    // Add API status
    services.add(_buildServiceCard(
      'API Service',
      statusData['status'] ?? 'unknown',
      statusData['message'] ?? 'No status message',
      Icons.api,
    ));
    
    // Add database status if available
    if (statusData['database'] != null) {
      services.add(const SizedBox(height: 12));
      services.add(_buildServiceCard(
        'Database',
        statusData['database']['status'] ?? 'unknown',
        statusData['database']['message'] ?? 'No status message',
        Icons.storage,
      ));
    }
    
    return services;
  }
  
  Widget _buildServiceCard(String title, String status, String message, IconData icon) {
    final statusColor = _getStatusColor(status);
    
    return Card(
      color: const Color(0xFF1E2C42),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: statusColor.withOpacity(0.3), width: 1),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: statusColor, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    message,
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                status.toUpperCase(),
                style: TextStyle(
                  color: statusColor,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'up':
      case 'ok':
        return Colors.green;
      case 'degraded':
      case 'warning':
        return Colors.orange;
      case 'unhealthy':
      case 'down':
      case 'error':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusProvider = context.watch<SystemStatusProvider>();

    return Scaffold(
      backgroundColor: const Color(0xFF0A1A2F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0A1A2F),
        elevation: 0,
        title: const Text(
          "System Status",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: statusProvider.isLoading 
                ? null 
                : () => statusProvider.fetchSystemStatus(),
          ),
          const SizedBox(width: 8),
        ],
      ),
        ],
      ),
      body: statusProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : statusProvider.error.isNotEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, color: Colors.red, size: 48),
                      const SizedBox(height: 16),
                      Text(
                        'Error: ${statusProvider.error}',
                        style: const TextStyle(color: Colors.white),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () => statusProvider.fetchSystemStatus(),
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
          : RefreshIndicator(
              onRefresh: () => statusProvider.fetchSystemStatus(),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Overall Status Card
                    Card(
                      color: const Color(0xFF162A45),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              "Overall Status",
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Container(
                                  width: 12,
                                  height: 12,
                                  decoration: BoxDecoration(
                                    color: statusProvider.systemStatus?['status'] == 'healthy' 
                                        ? Colors.green 
                                        : Colors.red,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  statusProvider.systemStatus?['status']?.toString().toUpperCase() ?? 'UNKNOWN',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const Spacer(),
                                Text(
                                  'Updated: ${DateTime.now().toString().substring(0, 16)}',
                                  style: TextStyle(
                                    color: Colors.grey[400],
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Services Status
                    const Text(
                      "Services",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    // List of services
                    ..._buildServiceStatusList(statusProvider.systemStatus ?? {}),
                    
                    // Additional information section
                    const SizedBox(height: 24),
                    const Text(
                      "Recent Activity",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Card(
                      color: const Color(0xFF1E2C42),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.history, color: Colors.blue, size: 20),
                                SizedBox(width: 8),
                                Text(
                                  "Last checked",
                                  style: TextStyle(color: Colors.white70, fontSize: 14),
                                ),
                                Spacer(),
                                Text(
                                  "Just now",
                                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                                ),
                              ],
                            ),
                            Divider(height: 24, color: Colors.white12),
                            Row(
                              children: [
                                Icon(Icons.update, color: Colors.blue, size: 20),
                                SizedBox(width: 8),
                                Text(
                                  "Uptime",
                                  style: TextStyle(color: Colors.white70, fontSize: 14),
                                ),
                                Spacer(),
                                Text(
                                  "99.9%",
                                  style: TextStyle(color: Colors.green, fontWeight: FontWeight.w500),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
                            Text(
                              model["status"] as String,
                              style: TextStyle(
                                color: model["color"] as Color,
                                fontWeight: FontWeight.w600,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
