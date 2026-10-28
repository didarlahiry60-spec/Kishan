class DailyForecast {
  final String date;
  final double tempMax;
  final double tempMin;
  final double precipitationSum;
  final int precipitationProb;
  final double windSpeed;
  final String conditionBn;
  final String riskLevel;

  DailyForecast({
    required this.date,
    required this.tempMax,
    required this.tempMin,
    required this.precipitationSum,
    required this.precipitationProb,
    required this.windSpeed,
    required this.conditionBn,
    required this.riskLevel,
  });

  factory DailyForecast.fromJson(Map<String, dynamic> json) {
    return DailyForecast(
      date: json['date'] as String? ?? '',
      tempMax: (json['temp_max'] as num?)?.toDouble() ?? 30.0,
      tempMin: (json['temp_min'] as num?)?.toDouble() ?? 22.0,
      precipitationSum: (json['precipitation_sum'] as num?)?.toDouble() ?? 0.0,
      precipitationProb: (json['precipitation_prob'] as num?)?.toInt() ?? 0,
      windSpeed: (json['wind_speed'] as num?)?.toDouble() ?? 10.0,
      conditionBn: json['condition_bn'] as String? ?? 'স্বাভাবিক',
      riskLevel: json['risk_level'] as String? ?? 'low',
    );
  }
}

class AgroAdvisory {
  final String headlineBn;
  final String riskLevel;
  final List<String> dosBn;
  final List<String> dontsBn;
  final String irrigationAdviceBn;
  final String voiceScriptBn;

  AgroAdvisory({
    required this.headlineBn,
    required this.riskLevel,
    required this.dosBn,
    required this.dontsBn,
    required this.irrigationAdviceBn,
    required this.voiceScriptBn,
  });

  factory AgroAdvisory.fromJson(Map<String, dynamic> json) {
    return AgroAdvisory(
      headlineBn: json['headline_bn'] as String? ?? 'আবহাওয়া পরামর্শ',
      riskLevel: json['risk_level'] as String? ?? 'low',
      dosBn: (json['dos_bn'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      dontsBn: (json['donts_bn'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      irrigationAdviceBn: json['irrigation_advice_bn'] as String? ?? 'স্বাভাবিক সেচ দিন।',
      voiceScriptBn: json['voice_script_bn'] as String? ?? '',
    );
  }
}
