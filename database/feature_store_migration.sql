-- 1. Create the Feature Store Table
CREATE TABLE IF NOT EXISTS user_financial_features (
    user_email TEXT PRIMARY KEY REFERENCES tamweel_results(email) ON DELETE CASCADE,
    total_income DECIMAL DEFAULT 0,
    total_expense DECIMAL DEFAULT 0,
    savings_rate DECIMAL DEFAULT 0,
    volatility DECIMAL DEFAULT 0,
    reliability INT DEFAULT 0,
    top_category VARCHAR DEFAULT 'none',
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create the Trigger Function to maintain aggregates
CREATE OR REPLACE FUNCTION refresh_user_features()
RETURNS TRIGGER AS $$
DECLARE
    v_email TEXT;
    v_total_income DECIMAL;
    v_total_expense DECIMAL;
    v_savings_rate DECIMAL;
    v_volatility DECIMAL;
    v_reliability INT;
    v_top_category VARCHAR;
BEGIN
    -- Determine the user_email affected
    IF TG_OP = 'DELETE' THEN
        v_email := OLD.user_email;
    ELSE
        v_email := NEW.user_email;
    END IF;

    -- Calculate Totals
    SELECT COALESCE(SUM(amount), 0) INTO v_total_income FROM transactions WHERE user_email = v_email AND type = 'income';
    SELECT COALESCE(SUM(amount), 0) INTO v_total_expense FROM transactions WHERE user_email = v_email AND type = 'expense';
    
    -- Calculate Savings Rate
    IF v_total_income > 0 THEN
        v_savings_rate := (v_total_income - v_total_expense) / v_total_income;
    ELSE
        v_savings_rate := 0;
    END IF;

    -- Calculate Volatility (safe division)
    SELECT 
        CASE 
            WHEN COUNT(*) < 2 THEN 0
            ELSE COALESCE(STDDEV_POP(monthly_total), 0)
        END INTO v_volatility
    FROM (
        SELECT DATE_TRUNC('month', created_at) as month, SUM(amount) as monthly_total
        FROM transactions
        WHERE user_email = v_email AND type = 'expense'
        GROUP BY month
    ) monthly_expenses;

    -- Calculate Reliability
    SELECT COUNT(*) INTO v_reliability FROM transactions WHERE user_email = v_email AND category = 'utilities';
    
    -- Identify Top Expense Category
    SELECT category INTO v_top_category 
    FROM transactions 
    WHERE user_email = v_email AND type = 'expense' 
    GROUP BY category 
    ORDER BY SUM(amount) DESC 
    LIMIT 1;

    -- Upsert the calculated features into the feature store
    INSERT INTO user_financial_features 
        (user_email, total_income, total_expense, savings_rate, volatility, reliability, top_category, last_updated)
    VALUES 
        (v_email, v_total_income, v_total_expense, ROUND(v_savings_rate, 4), ROUND(v_volatility, 2), v_reliability, COALESCE(v_top_category, 'none'), NOW())
    ON CONFLICT (user_email) DO UPDATE SET
        total_income = EXCLUDED.total_income,
        total_expense = EXCLUDED.total_expense,
        savings_rate = EXCLUDED.savings_rate,
        volatility = EXCLUDED.volatility,
        reliability = EXCLUDED.reliability,
        top_category = EXCLUDED.top_category,
        last_updated = EXCLUDED.last_updated;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 3. Bind the trigger to the transactions table
DROP TRIGGER IF EXISTS trg_update_features ON transactions;
CREATE TRIGGER trg_update_features
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW EXECUTE FUNCTION refresh_user_features();

-- 4. Rewrite calculate_financial_health to decouple from raw transactions
CREATE OR REPLACE FUNCTION calculate_financial_health(target_email TEXT)
RETURNS JSON AS $$
DECLARE
    feature_record RECORD;
BEGIN
    -- Ultra-fast point lookup from the Feature Store
    SELECT * INTO feature_record FROM user_financial_features WHERE user_email = target_email;
    
    IF NOT FOUND THEN
        RETURN json_build_object(
            'savings_rate', 0,
            'volatility', 0,
            'reliability', 0,
            'total_income', 0,
            'total_expense', 0,
            'top_category', 'none'
        );
    END IF;

    RETURN json_build_object(
        'savings_rate', feature_record.savings_rate,
        'volatility', feature_record.volatility,
        'reliability', feature_record.reliability,
        'total_income', feature_record.total_income,
        'total_expense', feature_record.total_expense,
        'top_category', feature_record.top_category
    );
END;
$$ LANGUAGE plpgsql STABLE;
