"""
Robust Average Package

A Python package that intelligently selects the most robust average 
(mean, median, or mode) for price analysis based on outlier and skewness detection.
"""

from .robust_average import robust_average

__version__ = "0.1.2"
__author__ = "Ben"
__email__ = "ben@example.com"

__all__ = ["robust_average"] 