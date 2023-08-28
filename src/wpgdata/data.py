import numpy as np
import urllib
import pathlib

class wpgdata_cfg():
    '''The configurator for Winnipeg Real Estate data.'''
    def __init__(self):

        self.data_save_path = pathlib.Path().absolute() / "Winnipeg_real_estate_open_data"
        self.data_auto_load()

    def auto_download(self):
        '''Download all file needed.'''
        file_dict = self.full_all_urls()

        for key in file_dict:
            file_list = file_dict[key]
            for file in file_list:
                self._download_file(file, save_sub_path = str(key))

    def full_all_urls(self):
        '''Get a dict of list with key = year.'''
        result = {}
        years = [2012, 2014, 2016, 2018, 2021]
        regions = np.arange(1,11)
        for year in years:
            url_list =[]
            for region in regions:
                bookurl = self.url_gen(type='house', year=year, region=region)
                url_list.append(bookurl)
            bookurl = self.url_gen(type='condo', year=year, region=region)
            url_list.append(bookurl)
            result.update({year: url_list})
        return result
    
    def url_gen(self, type='house', year=2012, region=1):
        '''
        Generate the full url of the required.
        
        This function is subject to change over time, depends on the winnipeg city website.
        '''

        typedict = {'house' : 'market_region_', 'condo' : 'condominium'}
        extention = '.pdf'
        base_url = 'https://assessment.winnipeg.ca/AsmtTax/pdfs/SelfService/'
        key_word= 'sales_book_'

        if year == 2018:
            yearurl = ''
        else:
            yearurl = str(year) + '/'

        if type == 'house':
            file_url = urllib.parse.urljoin(yearurl, key_word + typedict[type] + str(region) + extention)
        elif type == 'condo':
            file_url = urllib.parse.urljoin(yearurl, key_word + typedict[type] + extention)
        file_full_url = urllib.parse.urljoin(base_url, str(file_url))
        return file_full_url
    
    def _download_file(self, file_url, file_name=None, save_sub_path=None):
        '''Download a single file'''

        if file_name is None:
            file_name = file_url.rsplit('/', 1)[-1]

        if self.data_save_path is not None:
            fn = self.data_save_path / save_sub_path / file_name
        
        pathlib.Path(self.data_save_path / save_sub_path).mkdir(parents=True, exist_ok=True)
        
        if fn.exists():
            print(f'The file {fn} already exists, skip downloading!')
        else:

            try:
                (filename, headers) = urllib.request.urlretrieve(file_url, fn)
                return filename, headers
            except URLError as e:
                raise RuntimeError("Failed to download '{}'. '{}'".format(file_url, e.reason))
        
    def _test_url(self, url):
        result = urllib.parse.urlparse(url)
        return result

    def data_auto_load(self):
        '''Check if raw data is downloaded, auto load if found.'''
        pass

    def data_validator(self):
        '''Check if raw data is downloaded, auto load if found.'''
        pass
