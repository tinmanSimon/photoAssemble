
import os
from PIL import Image, ImageStat
import imagehash
import numpy as np
import random
from tempfile import TemporaryFile
imagePath = 'D:/pictures/lastYear/'
reducedImagesPath = 'D:/pictures/reduced/'
pixelatedImagesPath = 'D:/pictures/pixelated/'
testImagesPath = 'D:/pictures/test/'
saveImagePath = 'D:/pictures/saved/'
processedImgSize = (100, 100)

def getImages(path, reSizeValue = None):
    res = []
    counter = 0
    for file in os.listdir(path):
         if os.path.isfile(os.path.join(path, file)):
             #print(counter)
             counter += 1
             #if counter == 100: return res
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

def reduceImagesQualityAndSave(imagePath, saveDirPath):
    images = getImages(imagePath, processedImgSize)
    for i, img in enumerate(images):
        img.save(saveDirPath + str(i) + ".png", optimize=True)

def pixelateImages():
    images = getImages(reducedImagesPath, (16, 16))
    for i, img in enumerate(images):
        img = img.resize(processedImgSize, Image.Resampling.NEAREST)
        img.save(pixelatedImagesPath + str(i) + ".png", optimize=True)

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

def matchRows(targetPixelsRow, assemblePixels, useDistinctImages = False):
    newImgRow, impossibleVal = [], (-500, -500, -500)
    for targetPixel in targetPixelsRow:
        matchI, matchDiff = -1, -1
        for j, assemblePixel in enumerate(assemblePixels):
            curDiff = sum([abs(a - b) ** 2 for a, b in zip(targetPixel, assemblePixel)])
            if matchI < 0 or curDiff < matchDiff:
                matchDiff = curDiff
                matchI = j 
        if useDistinctImages: assemblePixel[matchI] = impossibleVal
        newImgRow.append(matchI)
    return newImgRow

def assembleImg(targetImg, assembleImgLib, saveFile):
    img = getTargetImg(targetImg)
    targetGrid = getCroppedImages(img, 10)
    targetGridPixels = [[tuple(int(fVal) for fVal in ImageStat.Stat(img.resize((16, 16))).mean) for img in row] for row in targetGrid]
    assembleImages = getImages(assembleImgLib, (16, 16))
    avgAssemblePixels = [tuple(int(fVal) for fVal in ImageStat.Stat(img).mean) for img in assembleImages]
    rowImgs = []
    reducedImages = getImages(assembleImgLib)
    print("iamges loaded, matching pixels")
    for i, row in enumerate(targetGridPixels):
        print("finished", i, "out of", len(targetGridPixels))
        newImgRow = matchRows(row, avgAssemblePixels)
        rowImgs.append(concatRightImgArr([reducedImages[i] for i in newImgRow]))
    newImg = concatDownImgArr(rowImgs)
    newImg.save(saveFile)

def pixelateImg(targetImg, saveFile, imgSize):
    img = getTargetImg(targetImg)
    targetGrid = getCroppedImages(img, 10)
    targetGridPixels = [[tuple(int(fVal) for fVal in ImageStat.Stat(img.resize((16, 16))).mean) for img in row] for row in targetGrid]
    rowImgs = []
    print("iamges loaded, matching pixels")
    for i, row in enumerate(targetGridPixels):
        print("finished", i, "out of", len(targetGridPixels))
        rowImgs.append(concatRightImgArr(Image.new("RGB", imgSize, tuple(v + random.randint(0, 20) for v in pixel)) for pixel in row))
    newImg = concatDownImgArr(rowImgs)
    newImg.save(saveFile)

assembleImg('D:/pictures/targetPic/marlo.png', 'D:/pictures/phoneReduced/', 'D:/pictures/saved/marlo2.png')
#pixelateImg('D:/pictures/targetPic/zhuge3.jpg', 'D:/pictures/saved/zhuge4.png', (40, 40))

