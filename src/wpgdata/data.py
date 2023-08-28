import numpy as np
import urllib
import pathlib
import logging
import pdfplumber
from .utils import get_headers

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
        '''Get a dict of list with key = year.'''
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

    def pdf_to_str(self, fpath):
        data_whole = []
        with pdfplumber.open(fpath) as pdf:
            total_pages = len(pdf.pages)
            for n in np.arange(5, total_pages):
                # print(n)
                pagestr = pdf.pages[n].extract_text(layout=True, x_tolerance=1, x_density=3)
                print(pagestr)

                headers = get_headers(pagestr)
                print(f'headers={headers}')
                # sa = loop_over_lanes(pagestr)
                data_whole.append(pagestr)
        return data_whole

    def data_validator(self, type='PDF'):
        '''
        Check if raw data is downloaded or interpreted.

        Return: a boolean value.
            Ture: dataset is complete.
            False: dataset is not complete.
        '''
        result = True
        if self.data_save_path.exists():
            for year in self.__years__:
                for region in self.__regions__:
                    fn = self.pdf_filename(year=year, type='house', region=region)
                    if not (self.data_save_path / fn).exists():
                        logger.info(f'file {fn} missing!')
                        result = False
                fn = self.pdf_filename(year=year, type='condo', region=None)
                if not (self.data_save_path / fn).exists():
                    logger.info(f'file {fn} missing!')
                    result = False
        return result
