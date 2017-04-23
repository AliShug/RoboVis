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
        elevator_length = self.config['elevator_length'].value
        forearm_length = self.config['forearm_length'].value
        linkage_length = self.config['linkage_length'].value
        lower_actuator_length = self.config['lower_actuator_length'].value
        upper_actuator_length = self.config['upper_actuator_length'].value
        wrist_length = self.config['wrist_length'].value
        actuator_torque = self.config['actuator_torque'].value
        elevator_torque = self.config['elevator_torque'].value
        min_load = self.config['min_load'].value

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
            self.scaling_factor = step
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

        forearm_dirs = forearm_vecs/forearm_length
        vdots = np.inner(forearm_dirs, vertical)
        hdots = np.inner(forearm_dirs, horizontal)
        forearm_angles = np.arccos(vdots) * ((hdots > 0)*2 - 1)
        elevator_ok = (np.logical_and(elevator_servos > 60, elevator_servos < 210)*1)
        forearm_ok = (np.logical_and(forearm_angles > 0, forearm_angles < 180)*1)

        # Elevator-forearm angle (elbow angle)
        # Element-wise dot product
        elbow_angles = np.arccos(np.einsum("ijk, ijk -> ij", elevator_norms, forearm_dirs))

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


        # Load calculations
        # Loads are calculated for the actuator and elevator servos, under the
        # assumption of a static resting system where the other servo is holding
        # steady.
        x_p = upper_actuator_length/1000
        x_l = forearm_length/1000
        x_e = elevator_length/1000
        x_a = lower_actuator_length/1000
        # Direction components for lower actuator and elevator, used to find
        # the moment of forces about these sections
        lower_a_x = np.sin(actuator_angles)
        lower_a_y = np.cos(actuator_angles)
        elevator_x = np.sin(elevator_angles)
        elevator_y = np.cos(elevator_angles)
        a = np.dstack([lower_a_x, lower_a_y])
        lower_actuators = a * x_a
        upper_actuators = elbows/1000 - x_p * forearm_dirs
        linkage_vecs = lower_actuators - upper_actuators
        linkage_dirs = linkage_vecs / (linkage_length/1000)
        # Angles
        thetas = forearm_angles - np.pi/2
        cos_alphas = np.einsum("ijk, ijk -> ij", linkage_dirs, forearm_dirs)
        alphas = np.arccos(cos_alphas) - np.pi/2
        # w' in calculations
        w = (x_l * np.cos(thetas)) / (x_p * np.cos(alphas))
        theta_sums = thetas + alphas
        sin_theta_sums = np.sin(theta_sums)
        cos_theta_sums = np.cos(theta_sums)
        actuator_loads = actuator_torque / (x_a * w * (cos_theta_sums*a[:,:,0] - sin_theta_sums*a[:,:,1]))
        z = w * sin_theta_sums * elevator_y - elevator_x * (w * cos_theta_sums + 1)
        elevator_loads = elevator_torque / (x_e * z)
        # We don't care about the direction of the torques
        actuator_loads = np.abs(actuator_loads)
        elevator_loads = np.abs(elevator_loads)
        loads = np.minimum(actuator_loads, elevator_loads)
        self.actuator_loads = actuator_loads
        self.elevator_loads = elevator_loads
        self.loads = loads

        load_ok = loads > min_load
        ok = elevator_ok*forearm_ok*actuator_ok*base_ok*forearm_ok*elbow_ok*load_ok
        self.reachable = ok

        if self.point_mode:
            # In point mode we just package up the point's results
            # Calculate the actuator vector
            a = actuator_angles[0,0]
            lower_actuator = lower_actuator_length * np.array([np.sin(a), np.cos(a)])
            forearm = forearm_vecs[0,0]
            upper_actuator = elbows[0,0] - upper_actuator_length * forearm / np.linalg.norm(forearm)
            if ok[0,0]:
                # say load is 20N
                l = loads[0,0]
                L = np.array([0, -l])
                # Divide by 1000 to convert units from mm to M
                x_p = upper_actuator_length/1000
                x_l = forearm_length/1000
                x_e = elevator_length/1000
                x_a = lower_actuator_length/1000
                theta = forearm_angles[0,0] - np.pi/2
                linkage = lower_actuator - upper_actuator
                linkage_dir = linkage/np.linalg.norm(linkage)
                forearm_dir = forearm/np.linalg.norm(forearm)
                alpha = np.arccos(linkage_dir.dot(forearm_dir)) - np.pi/2
                m_p = -(x_l * l * np.cos(theta))/(x_p * np.cos(alpha))
                P = np.array([np.sin(theta + alpha), np.cos(theta + alpha)]) * m_p
                F = -(P+L)
                # elevator = elevator_vecs[0,0]
                # elevator = elevator/np.linalg.norm(elevator)
                # elevator_torque = x_e * (- F[1]*elevator[0] + F[0]*elevator[1])
                # w = -m_p

                # print(np.linalg.norm(linkage))
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
                self.contours = []
                for contour in contours:
                    self.contours.append((contour - [self.height/2, 0]) * step)
            else:
                self.contour = None

            self.valid_points = np.sum(ok)
            self.valid_indices = np.dstack(np.where(ok)).reshape(self.valid_points, 2)
