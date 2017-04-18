import numpy as np
import cv2
from matplotlib import pyplot as plt


class RVIK(object):
    def __init__(self, config = None, resolution = None, point = None):
        self.point_results = None
        if resolution is not None:
            self.resolution = resolution
        else:
            self.resolution = 200
            if point is not None:
                self.point_mode = True
                self.point = point
            else:
                self.point_mode = False
        if config is not None:
            self.setConfig(config)

    def setPoint(self, point):
        '''Sets a goal point to solve for, rather than solving the full range'''
        self.point_mode = True
        self.point = point
        self.calculate()

    def setConfig(self, config):
        '''Set the configuration for the solver, and recalculate the IK solution set'''
        self.config = config
        self.calculate()

    # @profile
    def calculate(self):
        '''Calculates the set of IK solutions, revealing the reachable area'''
        # Config
        elevator_length = self.config['elevator_length']
        forearm_length = self.config['forearm_length']
        linkage_length = self.config['linkage_length']
        lower_actuator_length = self.config['lower_actuator_length']
        upper_actuator_length = self.config['upper_actuator_length']
        wrist_length = self.config['wrist_length']

        # Generate goals (or just use point mode)
        if self.point_mode:
            goals = np.array([[self.point]])
            self.width = 1
            self.height = 1
        else:
            # The maximum possible distance
            max_dist = elevator_length + forearm_length
            self.width = self.resolution
            self.height = 2*self.width
            step = max_dist/self.resolution
            x = np.arange(self.width) * step
            y = (self.height / 2 - np.arange(self.height)) * step
            goals = np.dstack(np.meshgrid(y, x))[:,:,::-1]

        dists = np.linalg.norm(goals, axis=2)

        # close enough for intersection
        # intersect
        stack_dists = np.dstack([dists,dists])
        a = (forearm_length**2 - elevator_length**2 + dists**2) / (dists*2)
        h = np.sqrt(forearm_length**2 - a**2)
        p2 = goals + (np.dstack([a,a])*(-goals)) / stack_dists
        i1 = np.array(p2)
        # [:, :, ::-1] flips x and y coords
        # dstack is a lazy way to get the scalar h/dists to multiply across the vectors
        # - it just doubles up the scalar to e.g. [h, h] so becomes [h,h]*[xi,yi]
        stack_h = np.dstack([h,h])
        flipped_goals = (-goals)[:,:,::-1]
        i_chunk = stack_h * flipped_goals / stack_dists
        i1 += [1,-1] * i_chunk
        i2 = np.array(p2)
        i2 += [-1,1] * i_chunk
        # Pick the higher solutions as the elbow points
        # elbows = np.zeros((self.width, self.height, 2))
        # for j in range(self.height):
        #     for i in range(self.width):
        #         if i1[i, j, 1] > i2[i, j, 1]:
        #             elbows[i, j] = i1[i, j]
        #         else:
        #             elbows[i, j] = i2[i, j]
        i1_greater = i1[:,:,1] > i2[:,:,1]
        i1_greater = np.dstack([i1_greater, i1_greater])
        i2_greater = ~ i1_greater
        elbows = i1_greater * i1 + i2_greater * i2

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

        if self.point_mode:
            # In point mode we just package up the point's results
            # Calculate the actuator vector
            a = actuator_angles[0,0]
            lower_actuator = lower_actuator_length * np.array([np.sin(a), np.cos(a)])
            forearm = forearm_vecs[0,0]
            upper_actuator = elbows[0,0] - upper_actuator_length * forearm / np.linalg.norm(forearm)
            if ok[0,0]:
                # TODO: inverse load calculations
                # say load is 20N
                l = 20
                L = np.array([0, -l])
                x_p = upper_actuator_length
                x_l = forearm_length
                theta = forearm_angles[0,0] - np.pi/2
                # TODO: calculate linkage angle properly
                alpha = np.pi/2 - (forearm_angles[0,0] - elevator_angles[0,0])
                m_p = -(x_l * l * np.cos(theta))/(x_p * np.cos(alpha))
                P = np.array([np.sin(theta + alpha), np.cos(theta + alpha)]) * m_p
                F = -(P+L)
                elevator_torque = F[1] * (elbows[0,0,0]/1000)
                # TODO: update for non-parallel mechanism
                actuator_torque = m_p * (upper_actuator_length/1000)
                print('theta {0:.2f}, alpha {1:.2f}, Te {2:.2f}, Ta {3:.2f}'.format(theta/np.pi, alpha/np.pi, elevator_torque, actuator_torque))
                self.point_results = {
                    'ok' : True,
                    'elbow_pos' : elbows[0,0],
                    'goal_pos' : goals[0,0],
                    'lower_actuator' : lower_actuator,
                    'upper_actuator' : upper_actuator,
                    'P': P,
                    'L': L,
                    'F': F,

                }
            else:
                self.point_results = {'ok': False}

        else:
            # Contour-map the reachable region
            im2, contours, hierarchy = cv2.findContours(np.array(-ok, np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                self.contour = (contours[0] - [self.height/2, 0]) * step
            else:
                self.contour = None

            self.valid_points = np.sum(ok)
            self.valid_indices = np.dstack(np.where(ok)).reshape(self.valid_points, 2)
            # print(self.valid_indices.shape)
            # print(self.valid_points)
