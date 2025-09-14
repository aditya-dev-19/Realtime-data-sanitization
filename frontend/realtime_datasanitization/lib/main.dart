import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/material.dart' show CardThemeData;

// Providers
import 'providers/threat_provider.dart';
import 'providers/system_status_provider.dart';
import 'providers/dashboard_provider.dart';
import 'providers/alerts_provider.dart';

// Screens
import 'screens/dashboard_screen.dart';
import 'screens/threat_detection_screen.dart';
import 'screens/alerts_page.dart';
import 'screens/settings_screen.dart';

// Services
import 'services/api_service.dart';

// Initialize environment variables
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Load environment variables
  try {
    await dotenv.load(fileName: ".env");
  } catch (e) {
    debugPrint('Error loading .env file: $e');
  }
  
  runApp(
    MultiProvider(
      providers: [
        // Core providers
        ChangeNotifierProvider(create: (_) => SystemStatusProvider()),
        ChangeNotifierProvider(create: (_) => DashboardProvider()),
        ChangeNotifierProvider(create: (_) => AlertsProvider()),
        ChangeNotifierProvider(create: (_) => ThreatProvider()),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  int _currentIndex = 0;
  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    
    // Initialize screens
    _screens = [
      const DashboardScreen(),
      const ThreatDetectionScreen(),
      const AlertsScreen(),
      const SettingsScreen(),
    ];
    
    // Initial data loading
    _loadInitialData();
  }
  
  Future<void> _loadInitialData() async {
    // Schedule the data loading to happen after the first frame
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      // Load initial data in parallel
      await Future.wait([
        context.read<SystemStatusProvider>().fetchSystemStatus(),
        context.read<DashboardProvider>().fetchDashboardData(),
        context.read<AlertsProvider>().fetchAlerts(),
      ]);
    });
  }

  // Build the bottom navigation bar
  Widget _buildBottomNavBar() {
    return BottomNavigationBar(
      currentIndex: _currentIndex,
      onTap: (index) {
        setState(() {
          _currentIndex = index;
        });
      },
      items: [
        const BottomNavigationBarItem(
          icon: Icon(Icons.dashboard),
          label: 'Dashboard',
        ),
        const BottomNavigationBarItem(
          icon: Icon(Icons.security),
          label: 'Scan',
        ),
        BottomNavigationBarItem(
          icon: Consumer<AlertsProvider>(
            builder: (context, alertsProvider, _) {
              final unreadCount = alertsProvider.unreadCount;
              return Stack(
                children: [
                  const Icon(Icons.notifications),
                  if (unreadCount > 0)
                    Positioned(
                      right: 0,
                      child: Container(
                        padding: const EdgeInsets.all(2),
                        decoration: const BoxDecoration(
                          color: Colors.red,
                          shape: BoxShape.circle,
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 16,
                          minHeight: 16,
                        ),
                        child: Text(
                          unreadCount > 9 ? '9+' : '$unreadCount',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                ],
              );
            },
          ),
          label: 'Alerts',
        ),
        const BottomNavigationBarItem(
          icon: Icon(Icons.settings),
          label: 'Settings',
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Cybersecurity',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0A1A2F),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0A1A2F),
          elevation: 0,
          centerTitle: true,
          titleTextStyle: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Color(0xFF0F2A48),
          selectedItemColor: Colors.blue,
          unselectedItemColor: Colors.grey,
          type: BottomNavigationBarType.fixed,
        ),
        cardTheme: CardThemeData(
          color: const Color(0xFF1E2C42),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 2,
        ),
      ),
      home: Scaffold(
        body: _screens[_currentIndex],
        bottomNavigationBar: _buildBottomNavBar(),
      ),
    );
  }
}
