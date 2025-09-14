import 'package:flutter/foundation.dart';

enum AlertSeverity { low, medium, high, critical }
enum AlertStatus { open, in_progress, resolved, dismissed }
enum AlertType {
  threat_detected,
  system_issue,
  security_alert,
  performance_issue,
  configuration_change,
}

class Alert {
  final int id;
  final String title;
  final String? description;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final DateTime? resolvedAt;
  final AlertSeverity severity;
  final AlertStatus status;
  final AlertType type;
  final String? source;
  final Map<String, dynamic>? metadata;

  Alert({
    required this.id,
    required this.title,
    this.description,
    DateTime? createdAt,
    this.updatedAt,
    this.resolvedAt,
    required this.severity,
    required this.status,
    required this.type,
    this.source,
    this.metadata,
  }) : createdAt = createdAt ?? DateTime.now();

  factory Alert.fromJson(Map<String, dynamic> json) {
    return Alert(
      id: json['id'] as int,
      title: json['title'] as String,
      description: json['description'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
      resolvedAt: json['resolved_at'] != null
          ? DateTime.parse(json['resolved_at'] as String)
          : null,
      severity: AlertSeverity.values.firstWhere(
        (e) => e.toString().split('.').last == json['severity'],
        orElse: () => AlertSeverity.medium,
      ),
      status: AlertStatus.values.firstWhere(
        (e) => e.toString().split('.').last == json['status'],
        orElse: () => AlertStatus.open,
      ),
      type: AlertType.values.firstWhere(
        (e) => e.toString().split('.').last == json['type'],
        orElse: () => AlertType.system_issue,
      ),
      source: json['source'] as String?,
      metadata: json['metadata'] != null
          ? Map<String, dynamic>.from(json['metadata'] as Map)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      if (description != null) 'description': description,
      'created_at': createdAt.toIso8601String(),
      if (updatedAt != null) 'updated_at': updatedAt!.toIso8601String(),
      if (resolvedAt != null) 'resolved_at': resolvedAt!.toIso8601String(),
      'severity': severity.toString().split('.').last,
      'status': status.toString().split('.').last,
      'type': type.toString().split('.').last,
      if (source != null) 'source': source,
      if (metadata != null) 'metadata': metadata,
    };
  }

  bool get isRead => status == AlertStatus.resolved || status == AlertStatus.dismissed;

  Alert copyWith({
    int? id,
    String? title,
    String? description,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? resolvedAt,
    AlertSeverity? severity,
    AlertStatus? status,
    AlertType? type,
    String? source,
    Map<String, dynamic>? metadata,
    bool? isRead,
  }) {
    return Alert(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      resolvedAt: resolvedAt ?? this.resolvedAt,
      severity: severity ?? this.severity,
      status: status ?? this.status,
      type: type ?? this.type,
      source: source ?? this.source,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  String toString() {
    return 'Alert(id: $id, title: $title, severity: $severity, status: $status, type: $type)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Alert &&
        other.id == id &&
        other.title == title &&
        other.description == description &&
        other.createdAt == createdAt &&
        other.severity == severity &&
        other.status == status;
  }

  @override
  int get hashCode {
    return id.hashCode ^
        title.hashCode ^
        (description?.hashCode ?? 0) ^
        createdAt.hashCode ^
        severity.hashCode ^
        status.hashCode;
  }
}
