
import os
from PIL import Image, ImageStat
import imagehash
import glob
import numpy as np
import cv2
import colour
from tempfile import TemporaryFile
imagePath = 'D:/pictures/lastYear/'
reducedImagesPath = 'D:/pictures/reduced/'
pixelatedImagesPath = 'D:/pictures/pixelated/'
saveImagePath = 'D:/pictures/saved/'

def getImages(path, reSizeValue = None):
    res = []
    counter = 0
    for file in os.listdir(path):
         if os.path.isfile(os.path.join(path, file)):
             print(counter)
             counter += 1
             img = Image.open(path + file)
             if reSizeValue: img = img.resize(reSizeValue)
             res.append(img)
    return res

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

def saveArrayToFile(arr, fileName):
    with open(fileName, 'wb') as f:
        np.save(f, np.array(arr))

def hashImagesLibAndSave():
    images = getImages(pixelatedImagesPath)
    imagehashvals = [imagehash.average_hash(img) for img in images]
    saveArrayToFile(imagehashvals, 'imagesHash.npy')
    return imagehashvals

def loadArrayFromFile(fileName):
    with open(fileName, 'rb') as f:
        return np.load(f, allow_pickle=True)

def test_saveSimilarImages(imageHashVals):
    threshold = 3
    similarImages = []
    for i in range(len(imageHashVals)):
        for j in range(i + 1, len(imageHashVals)):
            if imageHashVals[i] - imageHashVals[j] < threshold:
                similarImages.append((i, j))
    saveArrayToFile(similarImages, 'similarImgs.npy')
    return similarImages

def test_getSimilarImages():
    return loadArrayFromFile('similarImgs.npy')

def reduceImagesQualityAndSave():
    images = getImages(imagePath, (100, 100))
    for i, img in enumerate(images):
        img.save(reducedImagesPath + str(i) + ".png", optimize=True)

def pixelateImages():
    images = getImages(reducedImagesPath, (16, 16))
    for i, img in enumerate(images):
        img = img.resize((100, 100), Image.Resampling.NEAREST)
        img.save(pixelatedImagesPath + str(i) + ".png", optimize=True)



images = getImages(reducedImagesPath, (16, 16))
res = [ImageStat.Stat(img).mean for img in images]
print(res[:10])

#reduceImagesQualityAndSave()
#pixelateImages()

#imagehashvals =hashImagesLibAndSave()
#imagehashvals = loadArrayFromFile('imagesHash.npy')


#similarImages = test_saveSimilarImages(imageHashVals)
#similarImages = test_getSimilarImages()

#similarimages = [i for i, a in enumerate(imagehashvals) if a - imagehashvals[1] < 5]
#print(similarimages)
#images = getImages(reducedImagesPath)
#i = 50
#images[simFarIndexImages[i][0]].show()
#images[simFarIndexImages[i][1]].show()
#images[2].show()




#print("similarImages:")
#print(similarImages)
#saveArrayToFile([str(a[0]) + " " + str(a[1]) + "\n" for a in similarImages], "similarImages.txt")

#images[0].show()
#croppedImages = getCroppedImages(images[0], 800)
#saveImgs(saveImagePath, croppedImages)
#print(len(images))

