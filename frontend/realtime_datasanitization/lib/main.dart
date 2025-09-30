import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

// Providers
import 'providers/threat_provider.dart';
import 'providers/system_status_provider.dart';
import 'providers/dashboard_provider.dart';
import 'providers/alerts_provider.dart';
import 'providers/auth_provider.dart';
import 'providers/theme_provider.dart'; 

// Screens
import 'screens/dashboard_screen.dart';
import 'screens/threat_detection_screen.dart';
import 'screens/alerts_page.dart';
import 'screens/settings_screen.dart';
import 'screens/login_screen.dart';
import 'screens/registration_screen.dart';

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
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => SystemStatusProvider()),
        ChangeNotifierProvider(create: (_) => DashboardProvider()),
        ChangeNotifierProvider(create: (_) => AlertsProvider()),
        ChangeNotifierProvider(create: (_) => ThreatProvider()),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // final themeProvider = Provider.of<ThemeProvider>(context);
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return MaterialApp(
          title: 'AI Cybersecurity',
          debugShowCheckedModeBanner: false,
          themeMode: themeProvider.themeMode,
          // 5. Define the light theme
          theme: ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.light(
              primary: Colors.blue,
              background: const Color(0xFFF0F2F5),
              surface: Colors.white,
            ),
            scaffoldBackgroundColor: const Color(0xFFF0F2F5),
            appBarTheme: const AppBarTheme(
              backgroundColor: Colors.white,
              elevation: 1,
              centerTitle: true,
              titleTextStyle: TextStyle(
                color: Colors.black,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            cardTheme: CardThemeData(
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              elevation: 2,
            ),
            bottomNavigationBarTheme: const BottomNavigationBarThemeData(
              backgroundColor: Colors.white,
              selectedItemColor: Colors.blue,
              unselectedItemColor: Colors.grey,
              type: BottomNavigationBarType.fixed,
            ),
          ),
          darkTheme: ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.dark(
              primary: Colors.blue,
              background: const Color(0xFF0A1A2F),
              surface: const Color(0xFF1E1E2E),
            ),
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
            cardTheme: CardThemeData(
              color: const Color(0xFF1E2C42),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              elevation: 2,
            ),
            bottomNavigationBarTheme: const BottomNavigationBarThemeData(
              backgroundColor: Color(0xFF0F2A48),
              selectedItemColor: Colors.blue,
              unselectedItemColor: Colors.grey,
              type: BottomNavigationBarType.fixed,
            ),
          ),
          home: const AuthWrapper(),
          routes: {
            '/home': (context) => const MyAppContent(),
            '/login': (context) => const LoginScreen(),
            '/register': (context) => const RegistrationScreen(),
          },
        );
      }
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    
    // Show loading indicator while checking auth state
    if (authProvider.isLoading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    // Show login screen if not authenticated, otherwise show main app
    return authProvider.isAuthenticated ? const MyAppContent() : const LoginScreen();
  }
}

class MyAppContent extends StatefulWidget {
  const MyAppContent({super.key});

  @override
  State<MyAppContent> createState() => _MyAppContentState();
}

class _MyAppContentState extends State<MyAppContent> {
  int _currentIndex = 0;
  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    
    // Initialize screens
    _screens = [
      const DashboardScreen(),
      const ThreatDetectionScreen(),
      const AlertsPage(),
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
        // If alerts tab was tapped, refresh alerts
        if (index == 2 && _currentIndex != 2) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            context.read<AlertsProvider>().fetchAlerts(forceRefresh: true);
          });
        }
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
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: _buildBottomNavBar(),
    );
  }
}
