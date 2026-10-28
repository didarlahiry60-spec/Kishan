import 'package:flutter/material.dart';
import '../models/weather.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';

class WeatherScreen extends StatefulWidget {
  final String district;
  final List<String> crops;

  const WeatherScreen({Key? key, required this.district, required this.crops}) : super(key: key);

  @override
  State<WeatherScreen> createState() => _WeatherScreenState();
}

class _WeatherScreenState extends State<WeatherScreen> {
  Map<String, dynamic>? weatherData;
  AgroAdvisory? advisory;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadData();
  }

  @override
  void didUpdateWidget(covariant WeatherScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.district != widget.district) {
      loadData();
    }
  }

  Future<void> loadData() async {
    setState(() => isLoading = true);
    try {
      final wData = await ApiService.fetchWeatherForecast(widget.district);
      final adv = await ApiService.fetchAgroAdvisory(district: widget.district, crops: widget.crops);
      setState(() {
        weatherData = wData;
        advisory = adv;
        isLoading = false;
      });
    } catch (e) {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF1B5E20)));
    }

    final current = weatherData?['current'] ?? {};
    final daily = (weatherData?['daily_forecast'] as List<dynamic>?) ?? [];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // ওয়েদার হিরো কার্ড
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF2E7D32), Color(0xFF1B5E20)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [BoxShadow(color: Colors.green.shade900.withOpacity(0.3), blurRadius: 10)],
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(widget.district, style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 2),
                        Text(current['condition_bn'] ?? 'স্বাভাবিক', style: const TextStyle(color: Colors.white70, fontSize: 15)),
                      ],
                    ),
                    Text(
                      '${(current['temperature'] as num?)?.round() ?? 30}°C',
                      style: const TextStyle(color: Colors.white, fontSize: 40, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _statItem('🌧️', '${(daily.isNotEmpty ? daily[0]['precipitation_sum'] : 0)} মিমি', 'বৃষ্টিপাত'),
                    _statItem('💧', '${current['humidity'] ?? 75}%', 'আর্দ্রতা'),
                    _statItem('💨', '${(current['wind_speed'] as num?)?.round() ?? 10} কিমি/ঘ', 'বাতাস'),
                  ],
                ),
                const SizedBox(height: 14),
                ElevatedButton.icon(
                  onPressed: () {
                    if (advisory != null) {
                      final speech = advisory!.voiceScriptBn.isNotEmpty ? advisory!.voiceScriptBn : advisory!.headlineBn;
                      AudioService().speakBengali(speech);
                    }
                  },
                  icon: const Icon(Icons.volume_up, color: Colors.black87),
                  label: const Text('সম্পূর্ণ কৃষি পরামর্শ বাংলায় শুনুন', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.amber.shade600,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                    minimumSize: const Size.fromHeight(42),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // এআই এগ্রো-এডভাইজরি
          if (advisory != null)
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: Colors.blue.shade50, borderRadius: BorderRadius.circular(10)),
                      child: const Text('🤖 এআই কৃষি পরামর্শ (BRRI/BARI)', style: TextStyle(fontSize: 11, color: Colors.blue, fontWeight: FontWeight.bold)),
                    ),
                    const SizedBox(height: 6),
                    Text(advisory!.headlineBn, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.red)),
                    const Divider(height: 20),

                    // করণীয়
                    _advisoryBlock('✓ যা করবেন (করণীয়):', advisory!.dosBn, Colors.green),
                    const SizedBox(height: 10),

                    // বর্জনীয়
                    _advisoryBlock('✕ যা করবেন না (বর্জনীয়):', advisory!.dontsBn, Colors.red),
                    const SizedBox(height: 10),

                    // সেচ
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(color: Colors.blue.shade50, borderRadius: BorderRadius.circular(8)),
                      child: Row(
                        children: [
                          const Icon(Icons.water_drop, color: Colors.blue, size: 20),
                          const SizedBox(width: 8),
                          Expanded(child: Text(advisory!.irrigationAdviceBn, style: const TextStyle(fontSize: 13))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _statItem(String icon, String val, String lbl) {
    return Column(
      children: [
        Text(icon, style: const TextStyle(fontSize: 16)),
        const SizedBox(height: 2),
        Text(val, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
        Text(lbl, style: const TextStyle(color: Colors.white70, fontSize: 10)),
      ],
    );
  }

  Widget _advisoryBlock(String title, List<String> items, MaterialColor color) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(color: color.shade50, borderRadius: BorderRadius.circular(8), border: Border.all(color: color.shade200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: color.shade900)),
          const SizedBox(height: 4),
          ...items.map((it) => Padding(
                padding: const EdgeInsets.only(bottom: 3),
                child: Text('• $it', style: const TextStyle(fontSize: 12.5, height: 1.35)),
              )),
        ],
      ),
    );
  }
}
