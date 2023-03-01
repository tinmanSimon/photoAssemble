
import os
imagePath = r'C:\Users\wudis\OneDrive\currentPC\Pictures\tmp'

def getImages(path):
    res = []
    for file in os.listdir(path):
         if os.path.isfile(os.path.join(path, file)):
            res.append(file)
    return res

images = getImages(imagePath)
#print(images)

