import torch
import time
from mmaction.apis import init_recognizer, inference_recognizer

import cv2


# Class made for interpreting videos with networks made with mmaction2
class Interpreter:

    def __init__(self, networks, labels, device):
        self.networks = networks
        self.labels = labels
        self.device = device

    def get_results(self, video, net):
        device = torch.device(self.device)
        model = init_recognizer(self.networks[net][0], self.networks[net][1], device=device)

        start = time.time()
        results = inference_recognizer(model, video, self.labels)
        end = time.time()
        print(end - start)

        results = [[first, round(second, 3)] for [first, second] in results]

        top4_results = [str(line).strip("['']") for line in results]
        top4_results = '\n'.join(top4_results)

        top1_result = str(results[0][0])
        print(top1_result)
        print(top4_results)

        return top1_result, top4_results


class VideoReader:
    """
    Video Reader Class for reading video files with cv2 and rendering frames with printed label on top of them.
    video_path      ->   path to video in your file system.
    normalization   ->   value of horizontal dimension

    """
    def __init__(self, video_path, norm=None):
        self.cap = cv2.VideoCapture(video_path)

        self.WIDTH = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.HEIGHT = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.FPS = self.cap.get(cv2.CAP_PROP_FPS)
        self.FRAMES = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

        self.NORM_HEIGHT = int(norm * self.HEIGHT / self.WIDTH)
        self.DELAY = 1 / self.FPS

        self.FONT_SCALE = 0.9 * self.HEIGHT/self.NORM_HEIGHT

    def play_video(self, top1acc=''):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                colored_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                ready_frame = cv2.putText(colored_frame, top1acc, (int(self.FONT_SCALE * 5), int(self.FONT_SCALE * 45)),
                                          cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE, (255, 255, 255), thickness=int(2 * self.FONT_SCALE))

                return ret, ready_frame
            else:
                return ret, None

        return False, None

    def set_frame(self, wanted_frame, top1acc=''):
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, wanted_frame)
            ret, frame = self.cap.read()
            if ret:
                colored_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                ready_frame = cv2.putText(colored_frame, top1acc, (int(self.FONT_SCALE * 5), int(self.FONT_SCALE * 45)),
                                          cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE, (255, 255, 255), thickness=int(2 * self.FONT_SCALE))

                return ret, ready_frame
            else:
                return ret, None

        return False, None

    # def set_video(self, called_frame, top1acc=''):
    #    if self.cap.isOpened():
    #        self.cap.set(cv2.CAP_PROP_POS_FRAMES, called_frame)
    #        ret, frame = self.cap.read()
    #        if not ret:
    #            return ret, None

    #       else:
    #           frame = cv2.putText(frame, top1acc, (self.dimensions['height'] - 25, 25), cv2.FONT_HERSHEY_SIMPLEX,
    #                               1, (255, 255, 255), thickness=1.5)
    #           return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #   return False, None

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()