# jon-test

Example project containing a simple script for comparing hotel room
prices across several travel sites.  The `hotel_price_comparison.py`
module offers a command line interface:

```
python hotel_price_comparison.py --hotel "Hilton London Kensington" --location London
```

In this execution environment outbound network access is blocked, so the
script demonstrates the structure of the comparison but reports errors
instead of real prices.  When run on a machine with internet access the
fetch functions can be extended to parse prices from the respective
sites.
