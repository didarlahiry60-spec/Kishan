import 'package:flutter/material.dart';
import '../models/farmer_profile.dart';
import '../services/api_service.dart';
import 'bazar_screen.dart';
import 'weather_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  String currentDistrict = 'বগুড়া';
  List<String> currentCrops = ['ধান', 'আলু', 'পেঁয়াজ'];
  FarmerProfile? profile;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final p = await ApiService.fetchProfile('flutter-demo-farmer-01');
      setState(() {
        profile = p;
        currentDistrict = p.district;
        currentCrops = p.favoriteCrops;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        profile = FarmerProfile(
          deviceId: 'flutter-demo-farmer-01',
          name: 'করিম মিয়া',
          district: 'বগুড়া',
          upazila: 'শিবগঞ্জ',
          favoriteCrops: ['ধান', 'আলু'],
          smsAlertsEnabled: true,
        );
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: Color(0xFF1B5E20))),
      );
    }

    final screens = [
      BazarScreen(district: currentDistrict),
      WeatherScreen(district: currentDistrict, crops: currentCrops),
      ProfileScreen(
        profile: profile!,
        onProfileUpdated: (updated) {
          setState(() {
            profile = updated;
            currentDistrict = updated.district;
            currentCrops = updated.favoriteCrops;
          });
        },
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Text('🌾 কৃষাণ', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                '📍 $currentDistrict',
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
        backgroundColor: const Color(0xFF1B5E20),
        foregroundColor: Colors.white,
      ),
      body: screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        selectedItemColor: const Color(0xFF1B5E20),
        unselectedItemColor: Colors.grey.shade600,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.sell), label: 'বাজারদর'),
          BottomNavigationBarItem(icon: Icon(Icons.wb_sunny), label: 'আবহাওয়া'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'আমার খামার'),
        ],
      ),
    );
  }
}
