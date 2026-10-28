import 'package:flutter/material.dart';
import '../models/commodity.dart';
import '../services/audio_service.dart';

class CommodityCard extends StatelessWidget {
  final Commodity commodity;

  const CommodityCard({Key? key, required this.commodity}) : super(key: key);

  String _toBn(num n) {
    const bn = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
    return n.toString().replaceAllMapped(RegExp(r'[0-9]'), (m) => bn[int.parse(m[0]!)]);
  }

  @override
  Widget build(BuildContext context) {
    Color trendColor = Colors.grey;
    String trendText = 'অপরিবর্তিত';
    if (commodity.priceTrend == 'up') {
      trendColor = Colors.red.shade700;
      trendText = '▲ +${_toBn(commodity.priceChangePct)}% বৃদ্ধি';
    } else if (commodity.priceTrend == 'down') {
      trendColor = Colors.green.shade700;
      trendText = '▼ ${_toBn(commodity.priceChangePct)}% হ্রাস';
    }

    return Card(
      elevation: 1.5,
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // স্পিকার বাটন
            InkWell(
              onTap: () {
                final speech = '${commodity.district} মোকামে ${commodity.nameBn} পাইকারি প্রতি ${commodity.unit} ${_toBn(commodity.wholesaleAvg)} টাকা এবং খুচরা দর ${_toBn(commodity.retailAvg)} টাকা।';
                AudioService().speakBengali(speech);
              },
              borderRadius: BorderRadius.circular(20),
              child: Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: const Icon(Icons.volume_up, color: Color(0xFF1B5E20), size: 20),
              ),
            ),
            const SizedBox(width: 12),

            // পণ্যের নাম ও মোকাম
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    commodity.nameBn,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    commodity.marketName ?? commodity.district,
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ),

            // দাম ও ট্রেন্ড
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Row(
                  children: [
                    Text('পাইকারি: ', style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                    Text(
                      '৳${_toBn(commodity.wholesaleMin)}-${_toBn(commodity.wholesaleMax)}',
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20)),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Row(
                  children: [
                    Text('খুচরা: ', style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                    Text(
                      '৳${_toBn(commodity.retailAvg)}/${commodity.unit}',
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.blueGrey.shade800),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: trendColor.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    trendText,
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: trendColor),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
