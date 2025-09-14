import 'package:flutter/foundation.dart';

class Alert {
  final String id;
  final String title;
  final String message;
  final DateTime timestamp;
  final String severity; // 'high', 'medium', 'low'
  final bool read;

  Alert({
    required this.id,
    required this.title,
    required this.message,
    required this.timestamp,
    this.severity = 'medium',
    this.read = false,
  });

  factory Alert.fromJson(Map<String, dynamic> json) {
    return Alert(
      id: json['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      title: json['title'] ?? 'New Alert',
      message: json['message'] ?? '',
      timestamp: json['timestamp'] != null 
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      severity: json['severity']?.toLowerCase() ?? 'medium',
      read: json['read'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'message': message,
      'timestamp': timestamp.toIso8601String(),
      'severity': severity,
      'read': read,
    };
  }

  Alert copyWith({
    String? id,
    String? title,
    String? message,
    DateTime? timestamp,
    String? severity,
    bool? read,
  }) {
    return Alert(
      id: id ?? this.id,
      title: title ?? this.title,
      message: message ?? this.message,
      timestamp: timestamp ?? this.timestamp,
      severity: severity ?? this.severity,
      read: read ?? this.read,
    );
  }

  @override
  String toString() {
    return 'Alert(id: $id, title: $title, severity: $severity, read: $read)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Alert &&
        other.id == id &&
        other.title == title &&
        other.message == message &&
        other.timestamp == timestamp &&
        other.severity == severity &&
        other.read == read;
  }

  @override
  int get hashCode {
    return id.hashCode ^
        title.hashCode ^
        message.hashCode ^
        timestamp.hashCode ^
        severity.hashCode ^
        read.hashCode;
  }
}
