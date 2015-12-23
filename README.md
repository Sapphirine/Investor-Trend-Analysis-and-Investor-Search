# Investor-Trend-Analysis-and-Investor-Search
Note: all input files are in csv format
-------------------------------------------------------------------------
investor_trends.py
- uses mini-batch m-means to cluster investor filings to find investment trends

arguments: 1) number of clusters 2) input file name  3) mode (1 or 2)
input file format in mode 1 (do not include header line with column names):
  - each row contains the following columns separated by commas
Investor Country(int)
Holdings Latest Change(int)
Security Country(int)
Security GICS Sector(int)
Investor Institution Type(int)
Investor Market Value (float)
Security Market Capitalization (float)

input file format in mode 2 includes all the columns in mode 1 plus the following columns (do not include header line with column names):
- each percent portfolio value is in the following format: 99.56 for 99.56%
Percent Portfolio in Consumer Discretionary (GICS Sector)
Percent Portfolio in Consumer Staples (GICS Sector)
Percent Portfolio in Energy (GICS Sector)
Percent Portfolio in Financials (GICS Sector)
Percent Portfolio in Healthcare (GICS Sector)
Percent Portfolio in Industrials (GICS Sector)
Percent Portfolio in Information Technology (GICS Sector)
Percent Portfolio in Materials (GICS Sector)
Percent Portfolio in Telecommunication Services (GICS Sector)
Percent Portfolio in Utilities (GICS Sector)

The script also expects the following files to be in the same folder:
These files are used to build dictionaries of the enumerations in the input file and the actual name associated with the enumeration.
holder_country.csv
format: country name(string), country number(int)
sec_country.csv
format: country name(string), country number(int)
sector.csv
format: sector name(string), sector number (int)
inst_type.csv
format: institution type (string), institution type number (int)


-------------------------------------------------------------------------

investor_search.py
- uses SGD classifier and K-Means clustering to identify new investors 

arguments: 1) holders file name 2) non-holders file name 3) number of clusters
holders file: List of holders of the target security
holders file format:
unique investor ID (string), holder name(string)

non-holders file: list of non-holders of the target security
non-holders file format:
unique investor ID (string), holder name(string)

The script also expects the following files to be in the same folder:
sector.csv
- used to build a dictionary between the enumeration of the sector in the sec_fundamentals.csv file and the name of theh sector
format: sector name (string), sector number (int)

holder_index.csv
- list of indexes of the boundaries between the holdings of each investor in sec_fundamentals.csv. All holdings of an investor is listed together in sec_fundamentals.csv
format: index number

sec_fundamentals.csv
- file with all of the security characteristics of each filing. Filings for each investor are grouped together, with boundaries defined in holder_index.csv
format:
unique investor ID(string)
unique investor ID(string, same as above)
Security GICS Sector (int)
Security Gross Margin (float)
Security Sales Growth (float)
Security PE Ratio (float)
Security Dividend Yield (float)
Security EPS (float)
Security Debt to Equity Ratio (float)
Security PS Ratio (float)
Security PB Ratio (float)
Security Market Cap(float)

sec_prop.csv
- security properties of the target security
Security GICS Sector (int)
Security Gross Margin (float)
Security Sales Growth (float)
Security PE Ratio (float)
Security Dividend Yield (float)
Security EPS (float)
Security Debt to Equity Ratio (float)
Security PS Ratio (float)
Security PB Ratio (float)
Security Market Cap(float)
