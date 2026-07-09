import datetime
import math
from collections import defaultdict
from typing import Dict, Any
from decimal import Decimal

async def compute_financial_intelligence(supabase, user_email: str, months: int = 6) -> dict:
    # 1. Fetch user's profile
    profile_res = supabase.table("tamweel_results") \
        .select("avg_monthly_income_jod, credit_score, risk_level, approved_amount_jod") \
        .eq("email", user_email) \
        .order("generated_at", desc=True) \
        .limit(1) \
        .execute()
    
    if not profile_res.data:
        raise ValueError("Profile not found")
        
    profile = profile_res.data[0]
    avg_monthly_income_jod = Decimal(str(profile.get("avg_monthly_income_jod") or "0.0"))
    credit_score = int(profile.get("credit_score") or 0)
    
    # 2. Fetch transactions for the last `months` months
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=30 * months)
    cutoff_str = cutoff_date.isoformat()
    
    tx_res = supabase.table("transactions") \
        .select("amount, category, created_at, type") \
        .eq("user_email", user_email) \
        .gte("created_at", cutoff_str) \
        .order("created_at", desc=True) \
        .execute()
        
    transactions = tx_res.data or []
    
    # 3. Compute metrics in pure Python
    spending_by_cat = defaultdict(Decimal)
    monthly_spending = defaultdict(Decimal)
    monthly_income_amounts = defaultdict(Decimal)
    
    now = datetime.datetime.utcnow()
    cat_spending_last_2 = defaultdict(Decimal)
    cat_spending_prev_2 = defaultdict(Decimal)
    
    total_spending = Decimal('0.0')
    for tx in transactions:
        amount = Decimal(str(tx.get("amount") or "0.0"))
        tx_type = str(tx.get("type", "expense")).lower()
        cat = tx.get("category", "Uncategorized")
        
        created_at_str = tx.get("created_at")
        if not created_at_str:
            continue
            
        from app.utils import parse_iso_datetime
        try:
            created_at = parse_iso_datetime(created_at_str).replace(tzinfo=None)
        except Exception:
            continue
            
        month_key = created_at.strftime("%Y-%m")
        days_ago = (now - created_at).days
        
        if tx_type == "expense":
            total_spending += amount
            spending_by_cat[cat] += amount
            monthly_spending[month_key] += amount
            
            if days_ago <= 60:
                cat_spending_last_2[cat] += amount
            elif 60 < days_ago <= 120:
                cat_spending_prev_2[cat] += amount
        elif tx_type == "income":
            monthly_income_amounts[month_key] += amount
            
    avg_monthly_spending_jod = total_spending / Decimal(str(months)) if months > 0 else Decimal('0.0')
    
    if avg_monthly_income_jod > 0:
        savings_rate_percent = float(((avg_monthly_income_jod - avg_monthly_spending_jod) / avg_monthly_income_jod) * Decimal('100'))
    else:
        savings_rate_percent = 0.0
        
    spending_by_category_computed = {}
    for cat, total_amt in spending_by_cat.items():
        monthly_avg = total_amt / Decimal(str(months))
        pct_of_income = float((monthly_avg / avg_monthly_income_jod) * Decimal('100')) if avg_monthly_income_jod > 0 else 0.0
        spending_by_category_computed[cat] = {
            "monthly_average": float(monthly_avg),
            "percentage_of_income": pct_of_income
        }
        
    sorted_cats = sorted(spending_by_category_computed.items(), key=lambda x: x[1]["monthly_average"], reverse=True)
    top_3_categories = [cat for cat, _ in sorted_cats[:3]]
    
    spending_trend_per_category = {}
    for cat in spending_by_cat.keys():
        last_2_avg = cat_spending_last_2.get(cat, Decimal('0.0')) / Decimal('2.0')
        prev_2_avg = cat_spending_prev_2.get(cat, Decimal('0.0')) / Decimal('2.0')
        
        if prev_2_avg == 0 and last_2_avg > 0:
            trend = "increasing"
        elif prev_2_avg == 0 and last_2_avg == 0:
            trend = "stable"
        else:
            change = float((last_2_avg - prev_2_avg) / prev_2_avg)
            if change > 0.10:
                trend = "increasing"
            elif change < -0.10:
                trend = "decreasing"
            else:
                trend = "stable"
        spending_trend_per_category[cat] = trend
        
    months_with_overspending = 0
    for m, spent in monthly_spending.items():
        inc_to_compare = avg_monthly_income_jod if avg_monthly_income_jod > 0 else monthly_income_amounts.get(m, Decimal('0.0'))
        if spent > inc_to_compare:
            months_with_overspending += 1
            
    income_vals = list(monthly_income_amounts.values())
    if len(income_vals) > 1:
        mean_inc = sum(income_vals) / Decimal(str(len(income_vals)))
        variance = sum((x - mean_inc) ** 2 for x in income_vals) / Decimal(str(len(income_vals)))
        std_dev = math.sqrt(float(variance))
        if mean_inc > 0:
            cv = std_dev / float(mean_inc)
            income_stability_score = max(0.0, 1.0 - cv)
        else:
            income_stability_score = 0.0
    else:
        income_stability_score = 1.0
        
    # 4. Compute alerts
    alerts = []
    for cat, metrics in spending_by_category_computed.items():
        if metrics["percentage_of_income"] > 25:
            alerts.append(f"Spending in {cat} is high, taking up {metrics['percentage_of_income']:.1f}% of your income.")
            
    for cat, trend in spending_trend_per_category.items():
        if trend == "increasing":
            alerts.append(f"Your spending in {cat} has been increasing over the last 2 months.")
            
    if savings_rate_percent < 20:
        alerts.append(f"Your savings rate is {savings_rate_percent:.1f}%, which is below the recommended 20%.")
        
    if months_with_overspending > 0:
        alerts.append(f"You have overspent your income in {months_with_overspending} month(s).")
        
    if credit_score < 60:
        alerts.append(f"Your credit score is {credit_score}, which is considered below average.")
        
    # 5. Compute strengths
    strengths = []
    if income_stability_score > 0.8:
        strengths.append("Your income is highly stable.")
        
    if savings_rate_percent > 25:
        strengths.append(f"Excellent savings rate of {savings_rate_percent:.1f}%.")
        
    for cat, trend in spending_trend_per_category.items():
        if trend == "decreasing":
            strengths.append(f"You have successfully reduced your spending in {cat}.")
            
    if credit_score > 75:
        strengths.append(f"You have a strong credit score of {credit_score}.")
        
    # 6. Compute credit_improvement_tips
    tips = []
    # Sort categories by percentage of income descending
    sorted_tips_cats = sorted(spending_by_category_computed.items(), key=lambda x: x[1]["percentage_of_income"], reverse=True)
    for cat, metrics in sorted_tips_cats:
        if cat == "transport":
            continue
        if metrics["percentage_of_income"] > 20:
            target_spend = float(avg_monthly_income_jod) * 0.15
            tips.append(f"Reducing {cat} spending from {metrics['monthly_average']:.0f} JOD to {target_spend:.0f} JOD per month could improve your score by approximately 4-6 points.")
            break
            
    if savings_rate_percent < 15:
        tips.append("Increasing your savings rate to 20% would demonstrate stronger financial discipline to lenders.")
        
    if months_with_overspending > 0:
        tips.append(f"You overspent your income in {months_with_overspending} months — maintaining a positive balance every month is the single most impactful credit score improvement action.")
        
    tips = tips[:3]
    
    # 7. Return intelligence object
    return {
        "analysis_period_months": months,
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "income": {
            "average_monthly_jod": float(avg_monthly_income_jod),
            "stability_score": income_stability_score
        },
        "spending": {
            "average_monthly_jod": float(avg_monthly_spending_jod),
            "savings_rate_percent": savings_rate_percent,
            "by_category": spending_by_category_computed,
            "top_3_categories": top_3_categories,
            "trend_per_category": spending_trend_per_category,
            "months_with_overspending": months_with_overspending
        },
        "credit_health": {
            "score": credit_score,
            "risk_level": profile.get("risk_level")
        },
        "alerts": alerts,
        "strengths": strengths,
        "credit_improvement_tips": tips
    }
