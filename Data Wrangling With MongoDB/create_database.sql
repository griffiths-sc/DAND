.open area.db
.read data_wrangling_schema.sql
.mode csv
.import nodes.csv nodes
.import nodes_tags.csv nodes_tags
.import ways.csv ways
.import ways_tags.csv ways_tags
.import ways_nodes.csv ways_nodes
