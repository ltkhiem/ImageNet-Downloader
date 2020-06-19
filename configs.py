import os
import os.path as osp

WNID_MAPPING_URL = "http://www.image-net.org/api/text/imagenet.synset.geturls.getmapping?wnid={0}"
DATABASE_DIR = "database"
TEMP_DIR = "temp"

if not osp.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

if not osp.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
