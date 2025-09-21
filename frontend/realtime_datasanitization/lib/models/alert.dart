class Alert {
  final String id;
  final String title;
  final String description;
  final String severity;
  final String source;
  final DateTime timestamp;
  bool isRead;
  final Map<String, dynamic> details; // 👈 Add this field

  Alert({
    required this.id,
    required this.title,
    required this.description,
    required this.severity,
    required this.source,
    required this.timestamp,
    this.isRead = false,
    required this.details, // 👈 Add to constructor
  });

  factory Alert.fromFirestore(Map<String, dynamic> data, String id) {
    return Alert(
      id: id,
      title: data['title'] ?? 'No Title',
      description: data['description'] ?? 'No Description',
      severity: data['severity'] ?? 'Unknown',
      source: data['source'] ?? 'Unknown Source',
      timestamp: (data['timestamp'] as Timestamp).toDate(),
      isRead: data['is_read'] ?? false,
      details: Map<String, dynamic>.from(data['details'] ?? {}), // 👈 Deserialize the details
    );
  }
}