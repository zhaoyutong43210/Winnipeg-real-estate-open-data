import numpy as np
import pandas as pd


def clean_str(mystring):
    '''multiple white space to one.'''
    cleanstr = ' '.join(mystring.split())
    return cleanstr.strip()

def loop_over_lanes(pagestr, header_info):
    lines = pagestr.splitlines()

    trigger = False
    data_array = []
    for lane in lines:
        if ('Page' in lane) and ('of' in lane):
            # reach to the end of the page, no need to record.
            trigger = False

        if trigger:
            row = get_row_data(lane, header_info)
            if row is not None:
                data_array.append(row)

        if ('Adresse' in lane) and ('rôle' in lane):
            # reach to the start of the page, record the record begin.
            trigger = True

    return data_array


def get_row_data(lane_str, header_info):
    data_row = []
    ind_break = []
    
    for i in header_info:
        ind_break.append(i[0])
    ind_break.append(i[1])

    # 
    for n, i in enumerate(header_info):
        # loop over headers
        data_str = lane_str[ind_break[n]:ind_break[n+1]-1].strip()
        data_row.append(clean_str(data_str))
    
    if '' in data_row:
        return data_row.remove("")
    else:
        return data_row
    

def flatten_list(mylist):
    return [item for sublist in mylist for item in sublist]
