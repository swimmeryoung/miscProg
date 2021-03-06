import numpy as np
from skvideo.io import VideoCapture
import cv2
import skimage
import os
from faceDetect import *
from dataProcess import *

def PlayVideo(fileName, redFact = 0.5):
	'''
	Plays video using opencv functions
	Press 'q' to stop in between
	returns None
	'''
	cap = VideoCapture(fileName)
	cap.open()
	while True:
		retval, image = cap.read()
		print len(image), len(image[0])
		if not retval:
			break
		image = cv2.resize(image, None, fx=redFact, fy=redFact)
		image = image[:,:,::-1]
		cv2.imshow('frame',image)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()

def GetFrames(fileName, redFact = 0.5, skipLength = 1, debug = False):
	'''
	returns numpy array of frames
	'''
	cap = VideoCapture(fileName)
	cap.open()

	frameList = []
	cnt = -1

	if debug:
		print "Started creating Frame List"

	while True:
		retval, image = cap.read()
		cnt = (cnt+1)%skipLength
		if (cnt != 0):
			continue
		if not retval:
			break
		image = cv2.resize(image, None, fx=redFact, fy=redFact)
		image = image[:,:,::-1]
		image = np.array(image, dtype = np.uint8)
		frameList.append(image)
	cap.release()

	if debug:
		print "Finished creating Frame List"

	frameList = np.array(frameList)
	return frameList

if __name__ == "__main__":
	videoPath = '../training/download_train-val/trainFiles/'
	vidNames = os.listdir(videoPath)
	vidNames = [x for x in vidNames if x.endswith(".mp4")]
	fileName = vidNames[0]
	# fileName = '8XBprf4NyOg.001.mp4'
	# PlayVideo(videoPath+fileName)

	# savedVidPath = 'KORA'
	savedVidPath = 'tmpData/tmpVid'
	savedPicPath = 'tmpData/tmpPic.jpg'

	frameList = None
	if (not os.path.isfile(savedVidPath + '.npy')):
		frameList = GetFrames(videoPath+fileName, redFact = 0.5, skipLength = 5)
		# np.save(savedVidPath, frameList)
	else:
		frameList = np.load(savedVidPath+'.npy')

	# DetectFace(frameList[0])
	# DrawFace(frameList[0])
	DetectFaceInList(frameList, None, True)
	# DetectFaceLandmarksInList(frameList, None, None)
	# DetectFaceInListDlib(frameList, None, 2, True)
	# cv2.imwrite(savedPicPath, frameList[0])