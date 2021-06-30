import os
import subprocess
import sys

# openmvg编译bin目录
OPENMVG_SFM_BIN = "F:/openMVG2/openMVG/src/build/Windows-AMD64-Release/Release"
# openmvg相机参数目录
CAMERA_SENSOR_WIDTH_DIRECTORY = "F:/openMVG2/openMVG/src/openMVG/exif/sensor_width_database"


class OpenMVG:
    def __init__(self,input_dir,output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.matches_dir = os.path.join(output_dir, "matches")
        self.camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")  # 相机参数
        self.reconstruction_dir = os.path.join(output_dir, "reconstruction_sequential")
        if not os.path.exists(self.matches_dir):
            os.mkdir(self.matches_dir)

    # 初始化
    def Intrinsics_analysis(self):
        pIntrisics = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),
             "-i", self.input_dir,
             "-o", self.matches_dir,
             "-d",
             self.camera_file_params, "-c", "3"])
        pIntrisics.wait()

    # 提取特征
    def Compute_features(self):
        pFeatures = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"), "-i", self.matches_dir + "/sfm_data.json", "-o",
             self.matches_dir, "-m", "SIFT", "-f", "1"])
        pFeatures.wait()

    # 几何匹配
    def Compute_matches(self):
        pMatches = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"), "-i", self.matches_dir + "/sfm_data.json", "-o",
             self.matches_dir, "-f", "1", "-n", "ANNL2"])
        pMatches.wait()

    # 增量式重建
    def Incremental_sfm(self):
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

    # 全局SFM
    def global_sfm(self):
        pMatches = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"), "-i", self.matches_dir + "/sfm_data.json", "-o",
             self.matches_dir, "-r", "0.8", "-g", "e"])
        pMatches.wait()
        pRecons = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_GlobalSfM"), "-i", self.matches_dir + "/sfm_data.json", "-m",
             self.matches_dir, "-o", self.reconstruction_dir])
        pRecons.wait()
        pRecons = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"), "-i",
                                    self.reconstruction_dir + "/sfm_data.bin", "-o",
                                    os.path.join(self.reconstruction_dir, "colorized.ply")])
        pRecons.wait()
        pRecons = subprocess.Popen([os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"), "-i",
                                    self.reconstruction_dir + "/sfm_data.bin", "-m", self.matches_dir, "-o",
                                    os.path.join(self.reconstruction_dir, "robust.ply")])
        pRecons.wait()

    # 为PMVS做准备
    def convert_to_PMVS(self):
        pRecons = subprocess.Popen(
            [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2PMVS"), "-i", self.reconstruction_dir + "/sfm_data.bin",
             "-o",
             self.reconstruction_dir])
        pRecons.wait()


