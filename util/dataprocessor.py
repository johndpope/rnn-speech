'''
Reads in audio and text data, transforming it for input into the neural nets
It will download and extract the dataset.

TODO generalize it for any audio and corresponding text data

Curently it will only work for one specific dataset.
'''
import os
from random import shuffle
import util.audioprocessor as audioprocessor
#import multiprocessor
from math import floor
from multiprocessing import Process, Lock

class DataProcessor(object):
    def __init__(self, data_path, raw_data_path, config_dic):
        self.data_path = data_path
        self.raw_data_path = raw_data_path
        self.config_dic = config_dic

    def run(self):
        #First make output directories
        self.setupProcessedDataDirs()

        #check if processor needs to be run
        if os.path.exists(os.path.join(self.train_dir, "master_text_file.txt"))\
            and os.path.exists(os.path.join(self.test_dir, "master_text_file.txt")):
            print "No need to run data processor..."
            return

        #next check which data folders are present
        self.data_dirs = self.checkWhichDataFoldersArePresent()
        if len(self.data_dirs) == 0:
            print "Something went wrong, no data detected, check data directory.."
            return

        #get pairs of (audio_file_name, transcribed_text)
        print "Figuring out which files need to be processed..."
        audio_file_text_pairs, will_convert = self.getFileNameTextPairs()
        print "Using {0} files in total dataset...".format(len(audio_file_text_pairs))
        #shuffle pairs
        shuffle(audio_file_text_pairs)

        if will_convert:
            audio_processor = audioprocessor.AudioProcessor(1)
            for audio_file_name in audio_file_text_pairs:
                audio_processor.convertAndDeleteFLAC(audio_file_name[0].replace(".wav", ".flac"))

        #print audio_file_text_pairs[-20:]

        return audio_file_text_pairs

    def readInMetaInformation(self):
        file_info = []
        with open(os.path.join(self.raw_data_path,
            "CHAPTERS.txt")) as data_file:
            for line in data_file:
                info = line.split("|")
                if info[3].replace(" ", "") in self.data_dirs:
                    file_info.append(info)
        return file_info

    def getFileNameTextPairs(self):
        '''
        Gets and returns a list of tuples (audio_file_name, transcribed_text)
        '''
        audio_file_text_pairs = []
        for d in self.data_dirs:
            root_search_path = os.path.join(self.raw_data_path, d)
            for root, subdirs, files in os.walk(root_search_path):
                flac_audio_files = [os.path.join(root, audio_file) for audio_file in files if audio_file.endswith(".flac")]
                wav_audio_files = [os.path.join(root, audio_file) for audio_file in files if audio_file.endswith(".wav")]
                text_files = [os.path.join(root, text_file) for
                    text_file in files if text_file.endswith(".txt")]
                if len(wav_audio_files) == 0:
                    will_convert = True
                    audio_files = wav_audio_files
                else:
                    will_convert = False
                    audio_files = flac_audio_files
                if len(audio_files) >= 1 and len(text_files) >= 1:
                    assert len(text_files) == 1, "Issue detected with data directory structure..."
                    with open(text_files[0], "r") as f:
                        lines = f.read().split("\n")
                        for a_file in audio_files:
                            #this might only work on linux
                            audio_file_name = os.path.basename(a_file)
                            head = audio_file_name.replace(".flac", "")
                            for line in lines:
                                if head in line:
                                    text = line.replace(head, "").strip().lower() + "_"
                                    audio_file_text_pairs.append((a_file.replace(".flac",
                                        ".wav"), text))
                                    break
        return audio_file_text_pairs, will_convert

    def setupProcessedDataDirs(self):
        self.train_dir = os.path.join(self.data_path, "train/")
        self.test_dir = os.path.join(self.data_path, "test/")
        if not os.path.exists(self.train_dir):
            os.makedirs(self.train_dir)
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

    def checkWhichDataFoldersArePresent(self):
        dirs_to_check = ["dev-clean", "train-other-500", "train-other-100",
        "train-clean-100", "train-clean-360", "test-clean",
        "test-other", "dev-other"]
        dirs_available = [name for name in os.listdir(self.raw_data_path)]
        dirs_allowed = []
        for d in dirs_available:
            if d in dirs_to_check:
                dirs_allowed.append(d)
        return dirs_allowed
