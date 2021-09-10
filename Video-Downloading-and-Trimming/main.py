# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import csv
import subprocess
import os.path as osp
import glob


saving_path = '/home/hydraulik/mmaction2/data/my_set/'

tmp_path = '/tmp/my_set/'


def download_videos(vid_list):

    done_vids = glob.glob('/tmp/my_set/**/*.mp4')
    done_list = [done_vids[row] for row in done_vids]

    print(type(done_list))

    for row in vid_list:
        output_filename = osp.join(tmp_path, ''.join(['vid_', row[1], '.mp4']))

        if output_filename not in done_list:
            print('Downloading:', row[1])

            command = f'youtube-dl --quiet --no-warnings --no-check-certificate -f mp4 \
                      -o "{output_filename}" "https://www.youtube.com/watch?v={row[1]}"'

            try:
                subprocess.check_output(
                    command, shell=True, stderr=subprocess.STDOUT)
                done_vids.append(row[1])

            except subprocess.CalledProcessError as err:
                print('Oh, no :(', err)

    return


def read_csv(csv_path):

    with open(csv_path, 'r') as file:
        csv_file_r = csv.reader(file)
        listed_file = [tuple(row) for row in csv_file_r]

    listed_file.pop(0)

    return listed_file


def trim_videos(vid_list):

    for row in vid_list:
        print('Trimming:', row[1])

        tmp_filename = osp.join(tmp_path, ''.join(['vid_', row[1], '.mp4']))
        output_filename = osp.join(saving_path, row[4], row[0], ''.join([row[1], row[2], '-', row[3], '.mp4']))

        command = [
            'ffmpeg', '-i',
            '"%s"' % tmp_filename, '-ss',
            str(row[2]), '-to',
            str(row[3]), '-c:v', 'libx264', '-c:a', 'copy',
            '-threads', '1', '-loglevel', 'panic',
            '"%s"' % output_filename
        ]
        command = ' '.join(command)

        try:
            subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as err:
            print('Oh, no :( \n', err)

    return


if __name__ == '__main__':
    csv_path = '/home/hydraulik/mmaction2/data/my_set/annotations/coocked/my_kinetics_test_full.csv'

    video_list = read_csv(csv_path)
#    video_list = [('gymnastics_tumbling', 'lMbN6IcrxLs', '0', '180', 'test')]

    download_videos(video_list)
    trim_videos(video_list)
