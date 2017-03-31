import numpy as np
import cv2
from matplotlib import pyplot as plt


class RVIK(object):
    def __init__(self, config = None):
        if config:
            self.setConfig(config)

    def setConfig(self, config):
        '''Set the configuration for the solver, and recalculate the IK solution set'''
        self.config = config
        self.calculate()

    def calculate(self):
        '''Calculates the set of IK solutions, revealing the reachable area'''
        # Config
        elevator_length = self.config.elevator_length
        forearm_length = self.config.forearm_length
        linkage_length = self.config.linkage_length
        lower_actuator_length = self.config.lower_actuator_length
        upper_actuator_length = self.config.upper_actuator_length
        wrist_length = self.config.wrist_length

        # The maximum possible distance
        self.width = int(np.ceil((elevator_length + forearm_length)/4))
        self.height = 2*self.width
        goals = np.zeros((self.width,self.height,2))
        for j in range(self.height):
            for i in range(self.width):
                goals[i,j]=[i*4, (-j+self.height/2)*4]

        valid = np.ones((self.width,self.height), dtype=bool)
        dists = np.linalg.norm(goals, axis=2)

        # close enough for intersection
        valid &= dists < forearm_length + elevator_length
        valid &= dists > 0
        # intersect
        a = (forearm_length**2 - elevator_length**2 + dists**2) / (dists*2)
        h = np.sqrt(forearm_length**2 - a**2)
        p2 = goals + (np.dstack([a,a])*(-goals)) / np.dstack([dists,dists])
        i1 = np.array(p2)
        # [:, :, ::-1] flips x and y coords
        # dstack is a lazy way to get the scalar h/dists to multiply across the vectors
        # - it just doubles up the scalar to e.g. [h, h] so becomes [h,h]*[xi,yi]
        i1 += [1,-1] * np.dstack([h,h]) * (-goals)[:,:,::-1] / np.dstack([dists,dists])
        i2 = np.array(p2)
        i2 += [-1,1] * np.dstack([h,h]) * (-goals)[:,:,::-1] / np.dstack([dists,dists])
        # Pick the higher solutions as the elbow points
        elbows = np.zeros((self.width, self.height, 2))
        for j in range(self.height):
            for i in range(self.width):
                if i1[i, j, 1] > i2[i, j, 1]:
                    elbows[i, j] = i1[i, j]
                else:
                    elbows[i, j] = i2[i, j]

        # Get the elevator and forearm vectors
        elevator_vecs = elbows
        forearm_vecs = goals - elbows
        elbows = np.ma.masked_array(elbows, np.isnan(elbows))
        # goals = np.ma.masked_array(goals, elbows.mask)

        # Show the elevator/forearm angle
        # Need to calculate angle from vertical; can be negative
        vertical = np.array([0,1])
        horizontal = np.array([1,0])
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
        if len(contours) > 0:
            self.contour = contours[0] * 4
        else:
            self.contour = None

        self.valid_points = np.sum(ok)
        self.valid_indices = np.dstack(np.where(ok)).reshape(self.valid_points, 2)
        print(self.valid_indices.shape)
        print(self.valid_points)
