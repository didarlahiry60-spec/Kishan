import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/commodity.dart';
import '../models/weather.dart';
import '../models/farmer_profile.dart';

class ApiService {
  // লোকাল এমুলেটর বা ডিভাইসের জন্য কনফিগারযোগ্য বেস ইউআরএল (10.0.2.2 ফর অ্যান্ড্রয়েড এমুলেটর)
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';

  static Future<List<Commodity>> fetchDailyPrices({
    required String district,
    String? category,
    String? search,
  }) async {
    var uri = Uri.parse('$baseUrl/bazar/daily?district=${Uri.encodeComponent(district)}');
    if (category != null && category != 'সব') {
      uri = uri.replace(queryParameters: {...uri.queryParameters, 'category': category});
    }
    if (search != null && search.isNotEmpty) {
      uri = uri.replace(queryParameters: {...uri.queryParameters, 'search': search});
    }

    final response = await http.get(uri);
    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(utf8.decode(response.bodyBytes));
      return list.map((e) => Commodity.fromJson(e)).toList();
    }
    throw Exception('Failed to load daily prices');
  }

  static Future<Map<String, dynamic>> fetchMarketSummary(String district) async {
    final response = await http.get(Uri.parse('$baseUrl/bazar/summary?district=${Uri.encodeComponent(district)}'));
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    }
    throw Exception('Failed to load market summary');
  }

  static Future<Map<String, dynamic>> fetchWeatherForecast(String district) async {
    final response = await http.get(Uri.parse('$baseUrl/weather/forecast?district=${Uri.encodeComponent(district)}'));
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    }
    throw Exception('Failed to load weather forecast');
  }

  static Future<AgroAdvisory> fetchAgroAdvisory({
    required String district,
    required List<String> crops,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/weather/advisory'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'district': district, 'crops': crops}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return AgroAdvisory.fromJson(data['advisory']);
    }
    throw Exception('Failed to load agro advisory');
  }

  static Future<FarmerProfile> fetchProfile(String deviceId) async {
    final response = await http.get(Uri.parse('$baseUrl/profile/$deviceId'));
    if (response.statusCode == 200) {
      return FarmerProfile.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    }
    throw Exception('Failed to load farmer profile');
  }

  static Future<FarmerProfile> saveProfile(FarmerProfile profile) async {
    final response = await http.post(
      Uri.parse('$baseUrl/profile'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(profile.toJson()),
    );
    if (response.statusCode == 200) {
      return FarmerProfile.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    }
    throw Exception('Failed to save profile');
  }
}
