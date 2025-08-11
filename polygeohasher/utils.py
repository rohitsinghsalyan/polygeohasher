#!/usr/bin/python
"""
Utility functions and constants for polygeohasher package.

This module contains the core optimization algorithm and shared constants
used throughout the package.
"""

from typing import List, Union, Set

# Base32 character set used for geohash encoding
BASE32 = list("0123456789bcdefghjkmnpqrstuvwxyz")


def get_optimized_geohashes(
    geohashes: List[str], 
    largest_gh_size: int, 
    smallest_gh_size: int, 
    gh_input_level: int, 
    percentage_error: float = 10, 
    forced_gh_upscale: bool = False
) -> Union[List[str], bool]:
    """
    Optimize a list of geohashes by combining adjacent geohashes into larger ones
    when possible, reducing the total number of geohashes needed to cover an area.
    
    Args:
        geohashes (list): List of geohash strings to optimize
        largest_gh_size (int): Maximum geohash precision level (minimum string length)
        smallest_gh_size (int): Minimum geohash precision level (maximum string length)
        gh_input_level (int): Input geohash precision level
        percentage_error (float, optional): Allowed error percentage for optimization. Defaults to 10.
        forced_gh_upscale (bool, optional): Force upscaling to smallest_gh_size. Defaults to False.
    
    Returns:
        list: Optimized list of geohash strings
        
    Note:
        - larger gh_size means shorter geohash strings (less precise, covers larger area)
        - smaller gh_size means longer geohash strings (more precise, covers smaller area)
    """
    geohashes_set: Set[str] = set(geohashes)
    geohash_processed_check: Set[str] = set()
    processed_geohash_set: Set[str] = set()
    flag = True  # setting the flag True to initiate the optimisation
    
    if len(geohashes) == 0:  # if empty list of geohash is supplied return False
        return False
        
    len_desired_reached = False  # Indicator for length of desired geohash level reached or not, set to False to start optimisation
    no_of_cycle = 0  # number of cycles to reach desired geohash level
    
    if smallest_gh_size < gh_input_level:
        cutoff = (gh_input_level - smallest_gh_size) + (
            smallest_gh_size - largest_gh_size
        )
    else:
        cutoff = smallest_gh_size - largest_gh_size
        
    while flag == True:
        processed_geohash_set.clear()
        geohash_processed_check.clear()
        geohashes_set = set(geohashes_set)
        len_desired = largest_gh_size
        
        for geohash in geohashes_set:
            geohash_length = len(geohash)
            if geohash_length == len_desired or len_desired_reached == True:
                len_desired_reached = True
            else:
                len_desired_reached = False
                
            # cut short geohash only if the string length is greater than largest geohash size (smaller in string length)
            if geohash_length >= largest_gh_size:
                # substring value to generate all combination of child geohashes
                geohash_1up = geohash[:-1]
                # If a geohash has been processed, skip it.
                if (geohash_1up not in geohash_processed_check) and (
                    geohash not in geohash_processed_check
                ):
                    # Generating combinations
                    combinations = set([geohash_1up + i for i in BASE32])
                    # intersections of ideal vs real geohash childs in a parent geohash
                    intersect = combinations.intersection(geohashes_set)
                    # condition to process the geohash and add to processed list
                    if combinations.issubset(geohashes_set) or (
                        len(intersect) >= 32 * (1 - percentage_error / 100)
                        and no_of_cycle < 1
                    ):
                        # add to processed geohash list
                        processed_geohash_set.add(geohash_1up)
                        # check list for processes geohash
                        geohash_processed_check.add(geohash_1up)
                    else:
                        # if not add it to processes list anyway
                        geohash_processed_check.add(geohash)
                        # if forced optimisation is required
                        if (
                            geohash_length >= smallest_gh_size
                            and forced_gh_upscale == True
                        ):
                            processed_geohash_set.add(geohash[:smallest_gh_size])
                        else:
                            processed_geohash_set.add(geohash)
                            
        no_of_cycle = no_of_cycle + 1
        if len_desired_reached == True or no_of_cycle >= (cutoff):
            flag = False
        geohashes_set.clear()
        geohashes_set = geohashes_set.union(processed_geohash_set)  # adding the processed list
        
    final_geohashes = list(set(geohashes_set))
    return final_geohashes  # returning final geohash list