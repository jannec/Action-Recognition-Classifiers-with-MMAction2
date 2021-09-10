import csv
import glob
import os.path as osp
import random
import concurrent.futures

"""
Sieving categories from annotation files from other datasets. If You want to use some videos of given category
from another dataset, feel free to sieve their csv files.
"""


def sieve_categories(file, categories, set_name):
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        with open(f'my_annotations/{set_name}_sieved_from_{osp.basename(file)}', 'w') as new_file:
            csv_writer = csv.writer(new_file)

            for line in csv_reader:
                for category in categories:
                    if line[0] == category:
                        csv_writer.writerow(line)

    return


"""
Use this function to make annotations file used in training purposes.

"""


def make_annotations(annotations_tuple, labels_dict):
    file_path, glob_path = annotations_tuple

    paths = glob.glob(glob_path)
    common_prefix = osp.commonprefix(paths)
    rel_paths = [osp.relpath(path, common_prefix) for path in paths]

    with open(file_path, 'w+') as annotations_file:
        annotations_list = [osp.join(key, osp.basename(path)) + ' ' + labels_dict[key] + '\n'
                            for path in rel_paths for key in labels_dict.keys() if key in path]
        random.shuffle(annotations_list)
        for line in annotations_list:
            annotations_file.writelines(line)

    return


if __name__ == '__main__':

    """
    Setups for next functions.
    """

    files_to_sieve_list = ['annotations/kinetics_val.csv',
                           'annotations/kinetics_train.csv',
                           'annotations/kinetics_test.csv']

    categories_list = ['label',
                       'gymnastics_tumbling',
                       'breakdancing',
                       'parkour']

    dataset_name = 'my_set'
    annotations_paths_dict = {
        0: (f'coocked/{dataset_name}_annotations_val.txt',
            f'/home/hydraulik/mmaction2/data/{dataset_name}/validate/**/*.mp4'),
        1: (f'coocked/{dataset_name}_annotations_train.txt',
            f'/home/hydraulik/mmaction2/data/{dataset_name}/train/**/*.mp4'),
        2: (f'coocked/{dataset_name}_annotations_test.txt',
            f'/home/hydraulik/mmaction2/data/{dataset_name}/test/**/*.mp4')
    }

    labels = {'breakdancing': '0',
              'gymnastics_tumbling': '1',
              'parkour': '2',
              'tricking': '3'}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(3):
            executor.submit(sieve_categories,  files_to_sieve_list[i], categories_list, dataset_name)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(3):
            executor.submit(make_annotations, annotations_paths_dict[i], labels)
