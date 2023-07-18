import os
import subprocess
import re
import shutil
import exifread

# 判断该图片的大小和尺寸是否符合全景图
def filter_img_by_width_height_size(img_url):
    f = open(img_url, 'rb')
    tags = exifread.process_file(f)
    # 分别代表宽\高
    img_width = tags.get("EXIF ExifImageWidth")
    img_height = tags.get("EXIF ExifImageLength")
    if img_width is not None and img_height is not None:
        if isinstance(img_width,exifread.classes.IfdTag):
            if img_width.values[0] > 10000 and img_height.values[0] > 5000:
                # 说明是全景图的尺寸
                return True
            return False
        else:
            if img_width > 10000 and img_height > 5000:
                # 说明是全景图的尺寸
                return True
            return False
    return False


# add xmp header to img
def process_img(image_path):
    # 构建exiftool命令
    # use exiftool for add UsePanoramaViewer to img
    exiftool_cmd = [
        "exiftool",
        "-xmp:ProjectionType=equirectangular",
        "-xmp:CroppedAreaLeftPixels=0",
        "-xmp:CroppedAreaTopPixels=0",
        "-xmp:UsePanoramaViewer=true",
        "-overwrite_original",
        image_path
    ]
    # 执行exiftool命令
    # exec exiftool command
    complete_info = subprocess.run(exiftool_cmd)

files = os.listdir(".")
exec_path = os.getcwd()
for file in files:
    # 判断是否为经过PureShot后的图片,如果是,就增加全景信息.
    # only process PureShot img 
    result = re.match("IMG_\d{8}_\d{6}_\d+_\d+_PureShot.jpg",file)
    if result is not None or "merged" in file:
        print("{}/{}".format(exec_path,file))
        img_path = "{}/{}".format(exec_path,file)
        if filter_img_by_width_height_size(img_path):
            process_img(img_path)
    else:
        # 判断是否原始的导出图片,删除原始导出图片
        # remove orignal img 
        result = re.match("IMG_\d{8}_\d{6}_\d+_\d+\S+.jpg",file)
        if result is not None:
            # 删除无用的文件
            if filter_img_by_width_height_size("{}/{}".format(exec_path,file)):
                process_img("{}/{}".format(exec_path,file))
            #os.remove("{}/{}".format(exec_path,file))   
        # 判断是否是.jpg_original,如果是则删除
        # remove .jpg_original file
        result = re.match("\S+.jpg_original",file)
        if result is not None:
            os.remove("{}/{}".format(exec_path,file))   
        # 判断是否是.dng,如果是则删除
        # remove .dng file
        result = re.match("\S+.dng",file)
        if result is not None:
            os.remove("{}/{}".format(exec_path,file))   
        #  
    # 判断是否是文件夹,如何是文件夹则深入文件夹进行处理    
    # if the file is directory, enter dir, process img and move img back to root dir.
    if os.path.isdir(file):
        for d_file in os.listdir("{}/{}".format(exec_path,file)):
            if "jpg" in d_file:
                print("{}/{}/{}".format(exec_path,file,d_file))
                img_path = "{}/{}/{}".format(exec_path,file,d_file)
                if filter_img_by_width_height_size(img_path):
                    process_img(img_path)
                # 处理完成之后将该文件移动到原始目录下
                # move the img back to root dir
                shutil.move(img_path,"{}/{}".format(exec_path,d_file))
