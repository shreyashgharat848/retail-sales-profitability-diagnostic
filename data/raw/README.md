# Raw data

`Superstore.csv` is the widely used **Superstore sample dataset** (a fictional US office-supplies, furniture and
technology retailer): 9,994 order lines, 793 customers, orders from January 2014 to December 2017, values in US dollars.

- It is a public sample dataset, **not real company data**.
- The file is Latin-1 encoded; `src/01_load_to_sqlite.py` handles this.
- It is included so the project runs without extra downloads. Check the licence/terms of the source you
  obtained it from (it originates as a Tableau sample data set) before redistributing it commercially.
- The loader fails loudly if the file does not contain 9,994 rows and 793 customers.
