from mappings import *
import numpy as np
import pandas as pd
from collections import Counter
import re
import os
from dotenv import load_dotenv
import requests
import json
load_dotenv()
api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")   # get Google Translate API key from .env file

def translate_text(text, target_language="en", api_key=api_key):
    """
    Translates text from a source language to a target language using the Google Translate API.
    """
    url = "https://translation.googleapis.com/language/translate/v2"

    payload = {
        "q": text,
        "source": "de",
        "target": target_language,
        "key": api_key,
    }

    response = requests.post(url, params=payload)
    result = json.loads(response.text)

    if response.status_code == 200:
        translated_text = result["data"]["translations"][0]["translatedText"]
        return translated_text
    else:
        print("Error:", result)
        return None

def clean_employee_data(x):
    """Convert employee data to integer."""
    x = str(x).replace(",", "")
    if x == "n.a.":
        return np.nan
    return int(x)

def preprocess_company_name(name):
    """Preprocesses a company name for matching with the other dataset."""
    name = re.sub(r"[^a-zA-Z0-9\s&]", "", name)     # remove special characters
    name = re.sub(r"\s+", " ", name)                # replace multiple spaces with a single space
    name = name.lower().strip()                     # convert to lowercase and strip whitespace
    return name

def match_firms(orbis, kununu, matched_ids, edit_fn, fn_name):
    """
    Matches remaining firms from Orbis and Kununu based on company name
    based on the edit function and returns the updated datasets and matched ids.

    Parameters:
    orbis (pd.DataFrame): Orbis data
    kununu (pd.DataFrame): Kununu data
    matched_ids (list): List of ids that have already been matched
    edit_fn (function): Function to edit company names
    fn_name (str): Name of the function used for matching

    Returns:
    tuple: Updated Orbis data, updated Kununu data, matched data, updated matched ids
    """
    # remove firms that have already been matched
    orbis = orbis[~orbis["id"].isin(matched_ids)]
    kununu = kununu[~kununu["kununu_id"].isin(matched_ids)]

    # change names accordingly (e.g. remove abbreviations)
    orbis.loc[:, "orbis_name"] = orbis["orbis_name"].apply(edit_fn)
    kununu.loc[:, "kununu_name"] = kununu["kununu_name"].apply(edit_fn)

    # drop duplicates (recall rows are ordered by descending number of reviews)
    orbis = orbis.drop_duplicates(subset="orbis_name", keep="first")
    kununu = kununu.drop_duplicates(subset="kununu_name", keep="first")

    # merge Orbis and Kununu data
    matched_firms = orbis.merge(
        kununu, left_on="orbis_name", right_on="kununu_name", how="inner"
    )

    # add column to indicate which matching function was used
    matched_firms.loc[:, "match_type"] = fn_name
    
    print(f"Number of matches after applying {fn_name}: " + str(matched_firms.shape[0]))
    return (
        orbis,
        kununu,
        matched_firms,
        matched_firms["id"].tolist() + matched_firms["kununu_id"].tolist() + matched_ids,
)

def match_firms_in_sequence(orbis, kununu, steps):
    """
    Matches firms from two datasets (orbis and kununu) by applying a series of 
    transformation functions to the company names. The function runs each 
    transformation in sequence, collects the matched results, and returns all 
    matches combined.

    Parameters:
    - orbis (pd.DataFrame): The Orbis dataset containing company information.
    - kununu (pd.DataFrame): The Kununu dataset containing company information.
    - steps (list of tuples): A list of tuples where each tuple consists of a 
      transformation function and a corresponding label string. The function is 
      applied to the company names during the matching process.

    Returns:
    - orbis (pd.DataFrame): The modified Orbis dataset after all transformations.
    - kununu (pd.DataFrame): The modified Kununu dataset after all transformations.
    - all_matches (pd.DataFrame): A DataFrame containing all matched firms from 
      the sequence of transformations.
    """
    all_matches = []
    matched_ids = []
    num_initial_kununu_firms = kununu.shape[0]
    
    for func, label in steps:
        orbis, kununu, matches, matched_ids = match_firms(
            orbis, kununu, matched_ids, func, label
        )
        all_matches.append(matches)
    
    # Concatenate all match results
    all_matches = pd.concat(all_matches)
    print(f'Matched {100 * all_matches.shape[0] / num_initial_kununu_firms:.2f}% of Kununu firms.')
    return orbis, kununu, all_matches

def standardize_abbreviations(name):
    """Standardize abbreviations in company name by replacing full forms with abbreviations."""
    for key, value in abbreviation_map.items():  
        name = name.replace(key, value)
    return name

def umlauts_to_english(name):
    """Replace umlauts with their respective vowels."""
    return (
        name.replace("ae", "a")
        .replace("oe", "o")
        .replace("ue", "u")
        .replace("ss", "s")
        .replace("&", "und")
        .replace("ä", "a")
        .replace("ö", "o")
        .replace("ü", "u")
        .replace("ß", "ss")
    )

def remove_suffixes(name):
    """Remove abbreviations from company name if abbreviation is at the end of the name."""
    for abb in abbreviations:
        if name.endswith(abb):
            name = name.replace(abb, "").strip()
            break
    return name

def remove_words_from_name(name, common_words):
    """Remove words from company name."""
    name = name.split()
    name = [x for x in name if x not in common_words]
    return " ".join(name)

def get_word_frequencies(names):
    """Get word frequencies from a list of names."""
    word_counts = list(
        pd.Series(names)
        .drop_duplicates(keep="first")
        .str.split(expand=True)
        .stack()
    )
    return Counter(word_counts)

def get_most_common_words(names, pctile=99):
    """Get words that appear more commonly than 'pctile' percentage of all words."""
    word_counts = get_word_frequencies(names)
    pctile_99_frequency = int(np.percentile(list(word_counts.values()), 99))
    common_words = [word for word, count in word_counts.items() if count > pctile_99_frequency]
    return common_words