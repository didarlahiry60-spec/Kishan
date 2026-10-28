import 'package:flutter/material.dart';
import '../models/commodity.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../widgets/commodity_card.dart';

class BazarScreen extends StatefulWidget {
  final String district;

  const BazarScreen({Key? key, required this.district}) : super(key: key);

  @override
  State<BazarScreen> createState() => _BazarScreenState();
}

class _BazarScreenState extends State<BazarScreen> {
  String selectedCategory = 'সব';
  String searchQuery = '';
  List<Commodity> commodities = [];
  Map<String, dynamic>? summary;
  bool isLoading = true;

  final categories = ['সব', 'সবজি', 'চাল-ডাল', 'মসলা', 'তৈলবীজ', 'ফল'];

  @override
  void initState() {
    super.initState();
    loadData();
  }

  @override
  void didUpdateWidget(covariant BazarScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.district != widget.district) {
      loadData();
    }
  }

  Future<void> loadData() async {
    setState(() => isLoading = true);
    try {
      final items = await ApiService.fetchDailyPrices(
        district: widget.district,
        category: selectedCategory,
        search: searchQuery,
      );
      final sum = await ApiService.fetchMarketSummary(widget.district);
      setState(() {
        commodities = items;
        summary = sum;
        isLoading = false;
      });
    } catch (e) {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // বাজার সামারি কার্ড
        if (summary != null)
          Container(
            margin: const EdgeInsets.all(12),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border(left: BorderSide(color: Colors.orange.shade800, width: 4)),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('📢 আজকের বাজার বিশ্লেষণ', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    IconButton(
                      icon: const Icon(Icons.volume_up, size: 20, color: Color(0xFF1B5E20)),
                      onPressed: () {
                        final text = '${summary!['ai_summary']} ${summary!['bargaining_tip']}';
                        AudioService().speakBengali(text);
                      },
                    ),
                  ],
                ),
                Text(
                  summary!['ai_summary'] ?? 'বাজারদর লোড হচ্ছে...',
                  style: const TextStyle(fontSize: 13, height: 1.4),
                ),
              ],
            ),
          ),

        // সার্চ বার
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: TextField(
            onChanged: (val) {
              searchQuery = val;
              loadData();
            },
            decoration: InputDecoration(
              hintText: 'ফসলের নাম দিয়ে খুঁজুন (যেমন আলু, মরিচ)...',
              prefixIcon: const Icon(Icons.search),
              contentPadding: const EdgeInsets.symmetric(vertical: 10),
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(25), borderSide: BorderSide.none),
            ),
          ),
        ),

        // ক্যাটাগরি চিপস
        Container(
          height: 48,
          margin: const EdgeInsets.symmetric(vertical: 8),
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final cat = categories[index];
              final isSelected = cat == selectedCategory;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(cat),
                  selected: isSelected,
                  selectedColor: const Color(0xFF1B5E20),
                  labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.black87),
                  onSelected: (selected) {
                    if (selected) {
                      setState(() => selectedCategory = cat);
                      loadData();
                    }
                  },
                ),
              );
            },
          ),
        ),

        // কমোডিটি তালিকা
        Expanded(
          child: isLoading
              ? const Center(child: CircularProgressIndicator(color: Color(0xFF1B5E20)))
              : commodities.isEmpty
                  ? const Center(child: Text('কোনো পণ্য পাওয়া যায়নি।'))
                  : ListView.builder(
                      itemCount: commodities.length,
                      itemBuilder: (context, index) => CommodityCard(commodity: commodities[index]),
                    ),
        ),
      ],
    );
  }
}
