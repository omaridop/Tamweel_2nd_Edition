def print_report(res):
    def ar(text):
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    score_bar = "█" * int(res['final_score'] / 10) + "░" * (10 - int(res['final_score'] / 10))
    
    print("\n" + "═"*52)
    print("   TAMWEEL AI | HYBRID CREDIT ASSESSMENT REPORT")
    print("═"*52)
    print(f"   Applicant      : {res['applicant_name']}")
    print(f"   Profession     : {res['profession']}")
    print(f"   Timestamp      : {res['timestamp']}")
    print("─"*52)
    print(f"   ML Score       : {res['ml_score']:.1f}/100  (XGBoost)")
    print(f"   Adjusted Score : {res['llm_adjusted_score']:.1f}/100 (DeepSeek-V4/OpenRouter RAG)")
    print(f"   Final Score    : {res['final_score']:.1f}/100  [{score_bar}]")
    print(f"   Confidence     : {res['confidence']}")
    print("─"*52)
    print(f"   Risk Level     : {res['risk_level']}")
    print(f"   Decision       : {res['decision']}")
    print(f"   Approved Amt   : {res['approved_amount_jod']} JOD")
    print("─"*52)
    print("   Score Breakdown:")
    breakdown = res.get('score_breakdown', {})
    print(f"   Income Stability   : {breakdown.get('income_stability', 0)}/40")
    print(f"   Bill History       : {breakdown.get('bill_history', 0)}/30")
    print(f"   Financial Health   : {breakdown.get('financial_health', 0)}/30")
    print("─"*52)
    print("   Strengths:")
    for s in res.get('key_strengths', []):
        print(f"              + {s}")
    print("   Risks:")
    for r in res.get('key_risks', []):
        print(f"              - {r}")
    print("─"*52)
    print("   Arabic Reason:")
    print(f"   {ar(res['reason'])}")
    print("═"*52 + "\n")
