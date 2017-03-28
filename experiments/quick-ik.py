import numpy as np
from matplotlib import pyplot as plt

from util import *
from solvers import Circle
# from litearm import ArmController

width = 300
height = 600
goals = np.zeros((width,height,2))
for j in range(height):
    for i in range(width):
        goals[i,j]=[i+40, -j+height/2]

origin=np.array([18.71,0])

elevator_length = 148.4
forearm_length = 160.0

valid=np.ones((width,height), dtype=bool)
centers = np.array(goals)
diff = centers - origin
dists = np.linalg.norm(diff, axis=2)

# close enough for intersection
valid &= dists < forearm_length + elevator_length
valid &= dists > 0
# intersect
a = (forearm_length**2 - elevator_length**2 + dists**2) / (dists*2)
h = np.sqrt(forearm_length**2 - a**2)
p2 = centers + (np.dstack([a,a])*(origin - centers)) / np.dstack([dists,dists])
i1 = np.array(p2)
# [:, :, ::-1] flips x and y coords
# dstack is a lazy way to get the scalar h/dists to multiply across the vectors
# - it just doubles up the scalar to e.g. [h, h] so becomes [h,h]*[xi,yi]
i1 += [1,-1] * np.dstack([h,h]) * (origin - centers)[:,:,::-1] / np.dstack([dists,dists])
i2 = np.array(p2)
i2 += [-1,1] * np.dstack([h,h]) * (origin - centers)[:,:,::-1] / np.dstack([dists,dists])
# Pick the higher solutions as the elbow points
elbows = np.zeros((width, height, 2))
for j in range(height):
    for i in range(width):
        if i1[i, j, 1] > i2[i, j, 1]:
            elbows[i, j] = i1[i, j]
        else:
            elbows[i, j] = i2[i, j]

# # Construct geometry of arm from IK state
# main_arm = self.ik.elbow - self.ik.originpl
# arm_vert_angle = sigangle(main_arm, vertical)
# forearm = self.ik.wristpl - self.ik.elbow
# elbow_angle = angle_between(main_arm, forearm)
# # Solve actuator angle for given elbow angle
# # Base angle is between the main arm and actuator
# base_angle = self.physsolver.inverse_forearm(elbow_angle)
# actuator_angle = arm_vert_angle - base_angle

# def sigangle(v1, v2):
#     """Signed angle between two vectors (-ve if v1 is CCW from v2)"""
#     v1_u = normalize(v1)
#     v2_u = normalize(v2)
#     ang = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
#     # Right-angle to v2
#     perp = [v2_u[1], -v2_u[0]]
#     # Check handedness
#     if np.dot(v1_u, perp) < 0:
#         return -ang
#     else:
#         return ang

# print('my dist={0}'.format(dists))
# print('my a={0}'.format(a))
# print('my h={0}'.format(h[0,0]))
# print('my p2={0}'.format(p2[0,0]))
# print('my i1={0}'.format(i1[0,0]))
# print(origin-centers)
# c1 = Circle(origin, elevator_length)
# c2 = Circle([250,40], forearm_length)
# c2.intersect(c1)

# Get the elevator and forearm vectors
elevator_vecs = elbows - origin
forearm_vecs = goals - elbows

print(elbows)
elbows = np.ma.masked_array(elbows, np.isnan(elbows))
goals = np.ma.masked_array(goals, elbows.mask)

plt.scatter(elbows[:, :, 0], elbows[:, :, 1], s=1)
# plt.scatter(goals[:, :, 0], goals[:, :, 1], s=1)
plt.scatter(origin[0], origin[1])
plt.grid(True)
plt.show()
