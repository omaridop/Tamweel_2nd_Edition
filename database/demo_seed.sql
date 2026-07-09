-- Demo Preparation Seed Script
-- Inserts 3 realistic Jordanian profiles and 45 transactions

DO $$
DECLARE
    hash TEXT := '$2b$12$1PQdlNpY35zcPqHZ2k/roe1n2BdDgdPDE7tU8v/HUdD1kLgE4znua';
    ahmad_email TEXT := 'ahmad@tamweel.ai';
    sara_email TEXT := 'sara@tamweel.ai';
    tariq_email TEXT := 'tariq@tamweel.ai';
BEGIN
    -- ==========================================
    -- 1. Insert Profiles into tamweel_results
    -- ==========================================
    
    -- Ahmad: Careem Driver (Score: 78, Low Risk)
    INSERT INTO tamweel_results (
        name, email, password, role, profession, profession_category, avg_monthly_income_jod, 
        credit_score, risk_level, decision, approved_amount_jod, reason,
        key_strengths, key_risks, score_breakdown, generated_at
    ) VALUES (
        'Ahmad Careem', ahmad_email, hash, 'user', 'Careem Driver', 'gig', 850.0,
        78, 'Low', 'Approved', 600,
        'دخلك الشهري مستقر وتاريخ سداد الفواتير ممتاز.',
        ARRAY['استقرار الدخل', 'عدم وجود دفعات متأخرة'], ARRAY['نسبة الدين إلى الدخل قريبة من الحد الأعلى'],
        '{"income_stability": 35, "bill_history": 28, "financial_health": 15}', NOW()
    ) ON CONFLICT (email) DO NOTHING;

    -- Sara: Freelance Designer (Score: 54, Medium Risk)
    INSERT INTO tamweel_results (
        name, email, password, role, profession, profession_category, avg_monthly_income_jod, 
        credit_score, risk_level, decision, approved_amount_jod, reason,
        key_strengths, key_risks, score_breakdown, generated_at
    ) VALUES (
        'Sara Designer', sara_email, hash, 'user', 'Freelance Designer', 'freelance', 600.0,
        54, 'Medium', 'Conditional Approval', 300,
        'يوجد تذبذب في الدخل بسبب طبيعة العمل الحر، ولكن مستوى الادخار جيد.',
        ARRAY['مستوى ادخار جيد'], ARRAY['تذبذب الدخل الشهري', 'فاتورة متأخرة واحدة'],
        '{"income_stability": 20, "bill_history": 20, "financial_health": 14}', NOW()
    ) ON CONFLICT (email) DO NOTHING;

    -- Tariq: New Micro-entrepreneur (Score: 31, High Risk)
    INSERT INTO tamweel_results (
        name, email, password, role, profession, profession_category, avg_monthly_income_jod, 
        credit_score, risk_level, decision, approved_amount_jod, reason,
        key_strengths, key_risks, score_breakdown, generated_at
    ) VALUES (
        'Tariq Entrepreneur', tariq_email, hash, 'user', 'Micro-entrepreneur', 'business', 400.0,
        31, 'High', 'Conditional Approval', 150,
        'العمل التجاري جديد والمخاطرة عالية حالياً، ننصح بتقليل النفقات.',
        ARRAY['تنوع مصادر الدخل'], ARRAY['تأخر في سداد 3 فواتير', 'رصيد منخفض جداً', 'عمر المشروع قصير'],
        '{"income_stability": 10, "bill_history": 10, "financial_health": 11}', NOW()
    ) ON CONFLICT (email) DO NOTHING;

    -- ==========================================
    -- 2. Insert Transactions
    -- ==========================================
    
    -- Ahmad (Careem Driver) Transactions
    -- Maps: food -> groceries, transport -> other (Transport), entertainment -> other (Entertainment)
    INSERT INTO transactions (user_email, amount, type, category, description, created_at) VALUES
    (ahmad_email, 250.00, 'income', 'salary', 'Careem Weekly Payout', NOW() - INTERVAL '28 days'),
    (ahmad_email, 35.00, 'expense', 'other', 'Transport - Gas Station', NOW() - INTERVAL '27 days'),
    (ahmad_email, 40.00, 'expense', 'groceries', 'Food - Supermarket', NOW() - INTERVAL '25 days'),
    (ahmad_email, 15.00, 'expense', 'other', 'Entertainment - Coffee Shop', NOW() - INTERVAL '24 days'),
    (ahmad_email, 20.00, 'expense', 'utilities', 'Zain Phone Bill', NOW() - INTERVAL '22 days'),
    (ahmad_email, 220.00, 'income', 'salary', 'Careem Weekly Payout', NOW() - INTERVAL '21 days'),
    (ahmad_email, 30.00, 'expense', 'other', 'Transport - Maintenance', NOW() - INTERVAL '20 days'),
    (ahmad_email, 55.00, 'expense', 'groceries', 'Food - Grocery run', NOW() - INTERVAL '18 days'),
    (ahmad_email, 25.00, 'expense', 'other', 'Entertainment - Cinema', NOW() - INTERVAL '15 days'),
    (ahmad_email, 280.00, 'income', 'salary', 'Careem Weekly Payout', NOW() - INTERVAL '14 days'),
    (ahmad_email, 40.00, 'expense', 'other', 'Transport - Gas Station', NOW() - INTERVAL '12 days'),
    (ahmad_email, 60.00, 'expense', 'groceries', 'Food - Carefour', NOW() - INTERVAL '10 days'),
    (ahmad_email, 150.00, 'expense', 'rent', 'House Rent', NOW() - INTERVAL '8 days'),
    (ahmad_email, 20.00, 'expense', 'other', 'Entertainment - Subscription', NOW() - INTERVAL '5 days'),
    (ahmad_email, 240.00, 'income', 'salary', 'Careem Weekly Payout', NOW() - INTERVAL '1 days');

    -- Sara (Freelance Designer) Transactions
    INSERT INTO transactions (user_email, amount, type, category, description, created_at) VALUES
    (sara_email, 600.00, 'income', 'salary', 'Upwork Payout', NOW() - INTERVAL '30 days'),
    (sara_email, 45.00, 'expense', 'groceries', 'Food - Cozmo', NOW() - INTERVAL '28 days'),
    (sara_email, 10.00, 'expense', 'other', 'Transport - Uber', NOW() - INTERVAL '27 days'),
    (sara_email, 25.00, 'expense', 'other', 'Entertainment - Netflix & Spotify', NOW() - INTERVAL '25 days'),
    (sara_email, 30.00, 'expense', 'utilities', 'Internet Bill', NOW() - INTERVAL '22 days'),
    (sara_email, 120.00, 'expense', 'business_supplies', 'Adobe Creative Cloud', NOW() - INTERVAL '20 days'),
    (sara_email, 35.00, 'expense', 'groceries', 'Food - Bakery and Veggies', NOW() - INTERVAL '18 days'),
    (sara_email, 12.00, 'expense', 'other', 'Transport - Careem Ride', NOW() - INTERVAL '15 days'),
    (sara_email, 40.00, 'expense', 'other', 'Entertainment - Restaurant with friends', NOW() - INTERVAL '12 days'),
    (sara_email, 200.00, 'expense', 'rent', 'Studio Rent', NOW() - INTERVAL '10 days'),
    (sara_email, 50.00, 'expense', 'groceries', 'Food - Supermarket', NOW() - INTERVAL '8 days'),
    (sara_email, 15.00, 'expense', 'other', 'Transport - Uber', NOW() - INTERVAL '6 days'),
    (sara_email, 150.00, 'income', 'salary', 'Local Client Transfer', NOW() - INTERVAL '4 days'),
    (sara_email, 20.00, 'expense', 'other', 'Entertainment - Cafe working', NOW() - INTERVAL '2 days'),
    (sara_email, 30.00, 'expense', 'utilities', 'Electricity', NOW() - INTERVAL '1 days');

    -- Tariq (Micro-entrepreneur) Transactions
    INSERT INTO transactions (user_email, amount, type, category, description, created_at) VALUES
    (tariq_email, 150.00, 'income', 'zaincash_transfer', 'Customer Sale', NOW() - INTERVAL '29 days'),
    (tariq_email, 80.00, 'expense', 'business_supplies', 'Raw Materials', NOW() - INTERVAL '28 days'),
    (tariq_email, 25.00, 'expense', 'groceries', 'Food - Quick snacks', NOW() - INTERVAL '26 days'),
    (tariq_email, 15.00, 'expense', 'other', 'Transport - Delivery fuel', NOW() - INTERVAL '25 days'),
    (tariq_email, 10.00, 'expense', 'other', 'Entertainment - Tea shop', NOW() - INTERVAL '23 days'),
    (tariq_email, 180.00, 'income', 'zaincash_transfer', 'Customer Sale', NOW() - INTERVAL '20 days'),
    (tariq_email, 100.00, 'expense', 'business_supplies', 'Packaging', NOW() - INTERVAL '19 days'),
    (tariq_email, 40.00, 'expense', 'utilities', 'Overdue Electricity', NOW() - INTERVAL '17 days'),
    (tariq_email, 30.00, 'expense', 'groceries', 'Food - Local market', NOW() - INTERVAL '15 days'),
    (tariq_email, 20.00, 'expense', 'other', 'Transport - Bus and taxi', NOW() - INTERVAL '12 days'),
    (tariq_email, 120.00, 'income', 'zaincash_transfer', 'Customer Sale', NOW() - INTERVAL '10 days'),
    (tariq_email, 150.00, 'expense', 'rent', 'Shop Rent', NOW() - INTERVAL '8 days'),
    (tariq_email, 15.00, 'expense', 'other', 'Entertainment - Cafe', NOW() - INTERVAL '6 days'),
    (tariq_email, 35.00, 'expense', 'groceries', 'Food - Grocery store', NOW() - INTERVAL '3 days'),
    (tariq_email, 20.00, 'expense', 'other', 'Transport - Delivery fuel', NOW() - INTERVAL '1 days');

END $$;
