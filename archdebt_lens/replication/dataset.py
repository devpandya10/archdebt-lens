"""
Replication dataset from Sutoyo, Avgeriou, & Capiluppi (2025).
Contains empirical distributions and benchmark items from Zenodo 14697268.
"""

from typing import Dict, List, Optional

# Table III: Subset of Java Files from ATD #1 (Apache Camel, CAMEL-789, commit 77b260b6)
TABLE_III_CAMEL_DATA = [
    {
        "filename": "org/apache/camel/Endpoint.java",
        "intro_fan_in": 11,
        "intro_fan_out": 0,
        "pay_fan_in": 196,
        "pay_fan_out": 5,
        "removed": False,
    },
    {
        "filename": "org/apache/camel/RuntimeCamelException.java",
        "intro_fan_in": 2,
        "intro_fan_out": 0,
        "pay_fan_in": 66,
        "pay_fan_out": 0,
        "removed": False,
    },
    {
        "filename": "org/apache/camel/processor/SendProcessor.java",
        "intro_fan_in": 2,
        "intro_fan_out": 2,
        "pay_fan_in": 6,
        "pay_fan_out": 9,
        "removed": False,
    },
    {
        "filename": "org/apache/camel/builder/ChoiceBuilder.java",
        "intro_fan_in": 2,
        "intro_fan_out": 4,
        "pay_fan_in": None,
        "pay_fan_out": None,
        "removed": True,
    },
    {
        "filename": "org/apache/camel/builder/WhenBuilder.java",
        "intro_fan_in": 1,
        "intro_fan_out": 6,
        "pay_fan_in": None,
        "pay_fan_out": None,
        "removed": True,
    },
    {
        "filename": "org/apache/camel/builder/ToBuilder.java",
        "intro_fan_in": 10,
        "intro_fan_out": 5,
        "pay_fan_in": None,
        "pay_fan_out": None,
        "removed": True,
    },
]

# Statistical validation values for ATD #1 (Worked Example, Section IV)
WORKED_EXAMPLE_ATD1_STATS = {
    "fan_in_median_intro": 0.69,
    "fan_in_median_payment": 2.01,
    "fan_in_p_value": 0.0002,
    "fan_in_cliffs_delta": 0.5868,  # Large effect size (|d| >= 0.474)
    "fan_out_cliffs_delta": 0.1612, # Small effect size (0.147 <= |d| < 0.33)
    "fan_out_null_hypothesis_rejected": False,
}

# Table IV: Summary of FAN-IN and FAN-OUT Metric Changes (Complete Sample)
TABLE_IV_PAPER_SUMMARY = {
    "atd": {
        "files_count_intro": 5135,
        "files_count_payment": 3553,
        "file_reduction_pct": -44.5,
        "fan_in_avg_pct": 57.5,
        "fan_in_max_pct": 49.33,
        "fan_in_cliffs_delta": 0.1028,
        "fan_in_delta_magnitude": "negligible",
        "fan_in_p_value": 1.24e-16,
        "fan_out_avg_pct": 26.7,
        "fan_out_max_pct": 21.23,
        "fan_out_cliffs_delta": 0.1213,
        "fan_out_delta_magnitude": "negligible",
        "fan_out_p_value": 5.05e-22,
    },
    "non_atd": {
        "files_count_intro": 753,
        "files_count_payment": 593,
        "file_reduction_pct": -21.26,
        "fan_in_avg_pct": 89.06,
        "fan_in_max_pct": 86.32,
        "fan_in_cliffs_delta": 0.2766,
        "fan_in_delta_magnitude": "small",
        "fan_in_p_value": 4.78e-19,
        "fan_out_avg_pct": 36.18,
        "fan_out_max_pct": 3.87,
        "fan_out_cliffs_delta": 0.1805,
        "fan_out_delta_magnitude": "small",
        "fan_out_p_value": 7.49e-09,
    },
}

# Table V: Mann-Whitney U test p-values for Each ATD Item (Base and Normalized by SLOC)
# Format: (fan_in_sig_base, fan_in_sig_norm, fan_out_sig_base, fan_out_sig_norm)
TABLE_V_ATD_ITEMS = {
    "ATD #1":  {"fan_in": ("Y", "Y"), "fan_out": ("N", "N")},
    "ATD #2":  {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #3":  {"fan_in": ("-", "-"), "fan_out": ("-", "-")},  # only folders referenced
    "ATD #4":  {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #5":  {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #6":  {"fan_in": ("-", "-"), "fan_out": ("-", "-")},  # only folders referenced
    "ATD #7":  {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #8":  {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #9":  {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #10": {"fan_in": ("Y", "Y"), "fan_out": ("N", "N")},
    "ATD #11": {"fan_in": ("Y", "N"), "fan_out": ("N", "Y")},
    "ATD #12": {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #13": {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #14": {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #15": {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
    "ATD #16": {"fan_in": ("Y", "N"), "fan_out": ("Y", "N")},
    "ATD #17": {"fan_in": ("Y", "N"), "fan_out": ("Y", "N")},
    "ATD #18": {"fan_in": ("N", "N"), "fan_out": ("N", "N")},
}

# Table VI: Mann-Whitney U test p-values for Each Non-ATD Item
TABLE_VI_NON_ATD_ITEMS = {
    f"Non-ATD #{i}": {
        "fan_in": ("Y", "Y") if i in (14, 15) else ("N", "N"),
        "fan_out": ("Y", "N") if i in (14, 15) else ("N", "N"),
    }
    for i in range(1, 19)
}

# Table VII: Changes Statistic of ATD vs Non-ATD Files (Modification Frequency)
TABLE_VII_CHANGE_DISTRIBUTIONS = {
    "atd": {
        "n_files": 5135,
        "avg_change": 6.981,
        "median_change": 2.0,
        "min_change": 0,
        "max_change": 811,
        "std_dev": 20.935,
    },
    "non_atd": {
        "n_files": 753,
        "avg_change": 16.115,
        "median_change": 7.0,
        "min_change": 1,
        "max_change": 532,
        "std_dev": 30.320,
    },
}

# Table VIII: Partial Spearman Correlation Controlling for SLOC
TABLE_VIII_PARTIAL_CORRELATIONS = {
    "atd": {
        "fan_in": {"r": 0.241, "ci": (0.21, 0.27), "p_value": 0.001},
        "fan_out": {"r": 0.175, "ci": (0.14, 0.21), "p_value": 0.001},
        "complexity": {"r": -0.089, "ci": (-0.12, -0.06), "p_value": 0.001},
    },
    "non_atd": {
        "fan_in": {"r": 0.298, "ci": (0.22, 0.37), "p_value": 0.001},
        "fan_out": {"r": 0.533, "ci": (0.47, 0.59), "p_value": 0.001},
        "complexity": {"r": 0.313, "ci": (0.24, 0.38), "p_value": 0.001},
    },
}
