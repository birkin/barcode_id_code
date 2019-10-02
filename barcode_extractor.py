""" Extracts barcodes. """

import json, logging, os, pprint, time

import requests


logging.basicConfig(
    # filename=os.environ['zzz'],
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    )
log = logging.getLogger(__name__)
log.debug( 'log configured' )




def make_file_list():
    """ Makes json-list file of log-files in directory. """
    SOURCE_DIR_PATH = os.environ['TEMP__DIR_SOURCE']
    SOURCE_FILES_JSON_FILEPATH = os.environ['TEMP__SOURCE_FILES_JSON_FILEPATH']
    file_list = []
    for file_name in os.listdir( SOURCE_DIR_PATH ):
        if '.log' in file_name:
            file_path = f'{SOURCE_DIR_PATH}/{file_name}'
            file_list.append( file_path )
    file_list.sort()
    log.debug( f'file_list, ```{pprint.pformat(file_list)}```' )
    with open( SOURCE_FILES_JSON_FILEPATH, 'w' ) as f:
        data = json.dumps( file_list, sort_keys=True, indent=2 )
        f.write( data )
    log.debug( f'file_written to, ```{SOURCE_FILES_JSON_FILEPATH}```' )
    return file_list


def process_files():
    """ Loops through files, calling barcode-extractor. """
    SOURCE_FILES_JSON_FILEPATH = os.environ['TEMP__SOURCE_FILES_JSON_FILEPATH']
    with open( SOURCE_FILES_JSON_FILEPATH, 'r' ) as f:
        filepath_list = json.loads( f.read() )
    for log_filepath in filepath_list:
        extract_barcodes_from_file( log_filepath )
    log.debug( 'done' )
    return


def extract_barcodes_from_file( log_filepath ):
    """ Creates list of barcodes extracted from the log file. """
    BARCODE_LIST_JSON_FILEPATH = os.environ['TEMP__BARCODE_LIST_JSON_FILEPATH']
    with open( BARCODE_LIST_JSON_FILEPATH, 'r' ) as f:
        j_string = f.read()
    barcode_list = json.loads( j_string )
    log.debug( f'len(barcode_list) initially, `{len(barcode_list)}`' )
    with open( log_filepath, 'r' ) as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith( " 'patron_barcode': '" ):
            sierra_patron_id = line[20:34]
            log.debug( f'sierra_patron_id, `{sierra_patron_id}`' )
            if sierra_patron_id not in barcode_list:
                barcode_list.append( sierra_patron_id )
    barcode_list.sort()
    log.debug( f'len(barcode_list) after file-processing, `{len(barcode_list)}`' )
    data = json.dumps( barcode_list, sort_keys=True, indent=2 )
    with open( BARCODE_LIST_JSON_FILEPATH, 'w' ) as f:
        f.write( data )
    return


def convert_ids_from_barcodes():
    PBARCODE_ID_DCT_JSON_FILEPATH = os.environ['TEMP__PBARCODE_ID_DCT_JSON_FILEPATH']
    BARCODE_LIST_JSON_FILEPATH = os.environ['TEMP__BARCODE_LIST_JSON_FILEPATH']
    with open( BARCODE_LIST_JSON_FILEPATH, 'r' ) as f:
        j_string = f.read()
    patron_barcodes = json.loads( j_string )  # list
    sierra_patron_id_dct = {}
    for patron_barcode in patron_barcodes:
        sierra_patron_id = None
        time.sleep( 1 )
        try:
            sierra_patron_id = convert_id_from_barcode( patron_barcode )
        except:
            log.exception( f'problem getting id for patron_barcode `{patron_barcode}`; traceback follows; will try a 2nd time.' )
            try:
                sierra_patron_id = convert_id_from_barcode( patron_barcode )
            except:
                log.exception( f'problem with 2nd try; traceback follows; will continue to next available barcode' )
        if sierra_patron_id:
            sierra_patron_id_dct[patron_barcode] = sierra_patron_id
    log.debug( f'sierra_patron_id_dct, ```{pprint.pformat(sierra_patron_id_dct)}```' )
    data = json.dumps( sierra_patron_id_dct, sort_keys=True, indent=2 )
    with open( PBARCODE_ID_DCT_JSON_FILEPATH, 'w' ) as f:
        f.write( data )
    return


def convert_id_from_barcode( patron_barcode ):
    """ Attempts to get a sierra-patron-id for the given barcode. """
    PAPI_URL = os.environ['TEMP__PAPI_URL']
    PAPI_BASIC_AUTH_USERNAME = os.environ['TEMP__PAPI_BASIC_AUTH_USERNAME']
    PAPI_BASIC_AUTH_PASSWORD = os.environ['TEMP__PAPI_BASIC_AUTH_PASSWORD']
    r = requests.get( PAPI_URL, params={'patron_barcode': patron_barcode}, timeout=10, auth=(PAPI_BASIC_AUTH_USERNAME, PAPI_BASIC_AUTH_PASSWORD) )
    r.raise_for_status()  # will raise an http_error if not 200
    papi_dct = r.json()
    # log.debug( f'papi_dct, ```{pprint.pformat(papi_dct)}```' )
    sierra_patron_id = papi_dct['response']['record_']['value'][1:]  # strips initial character from, eg, '=1234567'
    log.debug( f'patron_barcode, `{patron_barcode}`; sierra_patron_id, `{sierra_patron_id}`' )
    return sierra_patron_id


if __name__ == '__main__':
    # make_file_list()
    # extract_barcodes_from_file( '' )
    # process_files()
    # convert_id_from_barcode( os.environ['TEMP__TEST_PATRON_BARCODE'] )
    convert_ids_from_barcodes()
