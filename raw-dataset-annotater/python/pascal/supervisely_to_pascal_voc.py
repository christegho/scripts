import glob, json, os, shutil
from pascal_voc_writer import *
import config as cfg
import argparse

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def supervisely_to_pascal_voc():
    """
    Hierarchy:
    Data Directory
    -> images
    --> image0.png
    --> image1.png
    --> imageN.png
    -> labels
    --> labels0.txt
    --> labels1.txt
    --> labelsN.txt

    In other words labels folder should be located next to the image folder in the same directory named "labels".
    """
    if not os.path.exists(cfg.voc_folder_name):
        os.mkdir(cfg.voc_folder_name)

    for subfolder in ['Annotations', 'JPEGImages', 'labels', 'ImageSets', 'ImageSets/Main']:
        if not os.path.exists(os.path.join(cfg.voc_folder_name, subfolder)):
            os.mkdir(os.path.join(cfg.voc_folder_name, subfolder))

    image_index = 0
    image_set = open(os.path.join(cfg.voc_folder_name, 'ImageSets', 'Main', cfg.dataset, 'w')
    list_file = open('{}.txt'.format(cfg.dataset), 'w')
    for json_path_pattern in cfg.json_path_pattern:
        for file in glob.glob(json_path_pattern):
            print(file)
            with open(file) as json_file:
                data = json.load(json_file)
                image_path = file.split('/')
                image_path[-1] = image_path[-1].split('.')[0] + '.png'
                image_path[-2] = 'img'
                image_path = os.path.join(*image_path)
                image_name = cfg.prefix_im_name + '_' + str(image_index).zfill(5)
                image_set.write(image_name+'\n')
                new_image_path = '{}/JPEGImages/{}.jpg'.format(cfg.voc_folder_name, image_name)
                list_file.write(new_image_path+'\n')
                image_index += 1
                try:
                    shutil.copy(image_path, new_image_path)
                except:
                    print('error', image_path, new_image_path)

                label_txt = open('{}/labels/{}.txt'.format(cfg.voc_folder_name, image_name), 'w')
                w = data["size"]["width"]
                h = data["size"]["height"]
                writer = Writer(new_image_path, w, h)
                for detBox in data['objects']:
                    if ('bitmap' not in detBox or ('bitmap' in detBox and not detBox['bitmap'])) \
                        and detBox['classTitle'] in cfg.class_mapping:
                        classname = detBox['classTitle']
                        p1, p2 = detBox['points']['exterior']
                        x1, y1 = p1
                        x2, y2 = p2
                        x_min = min(x1, x2)
                        x_max = max(x1, x2)
                        y_min = min(y1, y2)
                        y_max = max(y1, y2)
                        writer.addObject(cfg.class_mapping[classname], x_min, y_min, x_max, y_max)
                        bb = convert((int(w), int(h)), [float(a) for a in [x_min, x_max, y_min, y_max]])
                        label_txt.write(str(cfg.classes_conversion[classname]) + " " + " ".join([str(a) for a in bb]) + '\n')

                writer.save('{}/Annotations/{}.xml'.format(cfg.voc_folder_name, image_name))
                label_txt.close()

    list_file.close()
    image_set.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    supervisely_to_pascal_voc()

