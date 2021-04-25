CREATE OR REPLACE VIEW wine_searchindexview AS
SELECT row_number() OVER () as id,
       wine_producer.id as producer_id, 
       NULLIF(wine_wine.id,0) as wine_id, 
       NULLIF(wine_market.id,0) as market_id
FROM wine_producer  
LEFT JOIN wine_wine on wine_producer.id = wine_wine.producer_id 
LEFT JOIN wine_market on wine_wine.id = wine_market.wine_id