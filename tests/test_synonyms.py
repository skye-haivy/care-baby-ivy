import pytest

# Adjust import if your module path differs
from app.services.synonyms import canonicalize, normalize

# --- Positive mappings (input -> expected canonical slug)
CASES_POSITIVE = [
    ("Sleep Training", "topic_sleep"),
    ("sleep", "topic_sleep"),
    ("Nap", "topic_naps"),
    ("short naps", "topic_naps"),
    ("Feeding", "topic_feeding"),
    ("Bottle", "topic_feeding"),
    ("Breastfeeding", "topic_feeding"),
    ("Formula", "topic_feeding"),
    ("Weaning", "topic_weaning"),
    ("Solids", "topic_weaning"),
    ("BLW", "pref_blw"),
    ("Baby led weaning", "pref_blw"),
    ("Allergy", "topic_allergies"),
    ("Allergies", "topic_allergies"),
    ("Peanut", "allergy_peanut"),
    ("Peanut intro", "allergy_peanut"),
    ("Egg", "allergy_egg"),
    ("Cow milk", "allergy_milk"),
    ("Dairy", "allergy_milk"),
    ("Eczema", "cond_eczema"),
    ("Atopic dermatitis", "cond_eczema"),
    ("Reflux", "cond_gerd"),
    ("GERD", "cond_gerd"),
    ("Asthma", "cond_asthma"),
    ("RSV", "cond_rsv"),
    ("Fever", "cond_fever"),
    ("Vaccine", "topic_vaccines"),
    ("Vaccination", "topic_vaccines"),
    ("Shots", "topic_vaccines"),
    ("Development", "topic_development"),
    ("Milestones", "topic_development"),
    ("Tantrum", "topic_behavior"),
    ("Tantrums", "topic_behavior"),
    ("Screen time", "topic_screen_time"),
    ("Tablet", "topic_screen_time"),
    ("Nutrition", "topic_nutrition"),
    ("Iron", "topic_nutrition"),
    ("Vitamin D", "topic_nutrition"),
]

@pytest.mark.parametrize("inp,expected", CASES_POSITIVE)
def test_canonicalize_positive(inp, expected):
    assert canonicalize(inp) == expected


# --- Normalization stress tests (spaces/case/gremlins)
CASES_NORMALIZE = [
    ("  Sleep   Training  ", "sleep training"),
    ("\tVitamin   D\n", "vitamin d"),
    ("  COW   MILK  ", "cow milk"),
    ("  \t  naps \n", "naps"),
]

@pytest.mark.parametrize("raw,normalized", CASES_NORMALIZE)
def test_normalize_behavior(raw, normalized):
    assert normalize(raw) == normalized


# --- Negative/edge cases should return None
CASES_NEGATIVE = [
    ("", None),
    ("   ", None),
    ("Unicorn allergy", None),
    ("Quantum physics for toddlers", None),
]

@pytest.mark.parametrize("inp,expected", CASES_NEGATIVE)
def test_canonicalize_negative(inp, expected):
    assert canonicalize(inp) is expected
