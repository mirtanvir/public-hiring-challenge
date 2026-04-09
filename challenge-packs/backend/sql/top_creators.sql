SELECT
  m.campaign_id,
  cr.creator_id,
  cr.creator_name,
  SUM(m.impressions) AS total_impressions,
  SUM(m.clicks) AS total_clicks,
  SUM(m.conversions) AS total_conversions,
  ROUND(SUM(m.spend), 2) AS total_spend,
  ROUND(SUM(m.clicks)::DOUBLE / NULLIF(SUM(m.impressions), 0), 4) AS ctr
FROM campaign_daily_metrics m
JOIN creators cr USING (creator_id)
WHERE m.campaign_id = ?
GROUP BY 1, 2, 3
ORDER BY total_impressions DESC, total_clicks DESC, creator_id DESC
LIMIT ?;
