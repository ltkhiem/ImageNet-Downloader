import os
import os.path as osp
import argparse
import logging
import requests
from configs import *
from synset_fetcher import fetch_image_urls
from multiprocessing import Pool, Lock, Value
import multiprocessing_logging


parser = argparse.ArgumentParser(description='ImageNet Downloader')
parser.add_argument('-num_classes', default=999999999, type=int)  # To be implemented
parser.add_argument('-num_images', default=999999999, type=int)  # To be implemented
parser.add_argument('-output_dir', default='ImageNet', type=str)
parser.add_argument('-classes_list', default=None, type=str)
parser.add_argument('-resume', default=False, type=bool)
parser.add_argument('-num_workers', default=8, type=int)

args, args_other = parser.parse_known_args()

url_mappings = dict()
lock = Lock()
logging.basicConfig(filename='downloader.log', level=logging.WARNING)

if args.classes_list:
    dataset_dir = args.classes_list
    wnid_list = open(dataset_dir, 'r').read().split('\n')
    wnid_list.pop(-1)
    url_mappings = fetch_image_urls(wnid_list)

if not osp.exists(args.output_dir):
    os.mkdir(args.output_dir)


def check_header(header):
    """
    Check if url contains an image.

    :param header: response's header
    :return: boolean
    """
    try:
        if not 'image' in header['content-type']:
            return False
        return True
    except:
        return False


def get_extension(url):
    url = url.split('/')[-1]  # Get the last part of url
    url = url.split('?')[0]  # Remove url's params
    url = url.split('&')[0]  # Remove page settings
    ext = url.split('.')[-1]
    return ext


def get_image(image_id):
    """
    Fetch image from an url.

    :param image_id: image_name with wnid prefix
    :return: ---
    """
    try:
        url = url_mappings[image_id]

        response = requests.get(url, timeout=10)
        if check_header(response.headers):
            image_folder = image_id.split('_')[0]
            image_extension = get_extension(url)
            image_path = osp.join(args.output_dir, image_folder, "{}.{}".format(image_id, image_extension))
            with open(image_path, 'wb') as f:
                f.write(response.content)
                with lock:
                    cnt += 1
                    with open(osp.join(TEMP_DIR, 'downloaded.txt'), 'a') as ff:
                        ff.write(image_id + '\n')
        else:
            raise Exception("Not an image")


    except Exception as e:
        logging.error("<<{0}>> raises while fetching image {1} at {2}".format(str(e), image_id, url))


def download():
    """
    Handles download ImageNet dataset.

    :return: ---
    """
    if args.resume:
        try:
            downloaded = open(osp.join(TEMP_DIR, "downloaded.txt"), 'r').read().split('\n')
            downloaded.pop(-1)
            for item in downloaded:
                url_mappings.pop(item)
        except:
            pass

    for wnid in wnid_list:
        out_path = osp.join(args.output_dir, wnid)
        if not osp.exists(out_path):
            os.mkdir(out_path)

    print("Found {} classes".format(len(wnid_list)))
    print("Total images to download: {}".format(len(url_mappings)))
    input("Press any key to start ...")

    multiprocessing_logging.install_mp_handler()
    with Pool(processes=args.num_workers) as p:
        p.map(get_image, url_mappings.keys())


if __name__ == "__main__":
    download()
