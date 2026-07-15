import logging
from typing import List, Dict, Any
from modules.dork_optimizer.constants import (
    DORK_PATTERNS, GLOBAL_NEGATIVE_FILTERS, COUNTRY_DIRECTORIES, COUNTRY_TLDS
)
from modules.dork_optimizer.dork_scorer import DorkScorer

# Maps lowercase country name -> its primary ccTLD.
# Used to fill {tlds} in dork templates.
# Defaults to "com" when country is not found.
COUNTRY_TLD_MAP: dict[str, str] = {
    "usa":                      "com",
    "united states":            "com",
    "united states of america": "com",
    "us":                       "com",
    "uk":                       "co.uk",
    "united kingdom":           "co.uk",
    "britain":                  "co.uk",
    "england":                  "co.uk",
    "uae":                      "ae",
    "united arab emirates":     "ae",
    "dubai":                    "ae",
    "abu dhabi":                "ae",
    "germany":                  "de",
    "deutschland":              "de",
    "france":                   "fr",
    "netherlands":              "nl",
    "holland":                  "nl",
    "italy":                    "it",
    "italia":                   "it",
    "spain":                    "es",
    "espana":                   "es",
    "australia":                "com.au",
    "canada":                   "ca",
    "india":                    "in",
    "brazil":                   "com.br",
    "mexico":                   "com.mx",
    "south africa":             "co.za",
    "new zealand":              "co.nz",
    "singapore":                "com.sg",
    "pakistan":                 "com.pk",
    "bangladesh":               "com.bd",
    "nigeria":                  "com.ng",
    "kenya":                    "co.ke",
    "egypt":                    "com.eg",
    "saudi arabia":             "com.sa",
    "qatar":                    "com.qa",
    "kuwait":                   "com.kw",
    "indonesia":                "co.id",
    "malaysia":                 "com.my",
    "philippines":              "com.ph",
    "thailand":                 "co.th",
    "turkey":                   "com.tr",
    "russia":                   "ru",
    "china":                    "cn",
    "japan":                    "co.jp",
    "south korea":              "co.kr",
    "ireland":                  "ie",
    "sweden":                   "se",
    "norway":                   "no",
    "denmark":                  "dk",
    "finland":                  "fi",
    "poland":                   "pl",
    "portugal":                 "pt",
    "belgium":                  "be",
    "switzerland":              "ch",
    "austria":                  "at",
    "greece":                   "gr",
    "israel":                   "co.il",
    "argentina":                "com.ar",
    "chile":                    "cl",
    "colombia":                 "com.co",
    "peru":                     "com.pe",
    "ghana":                    "com.gh",
    "ethiopia":                 "com.et",
    "tanzania":                 "co.tz",
    "zimbabwe":                 "co.zw",
    "zambia":                   "co.zm",
    "uganda":                   "co.ug",
}

# Appended to every single dork query — keeps noise out of results
DORK_EXCLUSIONS = (
    " -site:youtube.com -site:x.com -site:twitter.com"
    " -site:reddit.com -site:quora.com -site:wikipedia.org"
    " -site:trustpilot.com -site:clutch.co -site:sortlist.com"
    " -site:capterra.com -site:g2.com"
    " -jobs -careers -hiring -news -blog -pdf"
)

logger = logging.getLogger(__name__)


def _get_tld(country: str) -> str:
    """
    Returns the primary ccTLD for the given country string.
    Strips whitespace, lowercases, looks up COUNTRY_TLD_MAP.
    Falls back to 'com' for unknown countries.

    Examples:
        _get_tld("UK")      -> "co.uk"
        _get_tld("Germany") -> "de"
        _get_tld("Kenya")   -> "co.ke"
        _get_tld("Nepal")   -> "com"   (fallback)
    """
    return COUNTRY_TLD_MAP.get(country.strip().lower(), "com")


def generate_manual_dorks(business: str, city: str = "", country: str = "") -> List[str]:
    """
    Build the raw manual dork list for a business, city, and country.
    """
    # ── Normalise inputs ────────────────────────────────────────────────────────
    business = business.strip()   # use the existing param name — do not rename
    city     = city.strip()       # new optional param — empty string if not provided
    country  = country.strip()

    # ── Resolve ccTLD from country ───────────────────────────────────────────────
    tld = _get_tld(country)

    excl = DORK_EXCLUSIONS

    # ── Build the raw dork list from exact templates ─────────────────────────────
    #
    # Placeholder mapping:
    #   {BUSINESS} -> business variable
    #   {CITY}     -> city variable
    #   {COUNTRY}  -> country variable
    #   {tlds}     -> tld variable  (e.g. "co.uk", "de", "com")
    #
    # IMPORTANT — site: prefix rules (match EXACTLY as shown):
    #   site:{tlds}   -> f"site:{tld}"    — NO dot before tld  (e.g. site:co.uk)
    #   site:.com     -> "site:.com"      — WITH dot            (hardcoded, never changes)
    #
    # City-based templates (lines marked <- CITY) are skipped when city == ""
    # to avoid generating malformed queries like "dentists" "" "UK".

    raw_dorks: list[str] = []

    # ── Group 1: Plain keyword queries ───────────────────────────────────────────
    if city:  # <- CITY
        raw_dorks.append(f'"{business}" "{city}" "{country}"')

    raw_dorks.extend([
        f'"{business}" "{country}"',
    ])

    if city:  # <- CITY
        raw_dorks.append(f'"{business}" "{city}"')

    raw_dorks.extend([
        f'"{business}" "{country}" Official',
        f'"{business}" "{country}" Company',
        f'"{business}" "{country}" Ltd',
        f'"{business}" "{country}" LLC',
        f'"{business}" "{country}" Inc',
        f'"{business}" "{country}" (contact OR "contact us")',
        f'"{business}" "{country}" ("Email" OR "E-mail")',
        f'"{business}" "{country}" ("Phone" OR "Tel")',
        f'"{business}" "{country}" Address',
        f'"{business}" "{country}" "Head Office"',
        f'"{business}" "{country}" "Corporate Office"',
    ])

    # ── Group 2: site:{tld} queries ──────────────────────────────────────────────
    raw_dorks.extend([
        f'site:{tld} "{business}" "{country}"',
    ])

    if city:  # <- CITY
        raw_dorks.append(f'site:{tld} "{business}" "{city}"')

    raw_dorks.extend([
        f'site:{tld} "{business}" Official',
        f'site:{tld} "{business}" Company',
        f'site:{tld} "{business}" Contact',
        f'site:{tld} "{business}" Address',
        f'site:{tld} "{business}" ("Email" OR "Phone")',
    ])

    # ── Group 3: site:.com queries (dot-com hardcoded) ───────────────────────────
    raw_dorks.extend([
        f'site:.com "{business}" "{country}"',
        f'site:.com "{business}" Contact',
        f'site:.com "{business}" Address',
        f'site:.com "{business}" ("Email" OR "Phone")',
    ])

    # ── Group 4: inurl / intitle queries ─────────────────────────────────────────
    raw_dorks.extend([
        f'site:{tld} inurl:contact "{business}"',
        f'site:{tld} inurl:contact-us "{business}"',
        f'site:{tld} inurl:about "{business}"',
        f'site:{tld} intitle:Contact "{business}"',
        f'site:{tld} intitle:"Contact Us" "{business}"',
        f'site:{tld} intitle:"About Us" "{business}"',
        f'inurl:contact "{business}" "{country}"',
        f'intitle:Contact "{business}" "{country}"',
    ])

    # ── Group 5: Email address patterns ──────────────────────────────────────────
    raw_dorks.extend([
        f'site:{tld} "{business}" info@',
        f'site:{tld} "{business}" contact@',
        f'site:{tld} "{business}" sales@',
        f'site:{tld} "{business}" support@',
        f'site:{tld} "{business}" mailto:',
    ])

    # ── Group 6: Phone patterns ───────────────────────────────────────────────────
    raw_dorks.extend([
        f'site:{tld} "{business}" Phone',
        f'site:{tld} "{business}" Tel',
        f'site:{tld} "{business}" Telephone',
    ])

    # ── Group 7: Social platforms ─────────────────────────────────────────────────
    raw_dorks.extend([
        f'site:facebook.com "{business}" "{country}"',
    ])

    if city:  # <- CITY
        raw_dorks.append(f'site:facebook.com "{business}" "{city}"')

    raw_dorks.extend([
        f'site:linkedin.com/company "{business}" "{country}"',
    ])

    if city:  # <- CITY
        raw_dorks.append(f'site:linkedin.com/company "{business}" "{city}"')

    # ── Append exclusions to every dork ──────────────────────────────────────────
    dorks_with_exclusions = [d + excl for d in raw_dorks]

    # ── Deduplicate while preserving insertion order ──────────────────────────────
    # (handles cases like USA where site:{tld} == site:com
    #  and could produce near-identical queries)
    seen: set[str] = set()
    final: list[str] = []
    for d in dorks_with_exclusions:
        if d not in seen:
            seen.add(d)
            final.append(d)

    return final

class DorkGenerator:
    def __init__(self):
        self.scorer = DorkScorer()

    def _lookup_country_value(self, mapping: Dict[str, Any], country: str, default: Any) -> Any:
        if not country:
            return default

        normalized_country = country.strip().casefold()

        for key, value in mapping.items():
            if key == country or key.casefold() == normalized_country:
                return value

        return default

    def _get_country_tld(self, country: str) -> str:
        return self._lookup_country_value(COUNTRY_TLDS, country, "com")

    def _compile_dork_exclusions(self, country: str, exclude_directories: bool, exclude_jobs_blogs: bool) -> List[str]:
        exclusions = []
        
        # 1. Directory exclusions
        if exclude_directories and country:
            # Match directly or by upper-case key
            direct_excl = self._lookup_country_value(COUNTRY_DIRECTORIES, country, None)
            if direct_excl:
                exclusions.extend(direct_excl)
            else:
                # Add default generic directory exclusions
                exclusions.extend(["-directory", "-listings", "-yellowpages"])
                
        # 2. Jobs, blogs, news, wikipedia exclusions
        if exclude_jobs_blogs:
            exclusions.extend(GLOBAL_NEGATIVE_FILTERS)
            
        return exclusions

    def generate_from_opportunity(self, opportunity: Dict[str, Any], dork_count: int = 10) -> List[Dict[str, Any]]:
        """
        Generates advanced Google dorks for B2B local business search from a parsed opportunity.
        """
        category = opportunity.get("category", "Business")
        region = opportunity.get("region") or opportunity.get("state") or "Metropolitan"
        country = opportunity.get("country", "")
        target_service = opportunity.get("target_service", "Lead Generation")
        
        country_tld = self._get_country_tld(country)
        exclusions = self._compile_dork_exclusions(
            country=country,
            exclude_directories=opportunity.get("exclude_directories", True),
            exclude_jobs_blogs=opportunity.get("exclude_jobs_blogs_news", True)
        )
        
        dorks = []
        
        # Loop through B2B dork patterns round-robin style until we hit dork_count
        pattern_keys = list(DORK_PATTERNS.keys())
        dorks_compiled = 0
        
        for idx in range(dork_count):
            p_key = pattern_keys[idx % len(pattern_keys)]
            patterns = DORK_PATTERNS[p_key]
            pattern = patterns[(idx // len(pattern_keys)) % len(patterns)]
            
            # Formulate the query by replacing template parameters
            base_query = pattern.replace("{category}", category).replace("{region}", region).replace("{country_tld}", country_tld)
            
            # Combine exclusions
            dork_query = base_query
            if exclusions:
                dork_query = f"{base_query} {' '.join(exclusions)}"
                
            # Score
            ctx = {"country": country, "region": region, "category": category, "target_service": target_service}
            score = self.scorer.score_dork(dork_query, ctx)
            
            dorks.append({
                "dork": dork_query,
                "dork_type": p_key,
                "intent": f"Identify leads for B2B {target_service} in {region}",
                "quality_score": score,
                "country": country,
                "region": region,
                "category": category,
                "target_service": target_service
            })
            
        return dorks

    def generate_manual(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compiles custom Google dorks based on explicit user form configurations.
        """
        category = config.get("category", "Business")
        sub_category = config.get("sub_category")
        region = config.get("city") or config.get("region") or config.get("state") or ""
        country = config.get("country", "")
        target_service = config.get("target_service", "SEO")

        search_category = f"{category} {sub_category}".strip() if sub_category else category.strip()
        dork_strings = generate_manual_dorks(search_category, region, country)

        include_keywords = config.get("include_keywords", "")
        exclude_keywords = config.get("exclude_keywords", "")

        include_terms = [kw.strip() for kw in include_keywords.split(",") if kw.strip()] if include_keywords else []
        exclude_terms = [kw.strip() for kw in exclude_keywords.split(",") if kw.strip()] if exclude_keywords else []

        if include_terms or exclude_terms:
            expanded_dorks: List[str] = []
            for dork in dork_strings:
                updated_dork = dork
                for kw in include_terms:
                    updated_dork = f'{updated_dork} "{kw}"'
                for kw in exclude_terms:
                    updated_dork = f'{updated_dork} -"{kw}"'
                expanded_dorks.append(updated_dork)

            seen_queries: set[str] = set()
            dork_strings = []
            for dork in expanded_dorks:
                if dork not in seen_queries:
                    seen_queries.add(dork)
                    dork_strings.append(dork)

        if config.get("exclude_directories", False) and country:
            direct_excl = self._lookup_country_value(COUNTRY_DIRECTORIES, country, None)
            if direct_excl:
                directory_suffix = " ".join(direct_excl)
            else:
                directory_suffix = "-directory -listings -yellowpages"

            dork_strings = [f"{dork} {directory_suffix}" for dork in dork_strings]

        if config.get("exclude_jobs_blogs_news", False):
            global_suffix = " ".join(GLOBAL_NEGATIVE_FILTERS)
            dork_strings = [f"{dork} {global_suffix}" for dork in dork_strings]

        num_dorks = config.get("num_dorks")
        if isinstance(num_dorks, int) and num_dorks > 0:
            dork_strings = dork_strings[:num_dorks]

        dorks = []
        for dork_query in dork_strings:
            ctx = {"country": country, "region": region, "category": search_category, "target_service": target_service}
            score = self.scorer.score_dork(dork_query, ctx)

            dorks.append({
                "dork": dork_query,
                "dork_type": "manual",
                "intent": f"Identify leads for B2B {target_service} in {region}",
                "quality_score": score,
                "country": country,
                "region": region,
                "category": search_category,
                "target_service": target_service
            })

        return dorks
