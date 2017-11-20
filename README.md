#EIA parser
### Gets data from U.S. Energy Information Administration and creates a datapackage
The script was made as a technical task.
Scraps only one page  
https://www.eia.gov/opendata/qb.php?sdid=NG.RNGWHHD.D  
using EIA open API (api specs here: https://www.eia.gov/opendata/commands.php).  
Grabs all data from 1997 till today.  
### Usage
```bash
python3 gas_prices_to_csv.py
```