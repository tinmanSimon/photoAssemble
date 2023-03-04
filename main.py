
import os
from PIL import Image, ImageStat
import numpy as np
import random

def getImages(path, reSizeValue = None):
    res = []
    for file in os.listdir(path):
         if os.path.isfile(os.path.join(path, file)):
             img = Image.open(path + file)
             if reSizeValue: img = img.resize(reSizeValue)
             res.append(img)
    return res

def concatRight(im1, im2):
    if im1 == None: return im2
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def concatDown(im1, im2):
    if im1 == None: return im2
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

# expecting a Pillow Image object, returns a 2D array of cropped images
def getCroppedImages(image, croppedW, croppedH = -1):
    w, h = image.size
    curh, curw, grid = 0, 0, []
    if croppedH < 0: croppedH = croppedW
    while curh < h:
        curw, curRow = 0, []
        while curw < w:
            croppedImg = image.crop((curw, curh, curw + croppedW, curh + croppedH))
            if curw < croppedW or h < croppedH:
                croppedImg.resize((croppedW, croppedH))
            curRow.append(croppedImg)
            curw += croppedW
        curh += croppedH
        grid.append(curRow)
    return grid


def saveImgs(dir, images):
    for i, image in enumerate(images):
        image.save(dir + "/" + str(i) + ".png")

def saveArrayToFile(arr, fileName):
    with open(fileName, 'wb') as f:
        np.save(f, np.array(arr))

def hashImagesLibAndSave(imagesPath):
    images = getImages(imagesPath)
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

def reduceImagesQualityAndSave(imagePath, saveDirPath, processedImgSize = (100, 100)):
    images = getImages(imagePath, processedImgSize)
    for i, img in enumerate(images):
        img.save(saveDirPath + str(i) + ".png", optimize=True)

def pixelateImages(imagePath, saveDirPath, processedImgSize = (100, 100)):
    images = getImages(imagePath, (16, 16))
    for i, img in enumerate(images):
        img = img.resize(processedImgSize, Image.Resampling.NEAREST)
        img.save(saveDirPath + str(i) + ".png", optimize=True)

def getTargetImg(targetImage, resizedWidth = 1000):
    img = Image.open(targetImage)
    w, h = img.size
    newW, newH = resizedWidth, int(resizedWidth * h / w)
    img = img.resize((newW, newH))
    return img

def concatRightImgArr(arr):
    newImg = None
    for img in arr:
        newImg = concatRight(newImg, img)
    return newImg

def concatDownImgArr(arr):
    newImg = None
    for img in arr:
        newImg = concatDown(newImg, img)
    return newImg

def assembleRow(targetRowPixels, libPixels, useDistinctImages = False):
    newImgRow, impossibleVal = [], (-500, -500, -500)
    for targetPixel in targetRowPixels:
        matchI, matchDiff = -1, -1
        for j, libPixel in enumerate(libPixels):
            curDiff = sum([abs(a - b) ** 2 for a, b in zip(targetPixel, libPixel)])
            if matchI < 0 or curDiff < matchDiff:
                matchI, matchDiff = j, curDiff
        if useDistinctImages: libPixels[matchI] = impossibleVal
        newImgRow.append(matchI)
    return newImgRow

def assembleImg(params):
    img = getTargetImg(params["targetImg"])
    targetGrid = getCroppedImages(img, params["croppedImgSize"])
    targetGridAvgPixels = [[tuple(int(fVal) for fVal in ImageStat.Stat(img.resize(params["pixelCalculationSize"])).mean) for img in row] for row in targetGrid]
    libImages = getImages(params["imgLib"], params["pixelCalculationSize"])
    libPixels = [tuple(int(fVal) for fVal in ImageStat.Stat(img).mean) for img in libImages]
    reducedImages = getImages(params["imgLib"])
    print("iamges loaded, matching pixels")
    rowImgs = []
    for i, row in enumerate(targetGridAvgPixels):
        print("finished", i + 1, "out of", len(targetGridAvgPixels))
        newImgRow = assembleRow(row, libPixels, params["useDistinctImages"])
        rowImgs.append(concatRightImgArr([reducedImages[i] for i in newImgRow]))
    newImg = concatDownImgArr(rowImgs)
    newImg.save(params["saveFile"])

#reduceImagesQualityAndSave('D:/pictures/phone/', 'D:/pictures/phoneReduced/')
assembleImg({
    "targetImg": 'D:/pictures/targetPic/marlo.png', 
    "imgLib": 'D:/pictures/phoneReduced/', 
    "croppedImgSize": 20, #the smaller the value is, the more calculation it does, longer it takes but more details it has.
    "pixelCalculationSize": (16, 16), #resize it,
    "useDistinctImages": False,
    "saveFile": 'D:/pictures/saved/marlo2.png'
})    