import quat
from importer import readAnimDataFile
import numpy as np
from train_common import load_features

x_bad = [150.1072, -92.0245, 184.3032, -0.4806652, 0.4731091, -0.5295398, 0.5145059]
x_good = [150.1072, 184.3032, 92.0245, -0.70369226, -0.03990254, -0.70897985, 0.023928981]


xpos1 = np.array(x_bad[:3])
xrot1 = np.array(x_bad[3:])
xpos2 = np.array(x_good[:3])
xrot2 = np.array(x_good[3:])

xrot3 = quat.mul(xrot1, quat.from_angle_axis(np.pi/2, np.array([0, 0, 1])))
xpos3 = quat.mul_vec(quat.from_angle_axis(-np.pi/2, np.array([1, 0, 0])), xpos1)
print(xrot3)
print(xpos3)