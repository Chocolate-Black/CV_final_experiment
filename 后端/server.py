import os
import subprocess
import sys
# import cv2
# import numpy as np
from flask import Flask, request, send_from_directory
import datetime
import random
# import base64
import shutil
from cloud import wxCloud
from random import choice
# pip install open3d-python
import open3d as o3d

localhost='http://127.0.0.1:8080/'
remoteserver='http://101.226.18.132:8000/'
app = Flask(__name__)
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'building/images')
app.config['PLY_PATH'] = os.path.join(app.root_path, 'building/reconstruction_sequential')
# openmvg编译bin目录(可cp -p到/usr/local/bin/)
OPENMVG_SFM_BIN = "/root/code/openMVG_Build/Linux-x86_64-RELEASE"
# pmvs编译bin目录(可cp -p到/usr/local/bin/)
PMVS_BIN = "/root/code/CMVS-PMVS/build/main"
# openmvg相机参数目录
CAMERA_SENSOR_WIDTH_DIRECTORY = "/root/code/openMVG/src/openMVG/exif/sensor_width_database"



def create_uuid(): #生成唯一的图片的名称字符串，防止图片显示时的重名问题
    nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前时间
    randomNum = random.randint(0, 100)  # 生成的随机整数n，其中0<=n<=100
    if randomNum <= 10:
        randomNum = str(0) + str(randomNum)
    uniqueNum = str(nowTime) + str(randomNum)
    return uniqueNum
def array(list):
    string = ""
    for x in list:
        print(x)
        string+= x
    return string

@app.route('/uppic', methods=['get','post']) # 上传图片
def uppic():
    img = request.files.get('file')
    # if i =='0':
    #     # path = os.path.join(app.config['UPLOAD_PATH'], '*')
    #     shutil.rmtree(app.config['UPLOAD_PATH'])
    #     os.mkdir(app.config['UPLOAD_PATH'])
    # print(array(request.form.get('type')))
    filename = create_uuid() + '.' + img.filename.split('.')[-1]
    path=os.path.join(app.config['UPLOAD_PATH'], filename)
    img.save(path)
    return "0"

@app.route('/clear', methods=['get','post']) # 清空图片
def clear():
    # path = os.path.join(app.config['UPLOAD_PATH'], '*')
    shutil.rmtree(app.config['UPLOAD_PATH'])
    os.mkdir(app.config['UPLOAD_PATH'])
    return "0"

@app.route('/rectr', methods=['get','post']) # 重建并保存
def rectr():
    file = "".join([choice("0123456789ABCDEF") for i in range(6)])
    type = request.get_json()['type']
    f_length=request.get_json()['f_length']
    print(type,f_length)
    # filename=file+'.ply'
    filename = 'option-0000.ply'

    # filename='surface_mesh.ply'
    
    # 0. 下载测试照片
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.abspath("./building")
    # data_dir = os.path.abspath("./ImageDataset_SceauxCastle")
    input_dir = os.path.join(data_dir, "images")
    output_dir = data_dir
    print("Using input dir  : ", input_dir)
    print("      output_dir : ", output_dir)
    matches_dir = os.path.join(output_dir, "matches")
    camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")  # 相机参数
    if not os.path.exists(matches_dir):
        os.mkdir(matches_dir)

    # 1. 从图片数据集中生成场景描述文件sfm_data.json
    print ("----------1. Intrinsics analysis----------")
    pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-d", camera_file_params, "-c", "3"] )
    #*注：如果产出的sfm_data.json里intrinsics内容为空，通常是在图片没有exif信息导致获取不到相机焦距、ccd尺寸等参数，用>带exif的原图即可。
    pIntrisics.wait()
    
    # 2. 计算图像特征
    print ("----------2. Compute features----------")
    pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT", "-f" , "1"] )
    pFeatures.wait()
    
    # 3. 计算几何匹配
    print ("----------3. Compute matches----------")
    pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-f", "1", "-n", "ANNL2"] )
    pMatches.wait()

    # 4. 执行增量三维重建
    reconstruction_dir = os.path.join(output_dir,"reconstruction_sequential")
    print ("----------4. Do Incremental/Sequential reconstruction----------") #set manually the initial pair to avoid the prompt question
    pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_IncrementalSfM"),  "-i", matches_dir+"/sfm_data.json", "-m", matches_dir, "-o", reconstruction_dir] )
    pRecons.wait()
    
    # 5. 计算场景结构颜色
    print ("----------5. Colorize Structure----------")
    pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
    pRecons.wait()
    
    # 6. 测量稳健三角
    print ("----------6. Structure from Known Poses (robust triangulation)----------")
    pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", reconstruction_dir+"/sfm_data.bin", "-m", matches_dir, "-o", os.path.join(reconstruction_dir,"robust.ply")] )
    pRecons.wait()

    
    # 7. 把openMVG生成的SfM_Data转为适用于PMVS输入格式的文件
    print ("----------7. Export to PMVS/CMVS----------")
    pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2PMVS"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", reconstruction_dir] )
    pRecons.wait()
    #*注：执行后会在-o路径下生成一个PMVS目录，包含 models, txt, visualize 三个子目录：models为空；txt包含对应图像的txt>文档，每个里面都是一个3x4的矩阵，大概是相机位姿；visualize包含11张图像，不确定是原图像还是校正过的图像
    
    # 8. 使用PMVS重建稠密点云、表面、纹理
    print ("----------8. pmvs2----------")
    pRecons = subprocess.Popen( [os.path.join(PMVS_BIN, "pmvs2"),  reconstruction_dir+"/PMVS/", "pmvs_options.txt"] )  # 注：不要修改pmvs_options.txt文件名
    pRecons.wait()
    #*注：执行后会在./PMVS/models文件夹中生成一个pmvs_options.txt.ply点云文件，用meshlab打开即可看到重建出来的彩色稠密>点云。



    path = os.path.join(app.config['PLY_PATH'], filename)
    mesh = o3d.io.read_triangle_mesh(path)
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(mesh)
    vis.update_geometry()
    vis.poll_events()
    vis.update_renderer()
    imgname = create_uuid() + '.png'
    imgname = file + '.png'
    imgpath=os.path.join(app.config['PLY_PATH'], imgname)
    vis.capture_screen_image(imgpath)
    vis.destroy_window()

    APP_ID = 'wxef5d34a20*******'	# 账号安全打码处理
    APP_SECRET = '************************************'
    ENV = 'test-jpqyt'
    ID = request.get_json()['id']
    print(ID)

    db = wxCloud(APP_ID, APP_SECRET, ENV)
    db.collection = 'test'
    if db.query_data(id=ID):
        print('找到用户')
        db.update_data(  # 存在则更新
            id=ID,
            address=localhost+'dld/'+filename,
            imgurl = localhost+'dld/' + imgname
        )
    else:
        print('新建用户')
        db.add_data(  # 不存在则添加
            id=ID,
            address=localhost+'dld/'+filename,
            imgurl = localhost+'dld/' + imgname
        )


@app.route("/dld/<filename>")
def download(filename):
    return send_from_directory(app.config['PLY_PATH'],path=filename,as_attachment=True)

# @app.route('/reg', methods=['GET','POST'])
# def reg():
#     img = request.files.get('file')
#
#     filename = create_uuid()+'.'+ img.filename.split('.')[-1]
#     path=os.path.join(app.config['UPLOAD_PATH'], filename)
#     img.save(path)
#     # print(path)
#     # b64=predict_expression('./photo/'+filename,model, filename)[0]
#     # print(filename)
#     print(b64)
#
#     return b64


if __name__ == '__main__':
    app.run(debug=True,
                host='127.0.0.1',
                port=8080
                )

