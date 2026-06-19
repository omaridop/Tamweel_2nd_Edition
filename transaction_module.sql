-- 1. Create Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT REFERENCES tamweel_results(email) ON DELETE CASCADE,
    amount DECIMAL NOT NULL,
    type VARCHAR(10) CHECK (type IN ('income', 'expense')),
    category VARCHAR(50) CHECK (category IN ('salary', 'utilities', 'groceries', 'zaincash_transfer', 'business_supplies', 'rent', 'other')),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Advanced Logic: Financial Health Calculation Function
CREATE OR REPLACE FUNCTION calculate_financial_health(target_email TEXT)
RETURNS JSON AS $$
DECLARE
    total_income DECIMAL;
    total_expense DECIMAL;
    savings_rate DECIMAL;
    volatility DECIMAL;
    reliability INT;
    top_category VARCHAR;
BEGIN
    -- Calculate Totals
    SELECT COALESCE(SUM(amount), 0) INTO total_income FROM transactions WHERE user_email = target_email AND type = 'income';
    SELECT COALESCE(SUM(amount), 0) INTO total_expense FROM transactions WHERE user_email = target_email AND type = 'expense';
    
    -- Calculate Savings Rate
    IF total_income > 0 THEN
        savings_rate := (total_income - total_expense) / total_income;
    ELSE
        savings_rate := 0;
    END IF;

    -- Calculate Volatility (Standard Deviation of Monthly Expenses)
    SELECT COALESCE(STDDEV_POP(monthly_total), 0) INTO volatility
    FROM (
        SELECT DATE_TRUNC('month', created_at) as month, SUM(amount) as monthly_total
        FROM transactions
        WHERE user_email = target_email AND type = 'expense'
        GROUP BY month
    ) monthly_expenses;

    -- Calculate Reliability (Count of Utility payments representing discipline)
    SELECT COUNT(*) INTO reliability FROM transactions WHERE user_email = target_email AND category = 'utilities';
    
    -- Identify Top Expense Category
    SELECT category INTO top_category 
    FROM transactions 
    WHERE user_email = target_email AND type = 'expense' 
    GROUP BY category 
    ORDER BY SUM(amount) DESC 
    LIMIT 1;

    RETURN json_build_object(
        'savings_rate', ROUND(savings_rate, 4),
        'volatility', ROUND(volatility, 2),
        'reliability', reliability,
        'total_income', total_income,
        'total_expense', total_expense,
        'top_category', COALESCE(top_category, 'none')
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- 3. Seed Data for "Anas" (High Variability, 3 Months)
DO $$
DECLARE
    target TEXT := 'anas@tamweel.ai';
BEGIN
    -- Month 1 (Good Savings)
    INSERT INTO transactions (user_email, amount, type, category, description, created_at) VALUES
    (target, 950.00, 'income', 'salary', 'Freelance Contract', NOW() - INTERVAL '90 days'),
    (target, 200.00, 'expense', 'rent', 'Monthly Rent', NOW() - INTERVAL '88 days'),
    (target, 50.00, 'expense', 'utilities', 'Electricity', NOW() - INTERVAL '85 days'),
    (target, 150.00, 'expense', 'groceries', 'Supermarket', NOW() - INTERVAL '80 days');

    -- Month 2 (High Volatility, Business Investment)
    INSERT INTO transactions (user_email, amount, type, category, description, created_at) VALUES
    (target, 800.00, 'income', 'salary', 'Freelance Contract', NOW() - INTERVAL '60 days'),
    (target, 200.00, 'expense', 'rent', 'Monthly Rent', NOW() - INTERVAL '58 days'),
    (target, 450.00, 'expense', 'business_supplies', 'New Laptop / Equipment', NOW() - INTERVAL '55 days'),
    (target, 50.00, 'expense', 'utilities', 'Electricity', NOW() - INTERVAL '50 days');

    -- Month 3 (Current)
    INSERT INTO transactions (user_email, amount, type, category, description, created_at) VALUES
    (target, 1100.00, 'income', 'zaincash_transfer', 'Client Payment', NOW() - INTERVAL '30 days'),
    (target, 200.00, 'expense', 'rent', 'Monthly Rent', NOW() - INTERVAL '28 days'),
    (target, 50.00, 'expense', 'utilities', 'Electricity', NOW() - INTERVAL '25 days'),
    (target, 300.00, 'expense', 'groceries', 'Supermarket', NOW() - INTERVAL '15 days');
END $$;