class Commodity {
  final int id;
  final String nameBn;
  final String? nameEn;
  final String category;
  final String district;
  final String? marketName;
  final double wholesaleMin;
  final double wholesaleMax;
  final double wholesaleAvg;
  final double retailMin;
  final double retailMax;
  final double retailAvg;
  final String unit;
  final String priceDate;
  final String priceTrend;
  final double priceChangePct;

  Commodity({
    required this.id,
    required this.nameBn,
    this.nameEn,
    required this.category,
    required this.district,
    this.marketName,
    required this.wholesaleMin,
    required this.wholesaleMax,
    required this.wholesaleAvg,
    required this.retailMin,
    required this.retailMax,
    required this.retailAvg,
    required this.unit,
    required this.priceDate,
    required this.priceTrend,
    required this.priceChangePct,
  });

  factory Commodity.fromJson(Map<String, dynamic> json) {
    return Commodity(
      id: json['id'] as int,
      nameBn: json['name_bn'] as String,
      nameEn: json['name_en'] as String?,
      category: json['category'] as String,
      district: json['district'] as String,
      marketName: json['market_name'] as String?,
      wholesaleMin: (json['wholesale_min'] as num).toDouble(),
      wholesaleMax: (json['wholesale_max'] as num).toDouble(),
      wholesaleAvg: (json['wholesale_avg'] as num).toDouble(),
      retailMin: (json['retail_min'] as num).toDouble(),
      retailMax: (json['retail_max'] as num).toDouble(),
      retailAvg: (json['retail_avg'] as num).toDouble(),
      unit: json['unit'] as String? ?? 'কেজি',
      priceDate: json['price_date'] as String,
      priceTrend: json['price_trend'] as String? ?? 'stable',
      priceChangePct: (json['price_change_pct'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
