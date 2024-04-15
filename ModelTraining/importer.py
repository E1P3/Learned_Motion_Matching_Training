import struct
import numpy as np

filename = "../ThesisStuff/Output/lafan_walk_1_subject_1.bin"
boneFileName = "../ThesisStuff/Output/boneParentInfo.bin"

def readAnimDataFile(filename):
    Y = np.fromfile(filename, dtype=np.float32)
    frameCount = int(Y[0])
    boneCount = int(Y[1])
    Y = Y[2:]
    return Y.reshape((frameCount, boneCount, 7)), frameCount, boneCount

def readBoneParents(filename):
    B = np.fromfile(filename, dtype=np.int32)
    boneCount = B[0]
    B = B[1:]
    return B, boneCount