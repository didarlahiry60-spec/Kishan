import 'package:flutter/material.dart';
import '../models/farmer_profile.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  final FarmerProfile profile;
  final Function(FarmerProfile) onProfileUpdated;

  const ProfileScreen({Key? key, required this.profile, required this.onProfileUpdated}) : super(key: key);

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late TextEditingController nameCtrl;
  late TextEditingController phoneCtrl;
  late TextEditingController upazilaCtrl;
  late String selectedDistrict;
  late List<String> userCrops;
  late bool smsEnabled;

  final allCrops = ['ধান', 'আলু', 'পেঁয়াজ', 'কাঁচা মরিচ', 'সরিষা', 'টমেটো', 'বেগুন', 'ভুট্টা'];
  final districts = ['বগুড়া', 'ঢাকা', 'রাজশাহী', 'যশোর', 'দিনাজপুর', 'রংপুর', 'ময়মনসিংহ', 'কুমিল্লা', 'চট্টগ্রাম'];

  @override
  void initState() {
    super.initState();
    nameCtrl = TextEditingController(text: widget.profile.name);
    phoneCtrl = TextEditingController(text: widget.profile.phone ?? '');
    upazilaCtrl = TextEditingController(text: widget.profile.upazila);
    selectedDistrict = widget.profile.district;
    userCrops = List.from(widget.profile.favoriteCrops);
    smsEnabled = widget.profile.smsAlertsEnabled;
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        elevation: 2,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text('🌾 আমার খামার ও প্রোফাইল', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              const Text('পাসওয়ার্ডের প্রয়োজন নেই। আপনার এলাকা ও প্রধান ফসল বাছাই করুন।', style: TextStyle(fontSize: 12, color: Colors.grey)),
              const Divider(height: 24),

              TextField(
                controller: nameCtrl,
                decoration: const InputDecoration(labelText: 'কৃষকের নাম', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),

              TextField(
                controller: phoneCtrl,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(labelText: 'মোবাইল নম্বর (SMS সতর্কতার জন্য)', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: selectedDistrict,
                      decoration: const InputDecoration(labelText: 'জেলা', border: OutlineInputBorder()),
                      items: districts.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
                      onChanged: (val) {
                        if (val != null) setState(() => selectedDistrict = val);
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: upazilaCtrl,
                      decoration: const InputDecoration(labelText: 'উপজেলা', border: OutlineInputBorder()),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              const Text('আপনার প্রধান ফসলসমূহ:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: allCrops.map((c) {
                  final isSelected = userCrops.contains(c);
                  return FilterChip(
                    label: Text(c),
                    selected: isSelected,
                    selectedColor: Colors.green.shade100,
                    onSelected: (val) {
                      setState(() {
                        if (val) userCrops.add(c);
                        else userCrops.remove(c);
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 14),

              CheckboxListTile(
                value: smsEnabled,
                title: const Text('জরুরি আবহাওয়া সতর্কবার্তা সরাসরি বাংলা SMS এ পেতে চাই', style: TextStyle(fontSize: 13)),
                onChanged: (val) => setState(() => smsEnabled = val ?? true),
                controlAffinity: ListTileControlAffinity.leading,
                contentPadding: EdgeInsets.zero,
              ),
              const SizedBox(height: 14),

              ElevatedButton(
                onPressed: () async {
                  final updated = FarmerProfile(
                    deviceId: widget.profile.deviceId,
                    name: nameCtrl.text.trim(),
                    phone: phoneCtrl.text.trim().isNotEmpty ? phoneCtrl.text.trim() : null,
                    district: selectedDistrict,
                    upazila: upazilaCtrl.text.trim(),
                    favoriteCrops: userCrops,
                    smsAlertsEnabled: smsEnabled,
                  );
                  final saved = await ApiService.saveProfile(updated);
                  widget.onProfileUpdated(saved);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('✓ তথ্য সফলভাবে সংরক্ষিত হয়েছে!')),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1B5E20),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                child: const Text('তথ্য সেভ করুন', style: TextStyle(fontSize: 16, color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
