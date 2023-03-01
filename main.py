
import os
from PIL import Image
imagePath = 'C:\\Users\\wudis\\OneDrive\\currentPC\\Pictures\\tmp\\'
saveImagePath = 'C:/Users/wudis/OneDrive/currentPC/Documents/python/photoAssemble/saved'

def getImages(path):
    res = []
    for file in os.listdir(path):
         if os.path.isfile(os.path.join(path, file)):
            res.append(path + file)
    return [Image.open(file) for file in res]

def concatRight(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def concatDown(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

# expecting a Pillow Image object
def getCroppedImages(image, croppedLen):
    w, h = image.size
    res = []
    curh, curw = 0, 0
    while curh < h:
        curw = 0
        while curw < w:
            # todo crop
            croppedImg = image.crop((curw, curh, curw + croppedLen, curh + croppedLen))
            if h < croppedLen or curw < croppedLen:
                croppedImg.resize((croppedLen, croppedLen))
            res.append(croppedImg)
            curw += croppedLen
        curh += croppedLen
    return res


def saveImgs(dir, images):
    for i, image in enumerate(images):
        image.save(dir + "/" + str(i) + ".png")

images = getImages(imagePath)
#images[0].show()
croppedImages = getCroppedImages(images[0], 800)
saveImgs(saveImagePath, croppedImages)
print(len(images))

