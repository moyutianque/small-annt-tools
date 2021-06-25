import jsonlines
import os
import os.path as osp
import random
from PIL import Image

imsitu_images = "../../imsitu/of500_images"
extracted_annts = "3_sentlen20.jsonl"

os.makedirs('./annt_first_try', exist_ok=True)
out_file = 'annt.jsonl'

cnt = 100
with jsonlines.open(extracted_annts) as reader:
    for obj in reader:
        dice = random.random()
        if (dice > 0.01):
            continue
        im_file = obj['image_file']
        im_path = osp.join(imsitu_images, im_file.split("_")[0], im_file)
        pil_img = Image.open(im_path)

        fixed_height = 420
        height_percent = (fixed_height / float(pil_img.size[1]))
        width_size = int((float(pil_img.size[0]) * float(height_percent)))
        pil_img = pil_img.resize((width_size, fixed_height), Image.NEAREST)
        pil_img.save(osp.join('./annt_first_try', im_file))


        with jsonlines.open(osp.join('./annt_first_try', out_file), mode='a') as writer:
            writer.write(obj)
        cnt += 1

        if cnt > 500:
            break