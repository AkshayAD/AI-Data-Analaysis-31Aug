-- Customer Analysis Queries
-- Database: customer_analytics

-- Query 1: Get customer churn rate by month
SELECT 
    DATE_TRUNC('month', churn_date) AS month,
    COUNT(CASE WHEN churn = 'Yes' THEN 1 END) AS churned_customers,
    COUNT(*) AS total_customers,
    ROUND(COUNT(CASE WHEN churn = 'Yes' THEN 1 END) * 100.0 / COUNT(*), 2) AS churn_rate
FROM customers
WHERE churn_date >= '2023-01-01'
GROUP BY DATE_TRUNC('month', churn_date)
ORDER BY month;

-- Query 2: Top factors correlated with churn
SELECT 
    tenure_months,
    AVG(monthly_charges) AS avg_monthly_charges,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned_count
FROM customers
GROUP BY tenure_months
HAVING COUNT(*) > 10
ORDER BY churned_count DESC;

-- Query 3: Customer lifetime value calculation
SELECT 
    customer_id,
    tenure_months,
    monthly_charges,
    total_charges,
    CASE 
        WHEN churn = 'No' THEN monthly_charges * 24
        ELSE total_charges
    END AS estimated_ltv
FROM customers
ORDER BY estimated_ltv DESC
LIMIT 100;