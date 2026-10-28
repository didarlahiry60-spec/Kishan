from typing import Dict, Any

class NegotiationCalculator:
    """
    Aratdar Negotiation and Farm Profitability Calculator.
    Empowers farmers with real numbers, gross margins, and negotiation scripts.
    """

    def calculate_deal(
        self,
        crop_name: str,
        quantity_mon: float,
        production_cost_per_mon: float,
        transport_cost_per_mon: float,
        market_wholesale_per_kg: float,
        aratdar_offered_per_mon: float = 0.0
    ) -> Dict[str, Any]:
        KG_PER_MON = 40.0
        
        # সরকারি রেটে প্রতি মণের পাইকারি দর
        fair_market_price_per_mon = round(market_wholesale_per_kg * KG_PER_MON, 1)
        total_quantity_kg = quantity_mon * KG_PER_MON

        # মোট ব্যয়
        total_prod_cost = round(production_cost_per_mon * quantity_mon, 1)
        total_transport_cost = round(transport_cost_per_mon * quantity_mon, 1)
        total_cost = round(total_prod_cost + total_transport_cost, 1)
        cost_per_mon = round(production_cost_per_mon + transport_cost_per_mon, 1)

        # ন্যায্য বাজারমূল্যে মোট প্রাপ্তি
        fair_gross_revenue = round(fair_market_price_per_mon * quantity_mon, 1)
        fair_net_profit = round(fair_gross_revenue - total_cost, 1)
        fair_margin_pct = round((fair_net_profit / total_cost) * 100, 1) if total_cost > 0 else 0.0

        # ব্রেক-ইভেন দর (যে দরের নিচে বিক্রি করলে লোকসান হবে)
        break_even_price_per_mon = cost_per_mon
        break_even_price_per_kg = round(cost_per_mon / KG_PER_MON, 1)

        # আড়তদারের প্রস্তাবের সাথে তুলনা
        aratdar_evaluation = ""
        difference_per_mon = 0.0
        if aratdar_offered_per_mon > 0:
            difference_per_mon = round(fair_market_price_per_mon - aratdar_offered_per_mon, 1)
            if aratdar_offered_per_mon < break_even_price_per_mon:
                aratdar_evaluation = f"সতর্কতা: আড়তদারের অফার ({int(aratdar_offered_per_mon)} ৳/মণ) আপনার উৎপাদন ও পরিবহন খরচের চেয়ে কম! এতে প্রতি মণে {int(break_even_price_per_mon - aratdar_offered_per_mon)} টাকা লোকসান হবে।"
            elif aratdar_offered_per_mon < fair_market_price_per_mon:
                aratdar_evaluation = f"আড়তদার সরকারি ন্যায্য পাইকারি দরের চেয়ে মণে {int(difference_per_mon)} টাকা কম প্রস্তাব করছে।"
            else:
                aratdar_evaluation = "আড়তদারের অফার সরকারি ন্যায্য পাইকারি রেটের কাছাকাছি বা ভালো।"

        # নেগোসিয়েশন ডায়ালগ জেনারেশন
        suggested_dialogue = (
            f"আড়তদার ভাইকে বলবেন: 'ভাই, আজকের সরকারি পাইকারি রেট কেজি প্রতি {int(market_wholesale_per_kg)} টাকা হিসেবে প্রতি মণ {int(fair_market_price_per_mon)} টাকা। "
            f"আমার {crop_name}-এর মান অত্যন্ত ভালো এবং মাঠ থেকে সরাসরি আনা। প্রতি মণে আমার উৎপাদন ও পরিবহন খরচই পড়েছে {int(cost_per_mon)} টাকা। "
            f"আপনার ন্যায্য আড়তদারি কমিশন বাদ দিয়ে আমাকে অন্তত {int(fair_market_price_per_mon * 0.95)} থেকে {int(fair_market_price_per_mon)} টাকা দিতে হবে, এর নিচে ছাড়লে আমার ক্ষতি হয়ে যাবে।'"
        )

        return {
            "crop_name": crop_name,
            "quantity_mon": quantity_mon,
            "total_quantity_kg": total_quantity_kg,
            "break_even_per_mon": break_even_price_per_mon,
            "break_even_per_kg": break_even_price_per_kg,
            "fair_market_per_mon": fair_market_price_per_mon,
            "total_cost": total_cost,
            "fair_gross_revenue": fair_gross_revenue,
            "fair_net_profit": fair_net_profit,
            "profit_margin_pct": fair_margin_pct,
            "aratdar_evaluation": aratdar_evaluation,
            "negotiation_script_bn": suggested_dialogue
        }

negotiation_calculator = NegotiationCalculator()
