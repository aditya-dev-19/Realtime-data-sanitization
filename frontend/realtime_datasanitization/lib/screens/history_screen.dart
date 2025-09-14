import 'package:flutter/material.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Map<String, String>> historyItems = [
      {
        "file": "final_report_q3_2025.docx",
        "status": "No Threats",
        "statusColor": "green",
        "date": "Sep 1"
      },
      {
        "file": "My credit card is 4111-XXXX-XXXX-1234, please...",
        "status": "PII Found",
        "statusColor": "orange",
        "date": "Aug 31"
      },
      {
        "file": "Click this link for a free prize: http://shady.link/giveaway",
        "status": "Malicious Detected",
        "statusColor": "red",
        "date": "Aug 29"
      },
      {
        "file": "project_alpha_source_code.zip",
        "status": "No Threats",
        "statusColor": "green",
        "date": "Aug 27"
      },
      {
        "file": "Meeting notes from our sync yesterday about the launch...",
        "status": "No Threats",
        "statusColor": "green",
        "date": "Aug 22"
      },
      {
        "file": "urgent_invoice_payment.pdf",
        "status": "Malicious Detected",
        "statusColor": "red",
        "date": "Aug 20"
      },
    ];

    return Scaffold(
      backgroundColor: const Color(0xFF0A1B2E), // Dark blue background like dashboard
      appBar: AppBar(
        backgroundColor: const Color(0xFF0A1B2E),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          "History",
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white, // same as Dashboard headline
          ),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // 🔍 Search bar
            TextField(
              decoration: InputDecoration(
                hintText: "Search scans...",
                hintStyle: const TextStyle(color: Colors.white70),
                prefixIcon: const Icon(Icons.search, color: Colors.white70),
                filled: true,
                fillColor: const Color(0xFF112A45),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              style: const TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 16),

            // 📂 History list
            Expanded(
              child: ListView.builder(
                itemCount: historyItems.length,
                itemBuilder: (context, index) {
                  final item = historyItems[index];
                  Color statusColor;
                  switch (item["statusColor"]) {
                    case "green":
                      statusColor = Colors.green;
                      break;
                    case "orange":
                      statusColor = Colors.orange;
                      break;
                    case "red":
                      statusColor = Colors.red;
                      break;
                    default:
                      statusColor = Colors.white;
                  }

                  return Card(
                    color: const Color(0xFF112A45), // Matches dashboard cards
                    margin: const EdgeInsets.only(bottom: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ListTile(
                      leading: Icon(
                        Icons.insert_drive_file,
                        color: Colors.blue[300],
                        size: 32,
                      ),
                      title: Text(
                        item["file"]!,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w500,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      subtitle: Text(
                        item["status"]!,
                        style: TextStyle(
                          color: statusColor,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      trailing: Text(
                        item["date"]!,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                        ),
                      ),
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
