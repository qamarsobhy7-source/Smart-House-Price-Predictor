"""PropertyFinder Scraper — v1.0
Extracts real estate listings from PropertyFinder Egypt.
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
BASE_DIR = Path(__file__).resolve().parent

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

DEFAULT_DELAY = (2, 4)  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30


# ═══════════════════════════════════════════════════════
# FETCH
# ═══════════════════════════════════════════════════════
def _get_headers():
    """Random headers to look like a real browser."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    }


def fetch_page(url, delay=DEFAULT_DELAY, max_retries=MAX_RETRIES):
    """Fetch a page with retries and rate limiting."""
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(*delay))

            r = requests.get(url, headers=_get_headers(), timeout=TIMEOUT)

            if r.status_code == 200:
                return r.text
            elif r.status_code == 429:  # Too Many Requests
                wait = 60 * (attempt + 1)
                print(f"   ⚠️ 429 Too Many Requests — waiting {wait}s")
                time.sleep(wait)
            else:
                print(f"   ⚠️ HTTP {r.status_code} — attempt {attempt + 1}")

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Error: {e} — attempt {attempt + 1}")
            time.sleep(5 * (attempt + 1))

    return None


# ═══════════════════════════════════════════════════════
# PARSE
# ═══════════════════════════════════════════════════════
def extract_next_data(html):
    """Extract __NEXT_DATA__ JSON from PropertyFinder page."""
    match = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        html,
        re.DOTALL
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None




# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════
def _parse_bedrooms(value):
    """Convert bedrooms value to int (handles 'studio', '3', 3, None)."""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().lower()
    if s in ('', 'none', 'nan', 'null'):
        return 0
    if s == 'studio':
        return 0
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def _parse_bathrooms(value):
    """Convert bathrooms value to int."""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().lower()
    if s in ('', 'none', 'nan', 'null'):
        return 0
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0




# ═══════════════════════════════════════════════════════
# GOVERNORATE NORMALIZER
# ═══════════════════════════════════════════════════════
GOVERNORATE_ALIASES = {
    # Cairo variations
    'cairo': 'Cairo',
    'new cairo city': 'Cairo',
    'new cairo': 'Cairo',
    'the 5th settlement': 'Cairo',
    'nasr city': 'Cairo',
    'heliopolis': 'Cairo',
    'maadi': 'Cairo',
    'mokattam': 'Cairo',
    'zamalek': 'Cairo',
    'downtown': 'Cairo',
    'new capital city': 'Cairo',
    'new administrative capital': 'Cairo',
    'badr city': 'Cairo',
    'shorouk city': 'Cairo',
    'obour city': 'Cairo',
    '10th of ramadan': 'Sharqia',
    'sheikh zayed': 'Giza',
    'sheikh zayed city': 'Giza',
    '6th of october': 'Giza',
    '6th of october city': 'Giza',
    '6 october': 'Giza',
    '6 october city': 'Giza',
    'october city': 'Giza',
    'giza': 'Giza',
    'haram': 'Giza',
    'faisal': 'Giza',
    'mohandessin': 'Giza',
    'dokki': 'Giza',
    'agouza': 'Giza',
    'imbaba': 'Giza',
    'mostakbal city': 'Cairo',
    'mostakbal city - future city': 'Cairo',
    # Alexandria
    'alexandria': 'Alexandria',
    'smouha': 'Alexandria',
    'sidi gaber': 'Alexandria',
    'montazah': 'Alexandria',
    'miami': 'Alexandria',
    'agami': 'Alexandria',
    # Red Sea
    'red sea': 'Red Sea',
    'hurghada': 'Red Sea',
    'el gouna': 'Red Sea',
    'sahl hasheesh': 'Red Sea',
    'makadi': 'Red Sea',
    'soma bay': 'Red Sea',
    'marsa alam': 'Red Sea',
    'magawish': 'Red Sea',
    'al ahyaa district': 'Red Sea',
    # Matruh / North Coast
    'matruh': 'Matruh',
    'mattrouh': 'Matruh',
    'marsa matruh': 'Matruh',
    'north coast': 'Matruh',
    'sidi abdel rahman': 'Matruh',
    'ras al hekma': 'Matruh',
    'al alamein': 'Matruh',
    'alamein': 'Matruh',
    'el alamein': 'Matruh',
    'dabaa': 'Matruh',
    # Suez
    'suez': 'Suez',
    'ain sokhna': 'Suez',
    'al ain al sokhna': 'Suez',
    # Qalyubia
    'qalyubia': 'Qalyubia',
    'banha': 'Qalyubia',
    'shubra el kheima': 'Qalyubia',
    'qalyub': 'Qalyubia',
    # Dakahlia
    'dakahlia': 'Dakahlia',
    'mansoura': 'Dakahlia',
    'talkha': 'Dakahlia',
    # Sharqia
    'sharqia': 'Sharqia',
    'zagazig': 'Sharqia',
    'belbeis': 'Sharqia',
    # Gharbia
    'gharbia': 'Gharbia',
    'tanta': 'Gharbia',
    'el mahalla el kubra': 'Gharbia',
    'mahalla': 'Gharbia',
    # Monufia
    'monufia': 'Monufia',
    'menoufia': 'Monufia',
    'shebin el kom': 'Monufia',
    # Beheira
    'beheira': 'Beheira',
    'damanhour': 'Beheira',
    'kafr el dawwar': 'Beheira',
}


def _normalize_governorate(text):
    """Normalize a governorate name using aliases."""
    if not text:
        return ''
    key = str(text).strip().lower()
    return GOVERNORATE_ALIASES.get(key, text)


def _detect_governorate_from_parts(parts):
    """Find the correct governorate by checking all parts against aliases."""
    if not parts:
        return ''
    # نفحص من آخر جزء للأول — آخر جزء عادةً الـ governorate
    for part in reversed(parts):
        key = str(part).strip().lower()
        if key in GOVERNORATE_ALIASES:
            return GOVERNORATE_ALIASES[key]
    # fallback: آخر جزء
    return parts[-1]


def parse_listing(prop):
    """Convert a PropertyFinder listing to our flat format."""
    loc = prop.get('location', {}) or {}
    coords = loc.get('coordinates', {}) or {}
    price = prop.get('price', {}) or {}
    size = prop.get('size', {}) or {}
    loc_tree = prop.get('location_tree', []) or []
    location_full = loc.get('full_name', '') or ''

    # ───────────────────────────────────────────────
    # استخراج العنوان من location_full (الأدق)
    # مثال: "Garden Residence, Hyde Park, New Cairo City, Cairo"
    # ───────────────────────────────────────────────
    governorate = ""
    city = ""
    district = ""
    compound = ""
    area = ""

    parts = [p.strip() for p in location_full.split(',') if p.strip()]

    # نحاول نلاقي الـ governorate الصح من كل الأجزاء
    governorate = _detect_governorate_from_parts(parts)

    if len(parts) >= 4:
        # [compound, area/zone, district, governorate]
        compound = parts[0]
        area = parts[1]
        district = parts[2]
        city = parts[2]
    elif len(parts) == 3:
        # [area, city, governorate]
        area = parts[0]
        city = parts[1]
        district = parts[0]
    elif len(parts) == 2:
        # [district, governorate]
        district = parts[0]
        city = parts[0]
    elif len(parts) == 1:
        city = parts[0]
        district = parts[0]

    # ───────────────────────────────────────────────
    # Override بـ location_tree لو فيه معلومات أدق
    # ───────────────────────────────────────────────
    for item in loc_tree:
        t = item.get('type', '').upper()
        name = item.get('name', '')
        if t in ('CITY',) and not city:
            city = name
        elif t in ('DISTRICT', 'AREA') and not district:
            district = name
        elif t in ('COMPOUND', 'TOWER', 'BUILDING') and not compound:
            compound = name

    # Amenities — join as string
    amenities = prop.get('amenities', []) or []
    amenity_names = prop.get('amenity_names', []) or []

    # Images
    images = prop.get('images', []) or []
    image_urls = [img.get('medium', '') for img in images if img.get('medium')]

    return {
        'id': prop.get('id', ''),
        'title': prop.get('title', ''),
        'price': price.get('value', 0),
        'currency': price.get('currency', 'EGP'),
        'price_period': price.get('period', 'sell'),
        'property_type': prop.get('property_type', ''),
        'size': size.get('value', 0),
        'size_unit': size.get('unit', 'sqm'),
        'bedrooms': _parse_bedrooms(prop.get('bedrooms') or prop.get('bedrooms_value')),
        'bathrooms': _parse_bathrooms(prop.get('bathrooms') or prop.get('bathrooms_value')),
        'governorate': governorate,
        'city': city,
        'district': district,
        'compound': compound,
        'area': area,
        'location_full': location_full,
        'location_name': loc.get('name', ''),
        'latitude': coords.get('lat'),
        'longitude': coords.get('lon'),
        'amenities': ','.join(amenities) if amenities else '',
        'amenity_names': ','.join(amenity_names) if amenity_names else '',
        'images_count': prop.get('images_count', 0),
        'images': '|'.join(image_urls[:5]),  # first 5 images
        'description': (prop.get('description', '') or '')[:1000],
        'completion_status': prop.get('completion_status', ''),
        'furnished': prop.get('furnished', ''),
        'is_verified': prop.get('is_verified', False),
        'is_premium': prop.get('is_premium', False),
        'is_featured': prop.get('is_featured', False),
        'is_new_construction': prop.get('is_new_construction', False),
        'is_direct_from_developer': prop.get('is_direct_from_developer', False),
        'listed_date': prop.get('listed_date', ''),
        'broker_name': (prop.get('broker', {}) or {}).get('name', ''),
        'agent_name': (prop.get('agent', {}) or {}).get('name', ''),
        'share_url': prop.get('share_url', ''),
        'reference': prop.get('reference', ''),
        'scraped_at': datetime.now().isoformat(),
    }


def extract_listings_from_page(html, expected_governorate=None):
    """Extract all listings from one search page.

    Args:
        html: page HTML
        expected_governorate: if set, filter to only listings in this governorate (case-insensitive)
    """
    data = extract_next_data(html)
    if not data:
        return [], {}

    try:
        sr = data['props']['pageProps']['searchResult']
    except (KeyError, TypeError):
        return [], {}

    listings_raw = sr.get('listings', []) or []
    meta = sr.get('meta', {}) or {}

    listings = []
    skipped_type = 0
    skipped_empty = 0
    skipped_gov = 0

    for item in listings_raw:
        # فلتر 1: نوع الإعلان لازم يكون 'property'
        listing_type = item.get('listing_type', '')
        if listing_type != 'property':
            skipped_type += 1
            continue

        prop = item.get('property')
        if not prop:
            skipped_empty += 1
            continue

        if not prop.get('id'):
            skipped_empty += 1
            continue

        price_val = (prop.get('price') or {}).get('value', 0)
        if not price_val or price_val <= 0:
            skipped_empty += 1
            continue

        try:
            parsed = parse_listing(prop)
        except Exception as e:
            print(f"   ⚠️ Parse error: {e}")
            skipped_empty += 1
            continue

        # فلتر 2: لو محدد governorate — نتأكد الإعلان فيها
        if expected_governorate:
            gov = parsed.get('governorate', '')
            if expected_governorate.lower() not in gov.lower():
                skipped_gov += 1
                continue

        listings.append(parsed)

    meta['_skipped_type'] = skipped_type
    meta['_skipped_empty'] = skipped_empty
    meta['_skipped_gov'] = skipped_gov

    return listings, meta


# ═══════════════════════════════════════════════════════
# SCRAPE WITH PAGINATION
# ═══════════════════════════════════════════════════════
def scrape_search(base_url, pages=5, verbose=True, expected_governorate=None):
    """Scrape multiple pages of a search URL.

    Args:
        base_url: PropertyFinder search URL (e.g., https://www.propertyfinder.eg/en/search?c=1&t=1)
        pages: number of pages to scrape
        verbose: print progress
        expected_governorate: if set, only keep listings in this governorate (case-insensitive)

    Returns:
        list of parsed listings (deduplicated, filtered by governorate)
    """
    all_listings = []
    seen_ids = set()

    for page in range(1, pages + 1):
        url = f"{base_url}&page={page}" if "?" in base_url else f"{base_url}?page={page}"

        if verbose:
            print(f"\n📄 Page {page}/{pages}: {url[:80]}")

        html = fetch_page(url)
        if not html:
            print(f"   ❌ Failed to fetch page {page}")
            continue

        listings, meta = extract_listings_from_page(html, expected_governorate=expected_governorate)

        # dedup بـ id
        new_count = 0
        dup_count = 0
        for item in listings:
            rid = item.get('id')
            if rid and rid not in seen_ids:
                seen_ids.add(rid)
                all_listings.append(item)
                new_count += 1
            else:
                dup_count += 1

        if verbose:
            total = meta.get('total_count', '?')
            skipped_type = meta.get('_skipped_type', 0)
            skipped_gov = meta.get('_skipped_gov', 0)
            print(f"   ✅ Got {new_count} new | {dup_count} dupes | "
                  f"{skipped_type} non-property | {skipped_gov} wrong-gov | total in site: {total}")

        # لو مفيش listings جديدة، نوقف
        if new_count == 0:
            if verbose:
                print(f"   ⏹️ No more new listings — stopping")
            break

    return all_listings


def save_listings(listings, output_path):
    """Save listings to CSV."""
    if not listings:
        print("⚠️ No listings to save")
        return

    df = pd.DataFrame(listings)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"✅ Saved {len(df)} listings to {output_path.name}")


# ═══════════════════════════════════════════════════════
# CITY MAPPING
# ═══════════════════════════════════════════════════════
CITY_CODES = {
    # 9 existing — مع governorate_name للفلترة
    "cairo":       {"c": 1,   "name_en": "Cairo",          "name_ar": "القاهرة",       "gov_filter": "Cairo"},
    "giza":        {"c": 2,   "name_en": "Giza",           "name_ar": "الجيزة",        "gov_filter": "Giza"},
    "alexandria":  {"c": 3,   "name_en": "Alexandria",     "name_ar": "الإسكندرية",    "gov_filter": "Alexandria"},
    "dakahlia":    {"c": 4,   "name_en": "Dakahlia",       "name_ar": "الدقهلية",      "gov_filter": "Dakahlia"},
    "red-sea":     {"c": 5,   "name_en": "Red Sea",        "name_ar": "البحر الأحمر",  "gov_filter": "Red Sea"},
    "sharqia":     {"c": 6,   "name_en": "Sharqia",        "name_ar": "الشرقية",       "gov_filter": "Sharqia"},
    "qalyubia":    {"c": 7,   "name_en": "Qalyubia",       "name_ar": "القليوبية",     "gov_filter": "Qalyubia"},
    "kafr-el-sheikh": {"c": 8, "name_en": "Kafr El Sheikh", "name_ar": "كفر الشيخ",    "gov_filter": "Kafr El Sheikh"},
    "gharbia":     {"c": 9,   "name_en": "Gharbia",        "name_ar": "الغربية",       "gov_filter": "Gharbia"},
    "monufia":     {"c": 10,  "name_en": "Monufia",        "name_ar": "المنوفية",      "gov_filter": "Monufia"},
    "beheira":     {"c": 11,  "name_en": "Beheira",        "name_ar": "البحيرة",       "gov_filter": "Beheira"},
    "ismailia":    {"c": 12,  "name_en": "Ismailia",       "name_ar": "الإسماعيلية",   "gov_filter": "Ismailia"},
    "damietta":    {"c": 13,  "name_en": "Damietta",       "name_ar": "دمياط",         "gov_filter": "Damietta"},
    "faiyum":      {"c": 14,  "name_en": "Faiyum",         "name_ar": "الفيوم",        "gov_filter": "Faiyum"},
    "beni-suef":   {"c": 15,  "name_en": "Beni Suef",      "name_ar": "بني سويف",      "gov_filter": "Beni Suef"},
    "minya":       {"c": 16,  "name_en": "Minya",          "name_ar": "المنيا",        "gov_filter": "Minya"},
    "asyut":       {"c": 17,  "name_en": "Asyut",          "name_ar": "أسيوط",         "gov_filter": "Asyut"},
    "sohag":       {"c": 18,  "name_en": "Sohag",          "name_ar": "سوهاج",         "gov_filter": "Sohag"},
    "qena":        {"c": 19,  "name_en": "Qena",           "name_ar": "قنا",           "gov_filter": "Qena"},
    "luxor":       {"c": 20,  "name_en": "Luxor",          "name_ar": "الأقصر",        "gov_filter": "Luxor"},
    "aswan":       {"c": 21,  "name_en": "Aswan",          "name_ar": "أسوان",         "gov_filter": "Aswan"},
    "suez":        {"c": 22,  "name_en": "Suez",           "name_ar": "السويس",        "gov_filter": "Suez"},
    "matrouh":     {"c": 23,  "name_en": "Matruh",         "name_ar": "مطروح",         "gov_filter": "Matruh"},
    "north-coast": {"c": 24,  "name_en": "North Coast",    "name_ar": "الساحل الشمالي","gov_filter": "Matruh"},
}


def get_search_url(city_key, property_type="1"):
    """Build PropertyFinder search URL for a city.

    Args:
        city_key: city key from CITY_CODES
        property_type: "1"=Apartment, "2"=Villa, etc.
    """
    info = CITY_CODES.get(city_key)
    if not info:
        raise ValueError(f"Unknown city: {city_key}")

    c = info["c"]
    return f"https://www.propertyfinder.eg/en/search?c={c}&t={property_type}&fu=0&ob=mr"
