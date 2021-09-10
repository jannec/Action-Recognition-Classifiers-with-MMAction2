import sys
import threading
import time
import PySimpleGUI as sg
from PIL import Image, ImageTk

from helper_classes import Interpreter, VideoReader


class MyWindow:

    def __init__(self):

        # ==== INTERPRETER ====#
        networks = {
            'tsn pretrained on kinetics400': (
                'configs/recognition/tsn/tsn_r50_video_1x1x8_100e_kinetics400_rgb_modified.py',
                'checkpoints/tsn_kinetics400_epoch_20.pth'),

            'tsn pretrained on diving48': (
                'configs/recognition/tsn/tsn_r50_video_1x1x8_100e_diving48_rgb_modified.py',
                'checkpoints/tsn_diving_epoch_20.pth'),

            'tsm pretrained on diving48': (
                'configs/recognition/tsm/tsm_r50_video_1x1x8_50e_diving48_rgb_modified.py',
                'checkpoints/tsm_diving_epoch_20.pth'),

            'tsm pretrained on kinetics400': (
                'configs/recognition/tsm/tsm_r50_video_1x1x8_50e_kinetics400_rgb_modified.py',
                'checkpoints/tsm_kinetics400_epoch_20.pth')
        }

        labels = 'label_list.txt'
        device = 'cpu'

        self.interpreter = None
        self.interpreter_event = threading.Event()
    #    self.interpreter_event.clear()
        self.net = 'tsn pretrained on kinetics400'
        self.top1_result = ''
        self.top4_result = ''

        # ==== VIDEO HANDLING ====#
        self.vReader = None
        self.image = None
        self.video = ''
        self.play_pause_event = threading.Event()
    #    self.play_pause_event.clear()
        self.video_length = 0
        self.cur_frame = 0
        self.v_height = 500
        self.v_width = 500

        # ==== GUI ====#
        sg.theme('DarkGray')
        controls_column = [
            # ==== NET BROWSER ====#
            [sg.Text('Choose network:')],
            [sg.Combo(
                values=['tsn pretrained on kinetics400',
                        'tsn pretrained on diving48',
                        'tsm pretrained on kinetics400',
                        'tsm pretrained on diving48'
                        ],
                default_value='tsn pretrained on kinetics400',
                size=(35, 3),
                enable_events=True,
                key="-NETWORK-")],

            # ==== FILE BROWSER ====#
            [sg.Text('Choose video file:')],
            [sg.In(size=(35, 1), enable_events=True, key="-VIDEO-BROWSER-"),
             sg.FileBrowse()],

            # ==== TOP4ACC ====#
            [sg.Text('Ordered accuracy:')],
            [sg.Multiline(size=(35, 4), key="-4-RESULTS-")],
            [sg.Text('Perform recognition'), sg.Button('Start', key="-RECOGNIZE-")],

        ]

        # ==== VIDEO DISPLAY + TOP1ACC ====#
        video_display_column = [
            [sg.Text('Using network:'),
             sg.Text('tsn pretrained on kinetics400', enable_events=True, key="-NETWORK-NAME-")],
            [sg.Canvas(size=(500, 500), key="-DISPLAY-", background_color='black')],

            # ==== VIDEO CONTROLS ====#
            [sg.Slider(range=(0, 0), orientation='horizontal', size=(63, 10), key="-SLIDER-", enable_events=True)],
            [sg.Button('Play', key="-PLAY-"),
             sg.Button('Pause', key="-PAUSE-")]
        ]

        layout = [
            [sg.Column(controls_column, vertical_alignment='top'),
             sg.VSeparator(),
             sg.Column(video_display_column)],
            [sg.Button("Exit", size=(10, 1))]
        ]

        self.window = sg.Window(
            "Gymnastics Brain",
            layout,
            location=(0, 0),
            finalize=True,
            element_justification="left",
            font="Courier 12").Finalize()

        display = self.window.Element("-DISPLAY-")
        self.display = display.TKCanvas

        self.interpreter_thread()
        self.video_thread()

        self.interpreter = Interpreter(networks, labels, device)

        while True:
            event, values = self.window.Read()

            if event == sg.WIN_CLOSED or event == "Exit":
                break

            if event == "-VIDEO-BROWSER-":
                if values["-VIDEO-BROWSER-"] != self.video:
                    self.video = values["-VIDEO-BROWSER-"]
                    try:
                        self.vReader = VideoReader(self.video, norm=500)     # norm -> normalization
                        self.top1_result, self.top4_result = None, None
                        self.v_height = self.vReader.NORM_HEIGHT
                        self.display.config(width=self.v_width, height=self.v_height)
                        self.window["-VIDEO-BROWSER-"].update(self.video)
                        self.window["-SLIDER-"].update(range=(0, self.vReader.FRAMES))
                        self.cur_frame = 0
                    except ZeroDivisionError as err:
                        print(err)

            if event == "-NETWORK-":
                self.net = values["-NETWORK-"]
                self.window["-NETWORK-NAME-"].update(self.net)

            if event == "-RECOGNIZE-":
                self.interpreter_event.set()

            if event == "-PLAY-":
                if self.vReader:
                    self.play_pause_event.set()

            if event == "-PAUSE-":
                if self.vReader:
                    self.play_pause_event.clear()

            if event == "-SLIDER-":
                self.wanted_frame = values["-SLIDER-"]
                self.set_frame(self.wanted_frame)

        self.window.close()
        sys.exit()

    def video_thread(self):
        t = threading.Thread(target=self.play_video)
        t.daemon = True
        t.start()

    def interpreter_thread(self):
        t = threading.Thread(target=self.interpret_video)
#        t.daemon = True
        t.start()

    def interpret_video(self):
        while self:
            self.interpreter_event.wait()
            if self.vReader:
                self.window["-4-RESULTS-"].update('recognizing...')
                self.top1_result, self.top4_result = self.interpreter.get_results(self.video, self.net)
                self.window["-4-RESULTS-"].update(self.top4_result)
                self.interpreter_event.clear()
            else:
                self.top1_result = ''
                self.top4_result = ''
                self.window["-4-RESULTS-"].update('Nothing to recognize.')
                self.interpreter_event.clear()

    def play_video(self):
        if self.play_pause_event.is_set():
            start_time = time.time()

            if self.vReader:
                ret, frame = self.vReader.play_video(top1acc=self.top1_result)

                if ret:
                    self.image = ImageTk.PhotoImage(
                        image=Image.fromarray(frame).resize((self.v_width, self.v_height), Image.NEAREST))
                    self.display.create_image(0, 0, image=self.image, anchor='nw')

                    self.cur_frame += 1
                    self.window["-SLIDER-"].update(value=self.cur_frame)

                self.display.after(abs(int((self.vReader.DELAY - (time.time() - start_time)) * 1000)), self.play_video)
                return

        self.display.after(200, self.play_video)
        return

    def set_frame(self, wanted_frame):
        if self.vReader:
            ret, frame = self.vReader.set_frame(wanted_frame, top1acc=self.top1_result)
            self.cur_frame = wanted_frame
            self.window["-SLIDER-"].update(value=self.cur_frame)
            if ret:
                self.image = ImageTk.PhotoImage(
                    image=Image.fromarray(frame).resize((self.v_width, self.v_height), Image.NEAREST))
                self.display.create_image(0, 0, image=self.image, anchor='nw')
        return


if __name__ == '__main__':
    MyWindow()
