import 'package:flutter/foundation.dart';

class ScanResult {
  final String id;
  final bool isThreat;
  final String? threatType;
  final String? threatDetails;
  final double threatScore;
  final String scannedContentPreview;
  final String scanType;
  final List<String> recommendedActions;
  final Map<String, dynamic>? rawAnalysis;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  ScanResult({
    required this.id,
    required this.isThreat,
    this.threatType,
    this.threatDetails,
    required this.threatScore,
    required this.scannedContentPreview,
    required this.scanType,
    this.recommendedActions = const [],
    this.rawAnalysis,
    this.metadata,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    return ScanResult(
      id: json['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      isThreat: json['isThreat'] ?? false,
      threatType: json['threatType'],
      threatDetails: json['threatDetails'],
      threatScore: (json['threatScore'] ?? 0).toDouble(),
      scannedContentPreview: json['scannedContentPreview'] ?? '',
      scanType: json['scanType'] ?? 'text',
      metadata: json['metadata'] != null
          ? Map<String, dynamic>.from(json['metadata'])
          : null,
      recommendedActions: json['recommendedActions'] != null
          ? List<String>.from(json['recommendedActions'])
          : [],
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'isThreat': isThreat,
      if (threatType != null) 'threatType': threatType,
      if (threatDetails != null) 'threatDetails': threatDetails,
      if (threatScore != null) 'threatScore': threatScore,
      'timestamp': timestamp.toIso8601String(),
      if (metadata != null) 'metadata': metadata,
      if (recommendedActions != null) 'recommendedActions': recommendedActions,
      if (scannedContentPreview != null) 'scannedContentPreview': scannedContentPreview,
      'scanType': scanType,
    };
  }

  ScanResult copyWith({
    String? id,
    bool? isThreat,
    String? threatType,
    String? threatDetails,
    double? threatScore,
    DateTime? timestamp,
    Map<String, dynamic>? metadata,
    List<String>? recommendedActions,
    String? scannedContentPreview,
    String? scanType,
  }) {
    return ScanResult(
      id: id ?? this.id,
      isThreat: isThreat ?? this.isThreat,
      threatType: threatType ?? this.threatType,
      threatDetails: threatDetails ?? this.threatDetails,
      threatScore: threatScore ?? this.threatScore,
      timestamp: timestamp ?? this.timestamp,
      metadata: metadata ?? this.metadata,
      recommendedActions: recommendedActions ?? this.recommendedActions,
      scannedContentPreview: scannedContentPreview ?? this.scannedContentPreview,
      scanType: scanType ?? this.scanType,
    );
  }

  @override
  String toString() {
    return 'ScanResult(id: $id, isThreat: $isThreat, threatType: $threatType, timestamp: $timestamp)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ScanResult &&
        other.id == id &&
        other.isThreat == isThreat &&
        other.threatType == threatType &&
        other.threatScore == threatScore &&
        other.timestamp == timestamp;
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      isThreat,
      threatType,
      threatScore,
      timestamp,
    );
  }
}
