import os
import subprocess

# PMVS目录
PMVS_BIN = "F:/CMVS-PMVS/binariesWin-Linux/Win64-VS2010"

class CMVS_PMVS:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.reconstruction_dir = os.path.join(output_dir, "reconstruction_sequential")

    def CMVS(self):
        pRecons = subprocess.Popen(
            [os.path.join(PMVS_BIN, "cmvs"), self.reconstruction_dir + "/PMVS/"])
        pRecons.wait()
        pRecons = subprocess.Popen(
            [os.path.join(PMVS_BIN, "genOption"), self.reconstruction_dir + "/PMVS/"])
        pRecons.wait()

    def PMVS(self):
        pRecons = subprocess.Popen(
            [os.path.join(PMVS_BIN, "pmvs2"), self.reconstruction_dir + "/PMVS/",
             "option-0000"])
        pRecons.wait()
