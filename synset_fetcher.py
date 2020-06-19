import requests
import time
import os.path as osp
from configs import *


def get_mapping(wnid):
    """
    Get list of image urls with their corresponding name mapping.
    Result will be saved as file for further reference.

    :param  wnid: synset id, eg. n02100735
    :return:
    """
    time.sleep(0.5)  # Avoid overloading ImageNet.
    print("Fetching urls for {}".format(wnid))
    url = WNID_MAPPING_URL.format(wnid)
    response = requests.get(url)
    if response:
        # Write to file
        with open(osp.join(DATABASE_DIR, wnid+'.txt'), 'w') as f:
            for item in response.content.splitlines():
                try:
                    if not len(item) > 1: continue
                    decoded = item.decode('utf-8')
                    f.write(decoded + '\n')
                except:
                    print("Error decoding entry {}".format(item))
            f.close()
    else:
        print("Fail to fetch image urls for {}".format(wnid))


def fetch_image_urls(wnid_list):
    """
    Prepare list of image urls to download.
    Fetch synset's urls if not exist.

    :param wnid_list: list of classes to download
    :return: list of download links
    """
    download_list = dict()
    for wnid in wnid_list:
        # Check if mapping exists
        wnid_file = osp.join(DATABASE_DIR, wnid+".txt")
        if not osp.exists(wnid_file):
            get_mapping(wnid)

        mappings = open(wnid_file, 'r').read().split('\n')
        mappings.pop(-1)
        for item in mappings:
            idx, url = item.split(' ')
            download_list[idx] = url

    return download_list



