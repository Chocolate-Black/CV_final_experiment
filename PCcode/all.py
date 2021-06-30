import os
import subprocess

# openmvg编译bin目录
OPENMVG_SFM_BIN = "F:/openMVG2/openMVG/src/build/Windows-AMD64-Release/Release"
# pmvs编译bin目录
PMVS_BIN = "F:/CMVS-PMVS/binariesWin-Linux/Win64-VS2010"
# openmvg相机参数目录
CAMERA_SENSOR_WIDTH_DIRECTORY = "F:/openMVG2/openMVG/src/openMVG/exif/sensor_width_database"

class mvg_mvs:
    def __init__(self,input_dir,output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.matches_dir = os.path.join(output_dir, "matches")
        self.camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY,
                                               "sensor_width_camera_database.txt")  # 相机参数
        self.reconstruction_dir = os.path.join(output_dir, "reconstruction_sequential")
        if not os.path.exists(self.matches_dir):
            os.mkdir(self.matches_dir)

    # 一键重建
    def recon(self):
        pIntrisics = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"), "-i", self.input_dir, "-o", self.matches_dir,
             "-d",
             self.camera_file_params, "-c", "3"])
        pIntrisics.wait()

        pFeatures = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"), "-i", self.matches_dir + "/sfm_data.json", "-o",
             self.matches_dir, "-m", "SIFT", "-f", "1"])
        pFeatures.wait()

        pMatches = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"), "-i", self.matches_dir + "/sfm_data.json", "-o",
             self.matches_dir, "-f", "1", "-n", "ANNL2"])
        pMatches.wait()

        pRecons = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_IncrementalSfM"), "-i", self.matches_dir + "/sfm_data.json", "-m",
             self.matches_dir, "-o", self.reconstruction_dir])
        pRecons.wait()

        pRecons = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"), "-i",
             self.reconstruction_dir + "/sfm_data.bin",
             "-o", os.path.join(self.reconstruction_dir, "colorized.ply")])
        pRecons.wait()

        pRecons = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"), "-i",
                                    self.reconstruction_dir + "/sfm_data.bin", "-m", self.matches_dir, "-o",
                                    os.path.join(self.reconstruction_dir, "robust.ply")])
        pRecons.wait()

        pRecons = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2PMVS"), "-i", self.reconstruction_dir + "/sfm_data.bin",
             "-o",
             self.reconstruction_dir])
        pRecons.wait()

        pRecons = subprocess.Popen(
            [os.path.join(PMVS_BIN, "cmvs"), self.reconstruction_dir + "/PMVS/"])
        pRecons.wait()
        pRecons = subprocess.Popen(
            [os.path.join(PMVS_BIN, "genOption"), self.reconstruction_dir + "/PMVS/"])
        pRecons.wait()
        pRecons = subprocess.Popen(
            [os.path.join(PMVS_BIN, "pmvs2"), self.reconstruction_dir + "/PMVS/",
             "option-0000"])  # 注：不要修改pmvs_options.txt文件名
        pRecons.wait()


