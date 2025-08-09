"""Compare hotel room prices across travel sites.

This script provides a command line interface that accepts a hotel name,
location, and a set of travel sites (British Airways Holidays, American
Express Travel, and Hilton).  It attempts to retrieve the price of a
single room for the hotel from the selected sites and prints a simple
comparison table.

Network access is required for the data retrieval.  In restricted
environments (such as the execution environment used for this commit)
network access is blocked; the script therefore fails gracefully and
reports the error for each site instead of a price.  The structure is
kept so that it can be extended with real scraping or API calls when run
in an environment that allows outbound network requests.
"""

from __future__ import annotations

import argparse
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple


@dataclass
class Result:
    """A price lookup result for a particular travel site."""

    site: str
    price: Optional[str]
    note: str = ""


def _attempt_fetch(url: str) -> str:
    """Fetch a URL and return its decoded body.

    Any errors are propagated to the caller so that a user friendly
    message can be generated.
    """

    with urllib.request.urlopen(url, timeout=10) as response:  # pragma: no cover - simple wrapper
        return response.read().decode("utf-8", errors="replace")


def _fetch_generic(base_url: str, hotel: str, location: str) -> Tuple[Optional[str], str]:
    """Attempt to retrieve a hotel's price from ``base_url``.

    This function currently just performs an HTTP GET to the provided
    base URL with a simple query string.  Real travel sites require more
    complex interaction which is outside the scope of this example.
    """

    query = urllib.parse.quote_plus(f"{hotel} {location}")
    url = f"{base_url}?q={query}"
    try:
        _attempt_fetch(url)
    except urllib.error.URLError as exc:  # pragma: no cover - network unavailable
        return None, f"request failed: {exc.reason}"
    except Exception as exc:  # pragma: no cover - unexpected issues
        return None, f"request failed: {exc}"
    # Real implementation would parse ``body`` for the price here.
    return None, "price parsing not implemented"


def fetch_british_airways(hotel: str, location: str) -> Result:
    price, note = _fetch_generic("https://www.britishairways.com/travel/hotel", hotel, location)
    return Result(site="British Airways", price=price, note=note)


def fetch_amex_travel(hotel: str, location: str) -> Result:
    price, note = _fetch_generic("https://travel.americanexpress.com/hotels", hotel, location)
    return Result(site="Amex Travel", price=price, note=note)


def fetch_hilton(hotel: str, location: str) -> Result:
    price, note = _fetch_generic("https://www.hilton.com/en/search/", hotel, location)
    return Result(site="Hilton", price=price, note=note)


SITE_FETCHERS: Dict[str, Callable[[str, str], Result]] = {
    "ba": fetch_british_airways,
    "amex": fetch_amex_travel,
    "hilton": fetch_hilton,
}


def compare_prices(hotel: str, location: str, sites: Iterable[str]) -> List[Result]:
    """Compare the price of ``hotel`` across ``sites``.

    ``sites`` should contain keys from :data:`SITE_FETCHERS`.
    """

    results: List[Result] = []
    for key in sites:
        fetcher = SITE_FETCHERS.get(key)
        if not fetcher:
            results.append(Result(site=key, price=None, note="unknown site"))
            continue
        results.append(fetcher(hotel, location))
    return results


def _print_table(results: List[Result]) -> None:
    """Print a simple comparison table for ``results``."""

    header = f"{'Site':<20} {'Price':<10} Note"
    print(header)
    print("-" * len(header))
    for r in results:
        price = r.price if r.price is not None else "N/A"
        print(f"{r.site:<20} {price:<10} {r.note}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hotel", required=True, help="Name of the hotel")
    parser.add_argument("--location", required=True, help="Hotel location")
    parser.add_argument(
        "--sites",
        nargs="*",
        default=list(SITE_FETCHERS.keys()),
        choices=list(SITE_FETCHERS.keys()),
        help="Sites to query (defaults to all)",
    )
    args = parser.parse_args(argv)
    results = compare_prices(args.hotel, args.location, args.sites)
    _print_table(results)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation
    raise SystemExit(main())
