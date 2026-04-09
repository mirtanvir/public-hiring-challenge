SELECT
  c.campaign_id,
  c.campaign_name,
  SUM(m.impressions) AS total_impressions,
  SUM(m.clicks) AS total_clicks,
  SUM(m.conversions) AS total_conversions,
  ROUND(SUM(m.spend), 2) AS total_spend,
  ROUND(SUM(COALESCE(m.revenue, 0)), 2) AS total_revenue,
  ROUND(SUM(m.clicks)::DOUBLE / NULLIF(SUM(m.impressions), 0), 4) AS ctr,
  ROUND(SUM(m.conversions)::DOUBLE / NULLIF(SUM(m.impressions), 0), 4) AS cvr,
  ROUND(AVG(COALESCE(m.revenue, 0)) / NULLIF(SUM(m.spend), 0), 4) AS roas
FROM campaign_daily_metrics m
JOIN campaigns c USING (campaign_id)
WHERE c.campaign_id = ?
GROUP BY 1, 2;
