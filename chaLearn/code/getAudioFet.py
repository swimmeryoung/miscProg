from dataProcess import *
import cPickle as pickle
import os
import sys

def getAudioFetA():
	'''
	Extracting audio features using the interspeech10 config
	Each audio track is broken into multiple overlapping segments, for which the features are computed
	The generated file for each video is a csv
	'''

	# fileName = '../training/training_gt.csv'
	# trueMap = getTruthVal(fileName)

	print 'Started extracting audio features'

	# videoPath = '/home/nishant/gitrepo/prog/chaLearn/training/download_train-val/trainFilesAudio/'
	videoPath = '/home/nishant/gitrepo/prog/chaLearn/training/download_test/testFilesAudio/'
	vidNames = os.listdir(videoPath)
	vidNames = [x for x in vidNames if x.endswith(".wav")]

	# videoPath = '/home/nishant/gitrepo/prog/chaLearn/training/download_train-val/validationFilesAudio/'
	# vidNamesTest = os.listdir(videoPath)
	# vidNamesTest = [x for x in vidNamesTest if x.endswith(".wav")]

	openSmilePath = '/home/nishant/Downloads/openSMILE-2.2rc1/'

	# vidNames.extend(vidNamesTest)

	# Initialize detectors, load it for face detection

	saveFetPath = '/home/nishant/gitrepo/prog/chaLearn/code/tmpData/audioFetA/'

	if not os.path.exists(saveFetPath):
	    os.makedirs(saveFetPath)
	vidNames = vidNames

	os.chdir(openSmilePath)

	for i in range(len(vidNames)):
		fileName = vidNames[i]

		if (os.path.isfile(saveFetPath+fileName.strip('.mp4.wav')+'.p')):
			continue

		fetList = getAudioFeatureAList(videoPath+fileName, segLen = 4, overlap = 3)
		savePath = saveFetPath + fileName.strip('.mp4.wav')
		pickle.dump(fetList, open(savePath+'.p', 'wb'))

		print ('\r'), ((i*(1.0))/len(vidNames)), 'part completed. Currently at file:', fileName,
		sys.stdout.flush()

	print '\n'

if __name__ == "__main__":
	getAudioFetA()