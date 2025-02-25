import requests
import lxml.etree as ET
from collections import defaultdict

BASE_URL = "https://www.ecfr.gov"

def fetch_agencies():
    """Fetch agencies from /api/admin/v1/agencies.json, including slugs."""
    url = f"{BASE_URL}/api/admin/v1/agencies.json"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["agencies"]

def fetch_titles_info():
    """Fetches the latest issue dates for all CFR Titles."""
    url = f"{BASE_URL}/api/versioner/v1/titles.json"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def find_latest_issue_date(titles_data, title_num):
    """Find the latest issue date for a given Title number."""
    for t in titles_data["titles"]:
        if str(t["number"]) == str(title_num):
            return t["latest_issue_date"]
    return None

def download_entire_title_xml(title_num, date_str):
    """Download the full XML for a given Title and date."""
    url = f"{BASE_URL}/api/versioner/v1/full/{date_str}/title-{title_num}.xml"
    resp = requests.get(url, headers={"Accept": "application/xml"})
    resp.raise_for_status()
    return resp.content

def extract_relevant_text_and_sections(root, ref):
    """
    Extracts text and counts sections using XPath to correctly locate elements regardless of nesting.
    """
    search_criteria = {
        "subtitle": "SUBTITLE",
        "chapter": "CHAPTER",
        "subchapter": "SUBCHAP",
        "part": "PART",
        "subpart": "SUBPART",
        "section": "SECTION"
    }

    hierarchy_trail = [key for key in ["subtitle", "chapter", "subchapter", "part", "subpart", "section"] if key in ref]

    if not hierarchy_trail:
        return "", 0  

    xpath_query = ".//"
    for level in hierarchy_trail:
        node_type = search_criteria[level]
        node_value = ref[level]
        xpath_query += f"*[@TYPE='{node_type}'][@N='{node_value}']/"

    xpath_query = xpath_query.rstrip("/")

    matching_nodes = root.findall(xpath_query)

    text_segments = []
    section_count = 0

    for node in matching_nodes:
        for elem in node.iter():
            if elem.text and elem.text.strip():
                text_segments.append(elem.text.strip())
            if elem.tail and elem.tail.strip():
                text_segments.append(elem.tail.strip())
            if elem.tag.startswith("DIV") and elem.attrib.get("TYPE") == "SECTION":
                section_count += 1

    return " ".join(text_segments), section_count
    
def count_words(text):
    """Counts words in the extracted text."""
    return len(text.split())

def compute_agency_word_and_section_count(agency, titles_data, title_xml_cache):
    """Computes word and section count for agencies, ensuring we follow the hierarchy trail."""
    results = {
        "slug": agency["slug"], 
        "total_words": 0,
        "total_sections": 0,
        "children": {}
    }

    references = list(agency.get("cfr_references", []))

    for child in agency.get("children", []):
        child_name = child["name"]
        child_refs = child.get("cfr_references", [])

        child_words, child_sections = compute_references_word_and_section_count(child_refs, titles_data, title_xml_cache)
        results["children"][child_name] = {
            "slug": child["slug"],
            "words": child_words,
            "sections": child_sections
        }
        results["total_words"] += child_words
        results["total_sections"] += child_sections

    agency_words, agency_sections = compute_references_word_and_section_count(references, titles_data, title_xml_cache)
    results["total_words"] += agency_words
    results["total_sections"] += agency_sections

    return results

def compute_references_word_and_section_count(references, titles_data, title_xml_cache):
    """Computes word and section count while following the hierarchy trail using XPath."""
    total_words = 0
    total_sections = 0
    refs_by_title = defaultdict(list)

    for ref in references:
        refs_by_title[ref["title"]].append(ref)

    for title_num, ref_list in refs_by_title.items():
        latest_date = find_latest_issue_date(titles_data, title_num)
        if not latest_date:
            continue

        cache_key = (title_num, latest_date)
        if cache_key not in title_xml_cache:
            xml_bytes = download_entire_title_xml(title_num, latest_date)
            root = ET.fromstring(xml_bytes) 
            title_xml_cache[cache_key] = root
        else:
            root = title_xml_cache[cache_key]

        for ref in ref_list:
            extracted_text, section_count = extract_relevant_text_and_sections(root, ref)
            total_words += count_words(extracted_text)
            total_sections += section_count

    return total_words, total_sections

def fetch_corrections():
    """Fetch all eCFR corrections from the API."""
    url = f"{BASE_URL}/api/admin/v1/corrections.json"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["ecfr_corrections"]

def count_corrections_by_year():
    """Counts the number of corrections per year."""
    corrections = fetch_corrections()
    corrections_by_year = defaultdict(int)

    for correction in corrections:
        year = correction["year"]
        corrections_by_year[year] += 1

    return dict(sorted(corrections_by_year.items()))

def process_agency_data():
    """Process and return agency data with word and section counts."""
    agencies = fetch_agencies()
    titles_data = fetch_titles_info()
    title_xml_cache = {}

    results = {}
    for ag in agencies:
        ag_name = ag["name"]
        word_section_data = compute_agency_word_and_section_count(ag, titles_data, title_xml_cache)
        results[ag_name] = word_section_data
        print(ag_name)
    return results

def process_corrections_data():
    """Process and return corrections data by year."""
    return count_corrections_by_year()

