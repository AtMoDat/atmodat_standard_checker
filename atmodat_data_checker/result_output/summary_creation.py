"""module to create summary of results from atmodat data checker"""

import os
import pandas as pd
import numpy as np
import json

import atmodat_data_checker.result_output.output_directory as output_directory


def delete_file(file):
    """deletes given file"""
    os.remove(output_directory.opath + file)


def extract_from_nested_json(obj, key):
    """Recursively fetch values from nested json file."""
    array = []

    def extract(obj, array, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    array.append(v)
                elif isinstance(v, (dict, list)):
                    extract(v, array, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, array, key)
        return array

    values = extract(obj, array, key)
    return values


def extract_overview_output_json(ifile_in):
    """extracts information from given json file and returns them as a dictionary"""
        
    with open(output_directory.opath + ifile_in) as f:
        data = json.load(f)

        summary_keys = ['data_file','check_type','scored_points','possible_points', 'msgs']
        summary = {key: None for key in summary_keys}

        for key, value in data.items():
                summary[summary_keys[0]] = key
                for sub_key, sub_value in value.items():
                    summary[summary_keys[1]] = sub_key.split("_")[-1].split(':')[0]

        summary[summary_keys[2]] = extract_from_nested_json(data,summary_keys[2])[0]
        summary[summary_keys[3]] = extract_from_nested_json(data,summary_keys[3])[0]

        if summary[summary_keys[2]] != summary[summary_keys[3]]:
            summary[summary_keys[4]] = extract_from_nested_json(data,summary_keys[4])
            # remove empty lists
            summary[summary_keys[4]] = [x for x in summary[summary_keys[4]] if x != []]
            # make lists into strings 
            summary[summary_keys[4]] = [x[0] for x in summary[summary_keys[4]]]
            summary[summary_keys[4]] = ', '.join([str(elem) for elem in summary[summary_keys[4]]]) 
            # remove "'" from strings
            summary[summary_keys[4]] = summary[summary_keys[4]].replace("'", "")
        else:
            # delete file if nor errors occured
            delete_file(ifile_in)

    return summary


def extracts_error_summary_cf_check(ifile_in):
    """extracts information from given txt file and returns them as a string"""
    substr = 'ERRORS detected:'
    with open(output_directory.opath + ifile_in) as f:
        data = f.read()
        for line in data.strip().split('\n'):
            if substr in line:
                return line.split(':')[-1].strip()


def write_short_summary(json_summary, cf_errors):
    scored_points = [str(int(json_summary['scored_points'].sum()))]
    possible_points = [str(int(json_summary['possible_points'].sum()))]

    check_types = ["mandatory", "recommended", "optional"]

    # Write summary of results into summary file 
    with open(output_directory.opath + 'short_summary.txt', 'w+') as f:
        f.write("This is a short summary of the results from the atmodat data checker. \n")
        f.write("Version of the checker: " + str(1.0) + "\n \n")
        f.write("Total scored points: " + scored_points[0] + '/' + possible_points[0] + '\n')

        for index, check in enumerate(check_types):
            scored_points.append(str(
                int(json_summary['scored_points'].loc[json_summary['check_type'] == check].sum())))
            possible_points.append(str(int(
                json_summary['possible_points'].loc[json_summary['check_type'] == check].sum())))
            f.write("Total scored " + check + " points: " + scored_points[index + 1] + '/' +
                    possible_points[index + 1] + '\n')

        f.write("Total number CF checker errors: " + str(cf_errors))


def write_detailed_json_summary(json_summary):
    # Write summary of results into summary file 
    with open(output_directory.opath + 'detailed_summary.csv', 'w+') as f:
        f.write("This is a detailed summary of the results from the atmodat data checker. \n")
        f.write("Version of the checker: " + str(1.0) + "\n \n")
        json_summary.to_csv (f, index = False, header=True)



def create_output_summary():
    json_summary = pd.DataFrame()
    cf_errors = 0
    for file in os.listdir(output_directory.opath):
        if file.endswith("_result.json"):
            json_summary = json_summary.append(extract_overview_output_json(file),
                                               ignore_index=True)
        elif file.endswith("_cfchecks_result.txt"):
            cf_errors = cf_errors + int(extracts_error_summary_cf_check(file))

    write_short_summary(json_summary, cf_errors)
    write_detailed_json_summary(json_summary)