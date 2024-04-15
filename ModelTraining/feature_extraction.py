import quat
import numpy as np
import math

class db:
    def __init__(self, positions, rotations, velocities, angular_velocities, parents, nframes, nranges, range_starts, range_stops):
        self.positions = positions
        self.rotations = rotations
        self.velocities = velocities
        self.angular_velocities = angular_velocities
        self.parents = parents
        self.nframes = nframes
        self.nranges = nranges
        self.range_starts = range_starts
        self.range_stops = range_stops

def build_feature_vector(db, position_features, velocity_features, weights):
    print("Building Feature Vector ...")

    nfeatures = len(position_features) * 3 + len(velocity_features) * 3 + 12
    features = np.zeros((db.nframes, 0))
    feature_offsets = []
    feature_scales = []

    print("Building Position Features ...")
    for i in range(len(position_features)):
        feature, feature_offset, feature_scale = get_position_feature(db,position_features[i], weights[0])
        features = np.concatenate((features, feature), axis=1)
        feature_offsets.append(feature_offset)
        feature_scales.append(feature_scale)

    print("Building Velocity Features ...")
    for i in range(len(velocity_features)):
        feature, feature_offset, feature_scale = get_velocity_feature(db, velocity_features[i], weights[1])
        features = np.concatenate((features, feature), axis=1)
        feature_offsets.append(feature_offset)
        feature_scales.append(feature_scale)

    print("Building Trajectory Features ...")
    feature, feature_offset, feature_scale = get_trajectory_position_feature(db, weights[2])
    features = np.concatenate((features, feature), axis=1)
    feature_offsets.append(feature_offset)
    feature_scales.append(feature_scale)

    feature, feature_offset, feature_scale = get_trajectory_direction_feature(db, weights[3])
    features = np.concatenate((features, feature), axis=1)
    feature_offsets.append(feature_offset)
    feature_scales.append(feature_scale)

    return features, feature_offsets, feature_scales


def get_position_feature(db, bone_index, weight):
    feature = np.zeros((db.nframes, 3))
    for i in range(db.nframes):
        bpos, brot = quat.forward_kinematics(db.positions[i], db.rotations[i], db.parents, bone_index)

        bpos = quat.mul_vec(quat.inv(db.rotations[i][0]), bpos - db.positions[i][0])

        feature[i, 0] = bpos[0]
        feature[i, 1] = bpos[1]
        feature[i, 2] = bpos[2] 

    feature, feature_offset, feature_scale = normalize_feature(feature, weight)
    return feature, feature_offset, feature_scale

def get_velocity_feature(db, bone_index, weight):
    feature = np.zeros((db.nframes, 3))
    for i in range(db.nframes):
        bpos, brot, bvel, bang = quat.forward_kinematics_velocities(db.positions[i], db.rotations[i], db.velocities[i], db.angular_velocities[i], db.parents, bone_index)

        bvel = quat.mul_vec(quat.inv(db.rotations[i][0]), bvel)

        feature[i, 0] = bvel[0]
        feature[i, 1] = bvel[1]
        feature[i, 2] = bvel[2] 

    feature, feature_offset, feature_scale = normalize_feature(feature, weight)
    return feature, feature_offset, feature_scale

def get_trajectory_position_feature(db, weight):
    feature = np.zeros((db.nframes, 6))
    for i in range(db.nframes):
        t0 = trajectory_clamp(db, i, 20)
        t1 = trajectory_clamp(db, i, 40)
        t2 = trajectory_clamp(db, i, 60)

        bpos0 = quat.mul_vec(quat.inv(db.rotations[i][0]), db.positions[t0][0] - db.positions[i][0])
        bpos1 = quat.mul_vec(quat.inv(db.rotations[i][0]), db.positions[t1][0] - db.positions[i][0])
        bpos2 = quat.mul_vec(quat.inv(db.rotations[i][0]), db.positions[t2][0] - db.positions[i][0])

        feature[i, 0] = bpos0[0]
        feature[i, 1] = bpos0[1]
        feature[i, 2] = bpos1[0]
        feature[i, 3] = bpos1[1]
        feature[i, 4] = bpos2[0]
        feature[i, 5] = bpos2[1]

    feature, feature_offset, feature_scale = normalize_feature(feature, weight)
    return feature, feature_offset, feature_scale

def get_trajectory_direction_feature(db, weight):
    feature = np.zeros((db.nframes, 6))
    for i in range(db.nframes):
        t0 = trajectory_clamp(db, i, 20)
        t1 = trajectory_clamp(db, i, 40)
        t2 = trajectory_clamp(db, i, 60)

        bdir0 = quat.mul_vec(quat.inv(db.rotations[i][0]), quat.mul_vec(db.rotations[t0][0], np.array([1, 0, 0])))
        bdir1 = quat.mul_vec(quat.inv(db.rotations[i][0]), quat.mul_vec(db.rotations[t1][0], np.array([1, 0, 0])))
        bdir2 = quat.mul_vec(quat.inv(db.rotations[i][0]), quat.mul_vec(db.rotations[t2][0], np.array([1, 0, 0])))

        feature[i, 0] = bdir0[0]
        feature[i, 1] = bdir0[1]
        feature[i, 2] = bdir1[0]
        feature[i, 3] = bdir1[1]
        feature[i, 4] = bdir2[0]
        feature[i, 5] = bdir2[1]

    feature, feature_offset, feature_scale = normalize_feature(feature, weight)
    return feature, feature_offset, feature_scale

def normalize_feature(feature, weight):
    # Calculate the mean of each feature across all frames
    feature_offset = np.mean(feature, axis=0)

    # Calculate the variance and then the standard deviation for each feature
    feature_scale = np.std(feature, axis=0)
    
    # Normalize the standard deviation by the total mean standard deviation divided by the weight
    std_mean = np.mean(feature_scale)  # Mean of standard deviations across features
    normalized_std = std_mean / weight
    feature_scale[:] = normalized_std  # Set all scale factors to the normalized standard deviation

    # Normalize each feature entry
    feature = (feature - feature_offset) / feature_scale

    return feature, feature_offset, feature_scale


def trajectory_clamp(db, frame, offset):
    for i in range(db.nranges):
        if frame >= db.range_starts[i] and frame < db.range_stops[i]:
            return clamp(frame + offset, db.range_starts[i], db.range_stops[i] - 1)
        

def clamp(x, min_val, max_val):
    return max(min_val, min(x, max_val))
