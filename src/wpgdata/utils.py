# import numpy as np
# import pandas as pd


def clean_str(mystring):
    '''multiple white space to one.'''
    cleanstr = ' '.join(mystring.split())
    return cleanstr.strip()


def loop_over_lanes(pagestr, header_info, trigger_str, method=1):
    lines = pagestr.splitlines()
    if trigger_str is not None:
        trigger_start = trigger_str[0]
        trigger_end = trigger_str[1]
    else:
        trigger_start = ['Adresse', 'rôle']
        trigger_end = ['Page', 'of']
    # logger.debug(trigger_start, trigger_end)
    trigger = False
    data_array = []
    for lane in lines:
        if all([s in lane for s in trigger_end]):
            # reach to the end of the page, no need to record.
            trigger = False

        if trigger:
            if method == 1:
                row = get_row_data(lane, header_info)
            elif method == 2:
                row = get_row_data_simple(lane)
            if row is not None:
                data_array.append(row)

        if all([s in lane for s in trigger_start]):
            # reach to the start of the page, record begin from the next lane.
            trigger = True

    return data_array


def get_row_data(lane_str, header_info):
    data_row = []
    ind_break = []

    for i in header_info:
        ind_break.append(i[0])
    ind_break.append(i[1])
    ind_break[0] = 0
    ind_break[-1] = ind_break[-1] + 2
    #
    for n, i in enumerate(header_info):
        # loop over headers
        data_str = lane_str[ind_break[n]:ind_break[n+1]].strip()
        data_row.append(clean_str(data_str))

    if '' in data_row:
        return data_row.remove("")
    else:
        return data_row


def get_row_data_simple(lane_str):
    data_row = [clean_str(n) for n in lane_str.split('           ')]

    if '' in data_row:
        return list(filter(lambda a: a != '', data_row))
    else:
        return data_row


def flatten_list(mylist):
    return [item for sublist in mylist for item in sublist]
