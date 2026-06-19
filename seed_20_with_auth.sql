-- SQL Script to update schema and insert 20 records with credentials
-- STEP 1: Update the table to include email and password
ALTER TABLE tamweel_results ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;
ALTER TABLE tamweel_results ADD COLUMN IF NOT EXISTS password TEXT;

-- STEP 2: Clear old data to avoid conflicts
TRUNCATE TABLE tamweel_results;

-- STEP 3: Insert 20 records with unique emails and passwords
INSERT INTO tamweel_results (
    name, email, password, profession, profession_category, avg_monthly_income_jod, 
    credit_score, risk_level, decision, approved_amount_jod, reason,
    key_strengths, key_risks, score_breakdown
) VALUES 
('Anas', 'anas@tamweel.ai', 'password123', 'Software Engineer', 'freelance', 850.0, 78, 'Low', 'Approved', 600, 'يظهر ملفك المالي التزاماً جيداً واستقراراً في الدخل الشهري.', ARRAY['استقرار دخل ممتاز', 'التزام تام بسداد الفواتير'], ARRAY['تنوع مصادر الدخل يمكن أن يتحسن'], '{"income_stability": 35, "bill_history": 25, "financial_health": 18}'::jsonb),
('Samer', 'samer@tamweel.ai', 'pass123', 'Senior Developer', 'freelance', 1200.0, 89, 'Low', 'Approved', 1000, 'سجل ائتماني ممتاز مع تدفقات نقدية قوية ومستقرة.', ARRAY['دخل مرتفع', 'تاريخ ائتماني نظيف'], ARRAY['لا توجد مخاطر جوهرية'], '{"income_stability": 38, "bill_history": 28, "financial_health": 23}'::jsonb),
('Rana', 'rana@tamweel.ai', 'pass123', 'Instagram Store Owner', 'gig', 450.0, 52, 'Medium', 'Conditional Approval', 300, 'تمت الموافقة المشروطة نظراً لتذبذب الدخل الشهري.', ARRAY['نشاط تجاري مستمر'], ARRAY['تذبذب في الرصيد'], '{"income_stability": 20, "bill_history": 15, "financial_health": 17}'::jsonb),
('Khaled', 'khaled@tamweel.ai', 'pass123', 'Construction Worker', 'gig', 300.0, 25, 'High', 'Rejected', 0, 'نسبة المخاطر عالية بسبب التأخر المتكرر في سداد الالتزامات.', ARRAY['وجود مصدر دخل'], ARRAY['تأخير متكرر في الفواتير'], '{"income_stability": 10, "bill_history": 5, "financial_health": 10}'::jsonb),
('Laila', 'laila@tamweel.ai', 'pass123', 'Graphic Designer', 'freelance', 700.0, 68, 'Low', 'Approved', 600, 'ملف مالي جيد مع الزام مقبول بسداد الفواتير.', ARRAY['مهارات مطلوبة', 'دخل منتظم'], ARRAY['استخدام عالي للرصيد'], '{"income_stability": 28, "bill_history": 22, "financial_health": 18}'::jsonb),
('Omar', 'omar@tamweel.ai', 'pass123', 'Uber Driver', 'gig', 550.0, 61, 'Low', 'Approved', 600, 'دخل يومي مستقر يدعم قدرتك على السداد.', ARRAY['تدفق نقدي يومي'], ARRAY['مصاريف تشغيلية عالية'], '{"income_stability": 25, "bill_history": 20, "financial_health": 16}'::jsonb),
('Zaid', 'zaid@tamweel.ai', 'pass123', 'Marketing Consultant', 'freelance', 950.0, 82, 'Low', 'Approved', 1000, 'أداء مالي متميز مع مدخرات جيدة.', ARRAY['مدخرات قوية', 'التزام مالي'], ARRAY['مخاطر منخفضة جداً'], '{"income_stability": 34, "bill_history": 26, "financial_health": 22}'::jsonb),
('Sara', 'sara@tamweel.ai', 'pass123', 'Careem Delivery', 'gig', 380.0, 44, 'Medium', 'Conditional Approval', 150, 'الموافقة على مبلغ محدود لبناء تاريخ ائتماني.', ARRAY['نشاط عالي'], ARRAY['دخل منخفض نسبياً'], '{"income_stability": 18, "bill_history": 12, "financial_health": 14}'::jsonb),
('Muna', 'muna@tamweel.ai', 'pass123', 'Online Tutor', 'freelance', 500.0, 58, 'Medium', 'Conditional Approval', 300, 'قدرة جيدة على السداد مع الحاجة لزيادة استقرار الدخل.', ARRAY['دخل من مصادر متعددة'], ARRAY['سجل مدفوعات حديث'], '{"income_stability": 22, "bill_history": 18, "financial_health": 18}'::jsonb),
('Hassan', 'hassan@tamweel.ai', 'pass123', 'Carpenter', 'gig', 420.0, 37, 'Medium', 'Conditional Approval', 150, 'يوجد تأخير في بعض الفواتير، يرجى الالتزام لتحسين السكور.', ARRAY['حرفة يدوية مطلوبة'], ARRAY['فواتير متأخرة'], '{"income_stability": 15, "bill_history": 10, "financial_health": 12}'::jsonb),
('Yousef', 'yousef@tamweel.ai', 'pass123', 'Food Delivery', 'gig', 400.0, 49, 'Medium', 'Conditional Approval', 300, 'ملف مقبول مع حاجة لتحسين إدارة السيولة.', ARRAY['عمل مستمر'], ARRAY['رصيد منخفض نهاية الشهر'], '{"income_stability": 19, "bill_history": 16, "financial_health": 14}'::jsonb),
('Aya', 'aya@tamweel.ai', 'pass123', 'Content Creator', 'freelance', 650.0, 64, 'Low', 'Approved', 600, 'نمو جيد في الدخل خلال الأشهر الثلاثة الماضية.', ARRAY['نمو في الدخل'], ARRAY['حداثة السجل المالي'], '{"income_stability": 26, "bill_history": 20, "financial_health": 18}'::jsonb),
('Fadi', 'fadi@tamweel.ai', 'pass123', 'Electrician', 'gig', 480.0, 55, 'Medium', 'Conditional Approval', 300, 'دخل جيد مع وجود التزامات مالية أخرى.', ARRAY['دخل مستقر'], ARRAY['قروض قائمة'], '{"income_stability": 21, "bill_history": 17, "financial_health": 17}'::jsonb),
('Nour', 'nour@tamweel.ai', 'pass123', 'Handmade Crafts', 'freelance', 320.0, 31, 'High', 'Conditional Approval', 150, 'الدخل يقترب من الحد الأدنى، يرجى زيادة المبيعات.', ARRAY['شغف بالعمل'], ARRAY['دخل غير كافٍ'], '{"income_stability": 12, "bill_history": 10, "financial_health": 9}'::jsonb),
('Rami', 'rami@tamweel.ai', 'pass123', 'Private Driver', 'gig', 500.0, 59, 'Medium', 'Conditional Approval', 300, 'التزام جيد بالسداد مع تذبذب طفيف في الدخل.', ARRAY['التزام بالسداد'], ARRAY['دخل غير متنوع'], '{"income_stability": 23, "bill_history": 19, "financial_health": 17}'::jsonb),
('Tariq', 'tariq@tamweel.ai', 'pass123', 'SEO Expert', 'freelance', 1100.0, 85, 'Low', 'Approved', 1000, 'ملف مالي قوي جداً يعكس إدارة مالية حكيمة.', ARRAY['دخل مرتفع وثابت'], ARRAY['لا يوجد'], '{"income_stability": 36, "bill_history": 27, "financial_health": 22}'::jsonb),
('Hala', 'hala@tamweel.ai', 'pass123', 'Translator', 'freelance', 600.0, 62, 'Low', 'Approved', 600, 'استمرارية جيدة في العمل الحر مع سجل سداد منتظم.', ARRAY['استمرارية العمل'], ARRAY['مبالغ فواتير متغيرة'], '{"income_stability": 24, "bill_history": 21, "financial_health": 17}'::jsonb),
('Majd', 'majd@tamweel.ai', 'pass123', 'Fitness Coach', 'gig', 750.0, 71, 'Low', 'Approved', 600, 'توازن جيد بين الدخل والمصاريف الشهرية.', ARRAY['توازن مالي'], ARRAY['ارتباط الدخل بالمواسم'], '{"income_stability": 29, "bill_history": 22, "financial_health": 20}'::jsonb),
('Dina', 'dina@tamweel.ai', 'pass123', 'Event Planner', 'freelance', 800.0, 74, 'Low', 'Approved', 600, 'سجل مالي نظيف مع تدفقات نقدية إيجابية.', ARRAY['إدارة سيولة جيدة'], ARRAY['مصاريف تسويق عالية'], '{"income_stability": 31, "bill_history": 23, "financial_health": 20}'::jsonb),
('Suleiman', 'suleiman@tamweel.ai', 'pass123', 'Tailor', 'gig', 350.0, 41, 'Medium', 'Conditional Approval', 150, 'الحاجة لتحسين تاريخ دفع الفواتير لرفع السكور.', ARRAY['مهارة فنية'], ARRAY['تأخير في المدفوعات'], '{"income_stability": 16, "bill_history": 12, "financial_health": 13}'::jsonb);
