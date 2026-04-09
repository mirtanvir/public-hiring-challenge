SELECT
  metric_date,
  impressions AS total_impressions,
  clicks AS total_clicks,
  conversions AS total_conversions,
  spend AS total_spend,
  revenue AS total_revenue,
  ROUND(clicks::DOUBLE / NULLIF(impressions, 0), 4) AS ctr,
  ROUND(revenue / NULLIF(spend, 0), 4) AS roas
FROM campaign_daily_metrics
WHERE campaign_id = ?
ORDER BY metric_date;
