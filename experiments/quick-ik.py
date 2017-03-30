import numpy as np
import cv2
from matplotlib import pyplot as plt

from util import *
from solvers import Circle
# from litearm import ArmController

width = 800
height = 800
goals = np.zeros((width,height,2))
for j in range(height):
    for i in range(width):
        goals[i,j]=[i+18.71, -j+height/2]

# Config
origin=np.array([18.71,0])
elevator_length = 148.4
forearm_length = 160.0
linkage_length = 155
lower_actuator_length = 65
upper_actuator_length = 54.4
wrist_length = 90.52

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

# print(elbows)
elbows = np.ma.masked_array(elbows, np.isnan(elbows))
# goals = np.ma.masked_array(goals, elbows.mask)

# plt.scatter(elbows[:, :, 0], elbows[:, :, 1], s=1)
# plt.scatter(goals[:, :, 0], goals[:, :, 1], s=1)
# plt.grid(True)
# plt.show()

# Show the elevator/forearm angle
# Need to calculate angle from vertical; can be negative
elevator_norms = elevator_vecs/elevator_length
vdots = np.inner(elevator_norms, vertical)
hdots = np.inner(elevator_norms, horizontal)
elevator_angles = np.arccos(vdots) * ((hdots > 0)*2 - 1)
# convert to servo setting
elevator_servos = (np.degrees(elevator_angles) - 178.21) * -1
# hacky but it works - divide by zero to clear out-of-range areas
elevator_servos /= (np.logical_and(elevator_servos > 60, elevator_servos < 210)*1)

forearm_norms = forearm_vecs/forearm_length
vdots = np.inner(forearm_norms, vertical)
hdots = np.inner(forearm_norms, horizontal)
forearm_angles = np.arccos(vdots) * ((hdots > 0)*2 - 1)
elevator_ok = (np.logical_and(elevator_servos > 60, elevator_servos < 210)*1)
forearm_ok = (np.logical_and(forearm_angles > 0, forearm_angles < 180)*1)
#img = np.logical_and(forearm_vecs[:,:,0] > 0, elevator_vecs[:,:,0] > 0)

# Elevator-forearm angle (elbow angle)
# Element-wise dot product
elbow_angles = np.arccos(np.einsum("ijk, ijk -> ij", elevator_norms, forearm_norms))

# Base angles are between the elevators and actuators (NOT the forearms!)
A = linkage_length
B = upper_actuator_length
C = elevator_length
D = lower_actuator_length
# Repeated application of cosine rule yields the forearm angle
# Y is a diagonal across the irregular quatrilateral (opposite
# desired)
Ysq = C**2 + B**2 - 2*C*B*np.cos(elbow_angles)
Y = np.sqrt(Ysq)
# foo and bar are the two angles adjacent to Y in the quat
cosFoo = np.clip((Ysq + D**2 - A**2) / (2*Y*D), -1, 1)
cosBar = np.clip((Ysq + C**2 - B**2) / (2*Y*C), -1, 1)
foo = np.arccos(cosFoo)
bar = np.arccos(cosBar)
# together they form the angle between the elevator and actuator
base_angles = foo + bar
# Actuator angles are then just the elevator - the base angle
actuator_angles = elevator_angles - base_angles

# Constraints
# limit actuator servo angles
actuator_servos = (np.degrees(actuator_angles) + 204.78)
actuator_ok = (actuator_servos > 100)*1 * (actuator_servos < 250)*1
# diff angle
base_ok = (np.degrees(base_angles) > 44)*1 *(np.degrees(base_angles) < 175)*1
# forearm angle
forearm_ok = (np.degrees(forearm_angles) > 80)*1 * (np.degrees(forearm_angles) < 200)*1
# elbow angle
elbow_ok = (np.degrees(elbow_angles) > 10)*1


ok = elevator_ok*forearm_ok*actuator_ok*base_ok*forearm_ok*elbow_ok
# Contour-map the reachable region
im2, contours, hierarchy = cv2.findContours(np.array(-ok, np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print(contours[0])

# Mask out unreachable goals and plot
ok = -1*(ok-1)
goals = np.ma.masked_array(goals, np.dstack([ok,ok]))

plt.clf()
extent = [18.71+wrist_length,818.71+wrist_length,-400,400]
# plt.imshow(ok.T)
# plt.scatter(origin[0], origin[1])
# plt.scatter(goals[:, :, 0], goals[:, :, 1], s=1)
# plt.imshow(elevator_servos.T, extent=extent)
# plt.imshow(np.degrees(elbow_angles).T, extent=extent)
# plt.imshow(np.degrees(base_angles).T, extent=extent)
# plt.imshow(actuator_servos.T, extent=extent)
plt.imshow(ok.T, extent=extent)
# plt.imshow(im2.T, extent=extent)
plt.show()
