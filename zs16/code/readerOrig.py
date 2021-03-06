import csv
import cPickle as pickle
import numpy as np
import random, sys
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import precision_recall_fscore_support
import sys

def getInt(val):
	try:
		a = int(val)
	except ValueError:
		return "IGNORE"
	return a

def formatField(val):
	if ('Hospital ' in val):
		val = val.strip('Hospital ')
	elif ('Region ' in val):
		val = val.strip('Region ')
	elif ('District ' in val):
		val = val.strip('District ')
	elif ('Instrument ' in val):
		val = val.strip('Instrument ')
	return getInt(val)

def getGoldenFet(fetList, leftA, rightA, leftB, rightB):
	newFetList = list(fetList)
	for i in range(leftA, rightA, 2):
		for j in range(leftB, rightB):
			newFetList.append(fetList[i] * fetList[j])
	# newFetList = np.array(newFetList, dtype = np.uint8)
	newFetList = np.array(newFetList, dtype = np.int)
	return newFetList

def getGoldenX(X, leftA, rightA, leftB, rightB):
	Xn = []
	for i in range(X.shape[0]):
		Xn.append(getGoldenFet(X[i], leftA, rightA, leftB, rightB))
		print '\r', (i*(1.0))/(X.shape[0]),
	print 'COMPLETED'
	# Xn = np.array(Xn, dtype = np.uint8)
	Xn = np.array(Xn, dtype = np.int)
	return Xn

def getHospitalRegion():

	regionList = {}

	with open('../resources/Dataset/HospitalRevenue.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',')
		next(reader, None)
		for row in reader:
			fetList = []
			for i in range(3):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				fetList.append(tmpVal)
			if (len(fetList) < 2):
				continue

			regionList[fetList[0]] = fetList[1]

	csvfile.close()

	return regionList

def getHospitalProfile(fineFlag = False):
	popList = {}
	regionList = getHospitalRegion()

	with open('../resources/Dataset/HospitalProfiling.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',')
		next(reader, None)
		for row in reader:
			fetList = []
			for i in range(3):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				fetList.append(tmpVal)
			if (len(fetList) < 3):
				continue

			# Fine tune the district
			if (fineFlag):
				if (fetList[0] in regionList):
					fetList[1] += regionList[fetList[0]] * 100				

			fetList = np.array(fetList)
			tmpKey = (fetList[0], fetList[1])
			if (tmpKey in popList):
				popList[tmpKey] = max(popList[tmpKey], fetList[2])
			else:
				popList[tmpKey] = fetList[2]
	csvfile.close()

	# for k in popList.keys():
	# 	popList[k] /= 100
	# 	if (popList[k] > 255):
	# 		popList[k] = 255

	return popList

def getHospitalSales():

	popList = getHospitalProfile()

	saleListDetailed = set()
	saleListRough = set()
	with open('../resources/Dataset/HospitalRevenue.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',')
		next(reader, None)
		for row in reader:
			fetList = []
			for i in range(4):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				fetList.append(tmpVal)
			if (len(fetList) < 4):
				continue

			tmpKey = (fetList[0], fetList[2])
			if (tmpKey in popList):
				fetList[0] = popList[tmpKey]
				fetList[1] = 0
			else:
				fetList[0] = 0
				fetList[1] = 1

			tmpTupDetailed = (fetList[0], fetList[1], fetList[2], fetList[3])
			tmpTupRough = (fetList[0], fetList[1], fetList[3])

			saleListRough.add(tmpTupRough)
			saleListDetailed.add(tmpTupDetailed)

	csvfile.close()

	return saleListDetailed, saleListRough

def getTestSetAcc(clf, enc, popFlag = True, goldenFlag = False):

	if popFlag:
		popList = getHospitalProfile()

	dataList = []
	with open('../resources/Dataset/ProjectedRevenue.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',')
		next(reader, None)
		for row in reader:
			fetList = [-1]
			for i in range(3):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				if (i > 0):
					if (tmpVal >= enc.n_values_[i - 1]):
						tmpVal = enc.n_values_[i - 1] - 1
				fetList.append(tmpVal)
			if (len(fetList) < 4):
				continue

			if (popFlag):
				tmpKey = (fetList[1], fetList[2])
				if (tmpKey in popList):
					fetList[0] = popList[tmpKey]
					fetList[1] = 0
				else:
					# print tmpKey
					fetList[0] = 0
					fetList[1] = 1

			fetList = np.array(fetList)
			dataList.append(fetList)

	csvfile.close()

	X = np.array(dataList)
	
	if popFlag:
		Xt = enc.transform(X[:, 2:])
		Xt = np.hstack((X[:,:2], Xt))
	else:
		Xt = enc.transform(X)

	if goldenFlag:
		print Xt.shape
		Xt = getGoldenX(Xt, 2, 2 + enc.feature_indices_[1], 2 + enc.feature_indices_[0], 2 + min(enc.feature_indices_[0] + 9, enc.feature_indices_[1]))
		print Xt.shape

	# Xt = scaler.transform(Xt)

	Y_pred = clf.predict(Xt)

	# Y_pred = clf.predict_proba(Xt)
	# for i in range(Y_pred.shape[0]):
	# 	if (Y_pred[i][1] > 0.9):
	# 		Y_pred_new[i] = 1
	# 	else:
	# 		Y_pred_new[i] = 0
	# Y_pred = Y_pred_new

	print precision_recall_fscore_support([1] * Y_pred.shape[0], Y_pred, average = 'binary')

	return Xt

def getDataXY(currYearFlag = False, popFlag = False):

	if popFlag:
		popList = getHospitalProfile()

	dataList = []
	with open('../resources/Dataset/HospitalRevenue.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',')
		next(reader, None)
		for row in reader:
			fetList = []
			for i in range(17):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				fetList.append(tmpVal)
			if (len(fetList) < 17):
				continue

			if (popFlag):
				tmpKey = (fetList[0], fetList[2])
				if (tmpKey in popList):
					fetList[0] = popList[tmpKey]
					fetList[1] = 0
				else:
					# print tmpKey
					fetList[0] = 0
					fetList[1] = 1
					# print 'OMG'

			fetList = np.array(fetList)
			dataList.append(fetList)
	csvfile.close()

	if (currYearFlag):

		# dataList.extend(dataList)
		# dataList.extend(dataList)
		# dataList.extend(dataList)

		currDataList = []
		with open('../resources/Dataset/ProjectedRevenue.csv', 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter = ',')
			next(reader, None)
			for row in reader:
				fetList = []
				for i in range(1):
					tmpVal = formatField(row[i])
					if (tmpVal == "IGNORE"):
						break
					fetList.append(tmpVal)
				for i in range(1, 2):
					fetList.append(-1)
				for i in range(1, 3):
					tmpVal = formatField(row[i])
					if (tmpVal == "IGNORE"):
						break
					fetList.append(tmpVal)
				for i in range(4, 16):
					fetList.append(-1)
				for i in range(3, 4):
					tmpVal = formatField(row[i])
					if (tmpVal == "IGNORE"):
						break
					fetList.append(tmpVal)

				if (len(fetList) < 17):
					continue

				if (popFlag):
					tmpKey = (fetList[0], fetList[2])
					if (tmpKey in popList):
						fetList[0] = popList[tmpKey]
						fetList[1] = 0
					else:
						# print tmpKey
						fetList[0] = 0
						fetList[1] = 1
						# print 'OMG'

				fetList = np.array(fetList)
				currDataList.append(fetList)
		csvfile.close()
		# currDataList.extend(currDataList)
		# currDataList.extend(currDataList)
		# currDataList.extend(currDataList)
		currDataList = np.array(currDataList)

		dataList = np.array(dataList)

		print dataList.shape
		print currDataList.shape

		dataList = np.vstack((dataList, currDataList))

	dataList = np.array(dataList, dtype = np.int)

	print dataList.shape

	if (popFlag):
		X = dataList[:,[0,1,2,3]]
	else:
		X = dataList[:,[0,2,3]]

	# Change this to modify the features chosen
	Y = dataList[:,-1:]

	print X.shape
	print Y.shape

	return X, Y

def getDataProjection(encoder, popFlag = False):

	if popFlag:
		popList = getHospitalProfile()

	currDataList = []
	with open('../resources/Dataset/ProjectedRevenue.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',')
		next(reader, None)
		for row in reader:
			fetList = []
			for i in range(1):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				fetList.append(tmpVal)
			for i in range(1, 2):
				fetList.append(-1)

			for i in range(1, 3):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				if (tmpVal >= encoder.n_values_[i - 1]):
					tmpVal = encoder.n_values_[i - 1] - 1
				fetList.append(tmpVal)
			for i in range(4, 16):
				fetList.append(-1)

			for i in range(3, 4):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				fetList.append(tmpVal)

			if (len(fetList) < 17):
				continue

			if (popFlag):
				tmpKey = (fetList[0], fetList[2])
				if (tmpKey in popList):
					fetList[0] = popList[tmpKey]
					fetList[1] = 0
				else:
					fetList[0] = 0
					fetList[1] = 1

			fetList = np.array(fetList)
			currDataList.append(fetList)
	csvfile.close()
	currDataList = np.array(currDataList)

	dataList = np.array(currDataList, dtype = np.int)

	print dataList.shape

	if (popFlag):
		X = dataList[:,[0,1,2,3]]
	else:
		X = dataList[:,[0,2,3]]

	# Change this to modify the features chosen
	Y = dataList[:,-1:]

	print X.shape
	print Y.shape

	return X, Y

def generatePredFileC(clfBuy, clfRevenue, encBuy, encRev, scalerBuy, scalerRev, popFlag = True, newHeuristic = False, goldenFlag = False):
	fieldList = []
	dataList = []

	print 'HERE IT IS'
	print encBuy.n_values_
	print encRev.n_values_

	if popFlag:
		popList = getHospitalProfile()

	if newHeuristic:
		saleListDetailed, saleListRough = getHospitalSales()

	with open('../resources/Dataset/Solution.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',')
		next(reader, None)
		for row in reader:
			fetList = [-1]
			for i in range(3):
				tmpVal = formatField(row[i])
				if (tmpVal == "IGNORE"):
					break
				if (i > 0):
					if (tmpVal >= encBuy.n_values_[i - 1]):
						tmpVal = encBuy.n_values_[i - 1] - 1
					if (tmpVal >= encRev.n_values_[i - 1]):
						tmpVal = encRev.n_values_[i - 1] - 1
				fetList.append(tmpVal)
			if (len(fetList) < 4):
				continue

			if (popFlag):
				tmpKey = (fetList[1], fetList[2])
				if (tmpKey in popList):
					fetList[0] = popList[tmpKey]
					fetList[1] = 0
				else:
					# print tmpKey
					fetList[0] = 0
					fetList[1] = 1

			fieldList.append(row)
			fetList = np.array(fetList)
			dataList.append(fetList)

	csvfile.close()

	X = np.array(dataList)
	print X

	if popFlag:
		Xt_rev = encRev.transform(X[:, 2:])
		Xt_rev = np.hstack((X[:,:2], Xt_rev))
	else:
		Xt_rev = encRev.transform(X)

	if popFlag:
		Xt_buy = encBuy.transform(X[:, 2:])
		Xt_buy = np.hstack((X[:,:2], Xt_buy))
	else:
		Xt_buy = encBuy.transform(X)

	# Xt_buy = scalerBuy.transform(Xt_buy)
	# Xt_rev = scalerRev.transform(Xt_rev)

	# Xt_buy = Xt_buy[:10000]

	if goldenFlag:
		print Xt_buy.shape
		Xt_buy = getGoldenX(Xt_buy, 2, 2 + encBuy.feature_indices_[1], 2 + encBuy.feature_indices_[0], 2 + min(encBuy.feature_indices_[0] + 9, encBuy.feature_indices_[1]))
		print Xt_buy.shape

	Y_pred_Revenue = clfRevenue.predict(Xt_rev)

	# Xt_buy = Xt_buy[:10000]

	print Xt_buy.shape

	Y_pred_Buy = clfBuy.predict_proba(Xt_buy)
	# Y_pred_Buy = clfBuy.predict(Xt_buy)

	# for t in list(Y_pred_Buy)[:100]:
	# 	print t

	with open('../resources/Dataset/SolutionMineAltOrig.csv', 'wb') as csvfile:
		gtwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
		gtwriter.writerow(['Hospital_ID', 'District_ID', 'Instrument_ID', 'Buy_or_not', 'Revenue'])
		for i in range(0, len(fieldList)):
			buyFlag = Y_pred_Buy[i][1]
			band = 0.3

			if (newHeuristic):
				band = 0
				tmpTupDetailed = (X[i][0], X[i][1], X[i][2], X[i][3])
				tmpTupRough = (X[i][0], X[i][1], X[i][3])
				if (tmpTupDetailed in saleListDetailed):
					band += 0.15
				elif (tmpTupRough in saleListRough):
					band -= 0.2
				else:
					band += 0.3

			if (buyFlag > 0.6 + band):
				buyFlag = 1
			else:
				buyFlag = 0
			gtwriter.writerow([fieldList[i][0], fieldList[i][1], fieldList[i][2], buyFlag, int( buyFlag * int(Y_pred_Revenue[i]))])
	csvfile.close()

def oneHot(X):
	encoder = OneHotEncoder(sparse = False)
	encoder.fit(X)
	return encoder

if __name__ == "__main__":
	X, Y = getDataXY()
	encoder = oneHot(X)
	Xt = encoder.transform(X)
	print Xt.shape
