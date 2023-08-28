import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
import pandas as pd


def get_row_data(info_str, ind_array):
    if info_str.isspace() or (info_str is None):
        return None
    ind = info_str.find('$')
    amount = info_str[ind+1:-1]
    last_name = clean_str(info_str[ind_array[0]:ind_array[1]])
    first_name = clean_str(info_str[ind_array[1]:ind_array[2]])
    position = clean_str(info_str[ind_array[2]:ind])
    compensation = float(amount.replace(" ", "").replace(',', ''))
    data_row = [last_name, first_name, position, compensation]
    # print(data_row)
    return data_row


def process_header(title_str, header_list):
    ind_array = []
    for item in header_list:
        ind = title_str.find(item)
        ind_array.append(ind)
    # print(ind_array)

    return ind_array


def clean_str(mystring):
    cleanstr = ' '.join(mystring.split())
    return cleanstr.rstrip()


def loop_over_lanes(pagestr):
    lines = pagestr.splitlines()

    trigger = False
    data_array = []
    for lanes in lines:
        my_str = lanes.lstrip() + ' '     # remove leading spaces

        if ('Page' in my_str) and ('of' in my_str):
            # reach to the end of the page, no need to record.
            trigger = False

        if trigger:
            row = get_row_data(my_str, ind_array)
            if row is not None:
                data_array.append(row)

        if 'Last Name' in my_str:
            ind_array = process_header(my_str, header_list)
            trigger = True

    return data_array


def get_headers(pagestr):

    headers = []
    return headers
