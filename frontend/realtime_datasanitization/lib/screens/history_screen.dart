// frontend/realtime_datasanitization/lib/screens/file_history_screen.dart

import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
// ignore: depend_on_referenced_packages
import 'package:open_file/open_file.dart';
// ignore: depend_on_referenced_packages
import 'package:path_provider/path_provider.dart';
import 'dart:io';

import '../providers/threat_provider.dart';

class FileHistoryScreen extends StatefulWidget {
  const FileHistoryScreen({super.key});

  @override
  State<FileHistoryScreen> createState() => _FileHistoryScreenState();
}

class _FileHistoryScreenState extends State<FileHistoryScreen> {
  @override
  void initState() {
    super.initState();
    Provider.of<ThreatProvider>(context, listen: false).fetchFileHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('File History'),
      ),
      body: Consumer<ThreatProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.fileHistory.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.fileHistory.isEmpty) {
            return const Center(child: Text('No file history found.'));
          }

          return ListView.builder(
            itemCount: provider.fileHistory.length,
            itemBuilder: (context, index) {
              final file = provider.fileHistory[index];
              return ListTile(
                title: Text(file['original_filename']),
                subtitle: Text('ID: ${file['firestore_doc_id']}'),
                trailing: IconButton(
                  icon: const Icon(Icons.download),
                  onPressed: () async {
                    final downloadedBytes = await provider.downloadFile(file['firestore_doc_id']);
                    if (downloadedBytes != null) {
                      final tempDir = await getTemporaryDirectory();
                      final filePath = '${tempDir.path}/${file['original_filename']}';
                      final fileHandle = File(filePath);
                      await fileHandle.writeAsBytes(downloadedBytes);
                      OpenFile.open(filePath);
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Failed to download file.'),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  },
                ),
              );
            },
          );
        },
      ),
    );
  }
}