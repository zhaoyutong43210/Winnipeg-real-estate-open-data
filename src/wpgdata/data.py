import numpy as np
import urllib
import pathlib
import logging
import pdfplumber
import re 
import pandas as pd

from .utils import loop_over_lanes, clean_str, flatten_list

logging.basicConfig(format=' %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class wpgdata_cfg():
    '''The configurator for Winnipeg Real Estate data.'''
    __years__ = [2012, 2014, 2016, 2018, 2021]  # The years that release the salebooks.
    __regions__ = np.arange(1, 11)              # The salebooks in different regions.
    __typedict__ = {'house': 'market_region_', 'condo': 'condominium'}

    def __init__(self):

        self.data_save_path = pathlib.Path().absolute().parents[1] / "Winnipeg_real_estate_open_data"
        # self.data_auto_load()

    def auto_download(self):
        '''Download all (PDF) files needed.'''
        file_dict = self.full_salebooks_urls()

        for key in file_dict:
            file_list = file_dict[key]
            for file in file_list:
                self._download_file(file, save_sub_path=str(key))

    def full_salebooks_urls(self):
        '''Get the urls of salebooks in format of dict of list with key = year.'''
        result = {}
        for year in self.__years__:
            url_list = []
            for region in self.__regions__:
                bookurl = self.url_gen(type='house', year=year, region=region)
                url_list.append(bookurl)
            bookurl = self.url_gen(type='condo', year=year, region=region)
            url_list.append(bookurl)
            result.update({year: url_list})
        return result
    
    def full_salebooks_paths(self):
        '''Get a local path  of salebooks in format of list with key = year.'''
        result = {}
        for year in self.__years__:
            path_list = []
            for region in self.__regions__:
                fn = self.pdf_filename(year=year, type='house', region=region)
                path_list.append(fn)
            fn = self.pdf_filename(type='condo', year=year, region=region)
            path_list.append(fn)
            result.update({year: path_list})
        return result

    def url_gen(self, type='house', year=2012, region=1):
        '''
        Generate the full url of the required.

        This function is subject to change over time, depends on the winnipeg city website.
        '''
        extention = '.pdf'
        base_url = 'https://assessment.winnipeg.ca/AsmtTax/pdfs/SelfService/'
        key_word = 'sales_book_'

        # Wired URL but it is the real world
        if year == 2018:
            yearurl = ''
        else:
            yearurl = str(year) + '/'

        if type == 'house':
            file_path = urllib.parse.urljoin(yearurl, key_word + self.__typedict__[type] + str(region) + extention)
        elif type == 'condo':
            file_path = urllib.parse.urljoin(yearurl, key_word + self.__typedict__[type] + extention)
        file_url = urllib.parse.urljoin(base_url, str(file_path))
        return file_url

    def pdf_filename(self, year=2012, type='house', region=1):
        if type == 'house':
            regionstr = str(region)
        elif type == 'condo':
            regionstr = ''
        file_name = 'sales_book_' + self.__typedict__[type] + regionstr + '.pdf'
        file_path = pathlib.Path(str(year)) / str(file_name)
        return file_path

    def _download_file(self, file_url, file_name=None, save_sub_path=None):
        '''Download a single file'''

        if file_name is None:
            file_name = file_url.rsplit('/', 1)[-1]

        if self.data_save_path is not None:
            fn = self.data_save_path / save_sub_path / file_name

        pathlib.Path(self.data_save_path / save_sub_path).mkdir(parents=True, exist_ok=True)

        if fn.exists():
            logger.info(f'The file {fn} already exists, skip downloading!')
        else:
            try:
                (filename, headers) = urllib.request.urlretrieve(file_url, fn)
                logger.info(f'Successfully downloaded: {fn}.')
                return filename, headers
            except urllib.error.URLError as e:
                raise RuntimeError("Failed to download '{}'. '{}'".format(file_url, e.reason))

    def _test_url(self, url):
        result = urllib.parse.urlparse(url)
        return result

    def pdf_to_datafram(self, fpath):
        salebook_data = []
        with pdfplumber.open(fpath) as pdf:
            total_pages = len(pdf.pages)
            for n in np.arange(5, total_pages):
                pagestr = pdf.pages[n].extract_text(layout=True, x_tolerance=1, x_density=3)
                page_data = loop_over_lanes(pagestr, self._headerinfo)
                salebook_data.append(page_data)
        return  pd.DataFrame(flatten_list(salebook_data), columns = self._headers)
    
    def get_headers(self, fpath, page=6):
        self._headers = None
        with pdfplumber.open(fpath) as pdf:
            pagestr = pdf.pages[page].extract_text(layout=True, x_tolerance=1, x_density=3)
            self._headerinfo = self._search_headers(pagestr)
            self._clean_header()

        self._headers = []
        for i in self._headerinfo:
            self._headers.append(clean_str(i[2]))
    
    def _search_headers(self, pagestr):
        headers = []
        inds = []
        inde = []
        lanes = []
        lines = pagestr.splitlines()
        for lanestr in lines:
            if 'Price' in lanestr  and 'Sale' in lanestr and 'this' not in lanestr:
                head =  [n.lstrip() for n in lanestr.split('     ')] 
                head = list(filter(None,head))
                for h in head: 
                    ind_start = [m.start() for m in re.finditer(h, lanestr)][0]
                    ind_end = [m.end() for m in re.finditer(h, lanestr)][0]
                    inds.append(ind_start)
                    inde.append(ind_end)
                for i in head:                    
                    headers.append(i)
                lanes.append(lanestr)

        # post process
        result = []
        headers = headers
        for n, item in enumerate(inds):
            result.append([inds[n],inde[n],headers[n]])
        return result
    
    def _clean_header(self):
        # clean duplicated headers
        start_i = []
        end_i = []
        for i in self._headerinfo:
            start_i.append(i[0])
            end_i.append(i[1])
            if ((i[0] > np.array(start_i)) & (i[0] < np.array(end_i))).any():
                self._headerinfo.remove(i)
        self._headerinfo.sort()

    def data_validator(self, type='PDF'):
        '''
        Check if raw data is downloaded or interpreted.

        Return: a boolean value.
            Ture: dataset is complete.
            False: dataset is not complete.
        '''
        result = True
        file_dict = self.full_salebooks_paths()
        for key in file_dict:
            file_list = file_dict[key]
            for file in file_list:
                if not (self.data_save_path / file).exists():
                        logger.info(f'file {file} missing!')
                        result = False
        return result
