
enum AlertStatus {
  open,
  in_progress,
  resolved,
  dismissed,
}

enum AlertSeverity {
  critical,
  high,
  medium,
  low,
}

enum AlertType {
  threat_detected,
  system_issue,
  security_alert,
  performance_issue,
  configuration_change,
}

class Alert {
  final String id;
  final String title;
  final String description;
  final AlertSeverity severity;
  final AlertType type;
  final AlertStatus status;
  final String source;
  final DateTime timestamp;
  final DateTime? resolvedAt;
  bool isRead;
  final Map<String, dynamic> details;

  Alert({
    required this.id,
    required this.title,
    required this.description,
    required this.severity,
    required this.type,
    required this.status,
    required this.source,
    required this.timestamp,
    this.resolvedAt,
    this.isRead = false,
    required this.details,
  });

  factory Alert.fromFirestore(Map<String, dynamic> data, String id) {
    return Alert(
      id: id,
      title: data['title'] ?? 'No Title',
      description: data['description'] ?? 'No Description',
      severity: _parseSeverity(data['severity'] ?? 'low'),
      type: _parseType(data['type'] ?? 'system_issue'),
      status: _parseStatus(data['status'] ?? 'open'),
      source: data['source'] ?? 'Unknown Source',
      timestamp: data['timestamp'] != null 
          ? DateTime.parse(data['timestamp'].toString())
          : DateTime.now(),
      resolvedAt: data['resolved_at'] != null
          ? DateTime.parse(data['resolved_at'].toString())
          : null,
      isRead: data['is_read'] ?? false,
      details: Map<String, dynamic>.from(data['details'] ?? {}),
    );
  }

  factory Alert.fromJson(Map<String, dynamic> json) {
    return Alert(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? 'No Title',
      description: json['description'] ?? 'No Description',
      severity: _parseSeverity(json['severity'] ?? 'low'),
      type: _parseType(json['type'] ?? 'system_issue'),
      status: _parseStatus(json['status'] ?? 'open'),
      source: json['source'] ?? 'Unknown Source',
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      resolvedAt: json['resolved_at'] != null
          ? DateTime.parse(json['resolved_at'])
          : null,
      isRead: json['is_read'] ?? false,
      details: Map<String, dynamic>.from(json['details'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'severity': severity.toString().split('.').last,
      'type': type.toString().split('.').last,
      'status': status.toString().split('.').last,
      'source': source,
      'timestamp': timestamp.toIso8601String(),
      'resolved_at': resolvedAt?.toIso8601String(),
      'is_read': isRead,
      'details': details,
    };
  }

  Alert copyWith({
    String? id,
    String? title,
    String? description,
    AlertSeverity? severity,
    AlertType? type,
    AlertStatus? status,
    String? source,
    DateTime? timestamp,
    DateTime? resolvedAt,
    bool? isRead,
    Map<String, dynamic>? details,
  }) {
    return Alert(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      severity: severity ?? this.severity,
      type: type ?? this.type,
      status: status ?? this.status,
      source: source ?? this.source,
      timestamp: timestamp ?? this.timestamp,
      resolvedAt: resolvedAt ?? this.resolvedAt,
      isRead: isRead ?? this.isRead,
      details: details ?? this.details,
    );
  }

  static AlertSeverity _parseSeverity(String severity) {
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

  static AlertType _parseType(String type) {
    switch (type.toLowerCase()) {
      case 'threat_detected':
        return AlertType.threat_detected;
      case 'system_issue':
        return AlertType.system_issue;
      case 'security_alert':
        return AlertType.security_alert;
      case 'performance_issue':
        return AlertType.performance_issue;
      case 'configuration_change':
        return AlertType.configuration_change;
      default:
        return AlertType.system_issue;
    }
  }

  static AlertStatus _parseStatus(String status) {
    switch (status.toLowerCase()) {
      case 'open':
        return AlertStatus.open;
      case 'in_progress':
        return AlertStatus.in_progress;
      case 'resolved':
        return AlertStatus.resolved;
      case 'dismissed':
        return AlertStatus.dismissed;
      default:
        return AlertStatus.open;
    }
  }
}
