class FarmerProfile {
  final String deviceId;
  final String name;
  final String? phone;
  final String district;
  final String upazila;
  final List<String> favoriteCrops;
  final bool smsAlertsEnabled;

  FarmerProfile({
    required this.deviceId,
    required this.name,
    this.phone,
    required this.district,
    required this.upazila,
    required this.favoriteCrops,
    required this.smsAlertsEnabled,
  });

  factory FarmerProfile.fromJson(Map<String, dynamic> json) {
    final cropsRaw = json['favorite_crops'] as String? ?? 'ধান,আলু,পেঁয়াজ';
    return FarmerProfile(
      deviceId: json['device_id'] as String? ?? '',
      name: json['name'] as String? ?? 'কৃষক বন্ধু',
      phone: json['phone'] as String?,
      district: json['district'] as String? ?? 'বগুড়া',
      upazila: json['upazila'] as String? ?? 'শিবগঞ্জ',
      favoriteCrops: cropsRaw.split(',').map((e) => e.trim()).toList(),
      smsAlertsEnabled: json['sms_alerts_enabled'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'device_id': deviceId,
      'name': name,
      'phone': phone,
      'district': district,
      'upazila': upazila,
      'favorite_crops': favoriteCrops.join(','),
      'sms_alerts_enabled': smsAlertsEnabled,
    };
  }
}
