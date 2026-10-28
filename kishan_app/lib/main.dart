import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const KishanApp());
}

class KishanApp extends StatelessWidget {
  const KishanApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'কৃষাণ - বাজারদর ও কৃষি আবহাওয়া',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.system,
      // লাইট মোড থিম
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        primaryColor: const Color(0xFF1B5E20),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1B5E20),
          brightness: Brightness.light,
          primary: const Color(0xFF1B5E20),
          secondary: const Color(0xFFF57F17),
        ),
        scaffoldBackgroundColor: const Color(0xFFF1F8E9),
        cardTheme: const CardTheme(color: Colors.white),
        textTheme: GoogleFonts.hindSiliguriTextTheme(
          Theme.of(context).textTheme,
        ),
      ),
      // ডার্ক মোড থিম
      darkTheme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF2E7D32),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D32),
          brightness: Brightness.dark,
          primary: const Color(0xFF388E3C),
          secondary: const Color(0xFFFFB74D),
          background: const Color(0xFF0D140E),
          surface: const Color(0xFF152017),
        ),
        scaffoldBackgroundColor: const Color(0xFF0D140E),
        cardTheme: const CardTheme(color: Color(0xFF152017)),
        textTheme: GoogleFonts.hindSiliguriTextTheme(
          ThemeData.dark().textTheme,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
