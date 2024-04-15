import importer
import quat
import numpy as np
from scipy.interpolate import griddata
import scipy.signal as signal
import scipy.ndimage as ndimage
import struct
from feature_extraction import db, build_feature_vector

def animation_mirror(lrot, lpos, parents, joints_mirror):

    mirror_pos = np.array([-1, 1, 1])
    mirror_rot = np.array([[-1, -1, 1], [1, 1, -1], [1, 1, -1]])

    grot, gpos = quat.fk(lrot, lpos, parents)

    gpos_mirror = mirror_pos * gpos[:,joints_mirror]
    grot_mirror = quat.from_xform(mirror_rot * quat.to_xform(grot[:,joints_mirror]))
    
    return quat.ik(grot_mirror, gpos_mirror, parents)

def saveAsBinary(filename, positions, rotations):
    #switch order of rotations from wxyz to xyzw
    xrot = quat.to_xform_xy(rotations)

    #flip from yup to z up
    rotations = quat.from_xform_xy(xrot)
    rotations = np.concatenate([rotations[:, :, 1:], rotations[:, :, 0:1]], axis=-1)

    with open(filename, "wb") as f:
        f.write(struct.pack("f", positions.shape[0]))
        f.write(struct.pack("f", positions.shape[1]))
        for i in range(positions.shape[0]):
            for j in range(positions.shape[1]):
                for k in range(3):
                    f.write(struct.pack("f", float(positions[i, j, k])))
                for k in range(4):
                    f.write(struct.pack("f", float(rotations[i, j, k])))

binaries_path = '../Animations/LAFAN1BIN/'

#files to create the database from, need to be preprocessed from the fbxtobinconverter

database_binaries = [
    (binaries_path + 'pushAndStumble1_subject5.bin', 194,  351),
    (binaries_path + 'run1_subject5.bin',             90, 7086),
    (binaries_path + 'walk1_subject5.bin',            80, 7791),
]

bone_info = binaries_path + "boneParentInfo.bin" # file containing bone hierarchy information
joints_mirror = np.array([0,5,6,7,8,1,2,3,4,9,10,11,12,13,18,19,20,21,14,15,16,17]) #mirror table for joints in the hierarchy

bone_positions = []
bone_velocities = []
bone_rotations = []
bone_angular_velocities = []
bone_parents = []
bone_names = []
    
range_starts = []
range_stops = []

contact_states = []

for filename, start, stop in database_binaries:
    for mirror in [False, True]:

        print('Loading "%s" %s...' % (filename, "(Mirrored)" if mirror else ""))

        Y, frameCount, boneCount = importer.readAnimDataFile(filename)
        B, bonecount = importer.readBoneParents(bone_info)
        if(start == -1 and stop == -1):
            start = 0
            stop = frameCount
        Y = Y[start:stop]
        positions = Y[:, :, :3]
        rotations = Y[:, :, 3:]

        #convert to z up coordinate system by multiplying the hip
        positions[:,0:1] = quat.mul_vec(quat.from_angle_axis(-np.pi/2, np.array([1, 0, 0])), positions[:,0:1])
        rotations[:,0:1] = quat.mul(rotations[:,0:1], quat.from_angle_axis(np.pi/2, np.array([0, 0, 1])))

        positions *= 0.01

        #switch order of rotations from xyzw to wxyz
        rotations = np.concatenate([rotations[:, :, 3:], rotations[:, :, :3]], axis=-1)

        if mirror:
            rotations, positions = animation_mirror(rotations, positions, B, joints_mirror)
            rotations = quat.unroll(rotations)

        nframes = Y.shape[0]
        nbones = Y.shape[1]

        # Supersample data to 60 fps
        original_times = np.linspace(0, nframes - 1, nframes)
        sample_times = np.linspace(0, nframes - 1, int(0.9 * (nframes * 2 - 1))) # Speed up data by 10%
        
        # This does a cubic interpolation of the data for supersampling and also speeding up by 10%
        positions = griddata(original_times, positions.reshape([nframes, -1]), sample_times, method='cubic').reshape([len(sample_times), nbones, 3])
        rotations = griddata(original_times, rotations.reshape([nframes, -1]), sample_times, method='cubic').reshape([len(sample_times), nbones, 4])
        
        # Need to re-normalize after super-sampling
        rotations = quat.normalize(rotations)

        global_rotations, global_positions = quat.fk(rotations, positions, B)

        sim_position_joint_index = 11
        sim_rotation_joint_index = 0

        sim_position = np.array([1.0,1.0,0.0]) * global_positions[:, sim_position_joint_index:sim_position_joint_index + 1]
        sim_position = signal.savgol_filter(sim_position, 31, 3, axis=0, mode='interp')

        sim_direction = np.array([1.0, 1.0, 0.0]) * quat.mul_vec(global_rotations[:,sim_rotation_joint_index:sim_rotation_joint_index+1], np.array([0.0, 0.0, 1.0]))

        sim_direction = sim_direction / np.sqrt(np.sum(np.square(sim_direction), axis=-1))[...,np.newaxis]
        sim_direction = signal.savgol_filter(sim_direction, 61, 3, axis=0, mode='interp')
        sim_direction = sim_direction / np.sqrt(np.sum(np.square(sim_direction), axis=-1)[...,np.newaxis])
        
        sim_rotation = quat.normalize(quat.between(np.array([1, 0, 0]), sim_direction))

        positions[:,0:1] = quat.mul_vec(quat.inv(sim_rotation), positions[:,0:1] - sim_position)
        rotations[:,0:1] = quat.mul(quat.inv(sim_rotation), rotations[:,0:1])

        positions = np.concatenate([sim_position, positions], axis=1)
        rotations = np.concatenate([sim_rotation, rotations], axis=1)
    
        B = np.concatenate([[-1], B + 1])

        velocities = np.empty_like(positions)
        velocities[1:-1] = (
            0.5 * (positions[2:  ] - positions[1:-1]) * 60.0 +
            0.5 * (positions[1:-1] - positions[ :-2]) * 60.0)
        velocities[ 0] = velocities[ 1] - (velocities[ 3] - velocities[ 2])
        velocities[-1] = velocities[-2] + (velocities[-2] - velocities[-3])
        
        angular_velocities = np.zeros_like(positions)
        angular_velocities[1:-1] = (
            0.5 * quat.to_scaled_angle_axis(quat.abs(quat.mul_inv(rotations[2:  ], rotations[1:-1]))) * 60.0 +
            0.5 * quat.to_scaled_angle_axis(quat.abs(quat.mul_inv(rotations[1:-1], rotations[ :-2]))) * 60.0)
        angular_velocities[ 0] = angular_velocities[ 1] - (angular_velocities[ 3] - angular_velocities[ 2])
        angular_velocities[-1] = angular_velocities[-2] + (angular_velocities[-2] - angular_velocities[-3])
        
        """ Compute Contact Data """ 

        global_rotations, global_positions, global_velocities, global_angular_velocities = quat.fk_vel(
            rotations, 
            positions, 
            velocities,
            angular_velocities,
            B)
        
        contact_velocity_threshold = 0.15
        
        contact_velocity = np.sqrt(np.sum(global_velocities[:,np.array([
            5, 
            9])]**2, axis=-1))
        
        # Contacts are given for when contact bones are below velocity threshold
        contacts = contact_velocity < contact_velocity_threshold
        
        # Median filter here acts as a kind of "majority vote", and removes
        # small regions  where contact is either active or inactive
        for ci in range(contacts.shape[1]):
        
            contacts[:,ci] = ndimage.median_filter(
                contacts[:,ci], 
                size=6, 
                mode='nearest')
        
        """ Append to Database """
        
        bone_positions.append(positions)
        bone_velocities.append(velocities)
        bone_rotations.append(rotations)
        bone_angular_velocities.append(angular_velocities)
        
        offset = 0 if len(range_starts) == 0 else range_stops[-1] 

        range_starts.append(offset)
        range_stops.append(offset + len(positions))
        
        contact_states.append(contacts)
    
    
""" Concatenate Data """
    
bone_positions = np.concatenate(bone_positions, axis=0).astype(np.float32)
bone_velocities = np.concatenate(bone_velocities, axis=0).astype(np.float32)
bone_rotations = np.concatenate(bone_rotations, axis=0).astype(np.float32)
bone_angular_velocities = np.concatenate(bone_angular_velocities, axis=0).astype(np.float32)
bone_parents = B.astype(np.int32)

range_starts = np.array(range_starts).astype(np.int32)
range_stops = np.array(range_stops).astype(np.int32)

contact_states = np.concatenate(contact_states, axis=0).astype(np.uint8)

db = db(bone_positions, bone_rotations, bone_velocities, bone_angular_velocities, bone_parents, bone_positions.shape[0], range_starts.shape[0], range_starts, range_stops)

features, feature_offsets, feature_scales = build_feature_vector(db, [4, 8], [4, 8, 1], [0.75, 1, 1, 1.5])

features = features.astype(np.float32)
feature_offsets = np.concatenate(feature_offsets, axis=0).astype(np.float32).flatten()
feature_scales = np.concatenate(feature_scales, axis=0).astype(np.float32).flatten()

""" Write Database """

print("Writing Database...")

with open('./Database/database.bin', 'wb') as f:
    
    nframes = bone_positions.shape[0]
    nbones = bone_positions.shape[1]
    nranges = range_starts.shape[0]
    ncontacts = contact_states.shape[1]
    
    f.write(struct.pack('II', nframes, nbones) + bone_positions.ravel().tobytes())
    f.write(struct.pack('II', nframes, nbones) + bone_velocities.ravel().tobytes())
    f.write(struct.pack('II', nframes, nbones) + bone_rotations.ravel().tobytes())
    f.write(struct.pack('II', nframes, nbones) + bone_angular_velocities.ravel().tobytes())
    f.write(struct.pack('I', nbones) + bone_parents.ravel().tobytes())
    
    f.write(struct.pack('I', nranges) + range_starts.ravel().tobytes())
    f.write(struct.pack('I', nranges) + range_stops.ravel().tobytes())
    
    f.write(struct.pack('II', nframes, ncontacts) + contact_states.ravel().tobytes())

print("Writing Features...")

with open('./Database/features.bin', 'wb') as f:    
    nframes = features.shape[0]
    nfeatures = features.shape[1]

    f.write(struct.pack('II', nframes, nfeatures) + features.ravel().tobytes())
    f.write(struct.pack('I', nfeatures) + feature_offsets.ravel().tobytes())
    f.write(struct.pack('I', nfeatures) + feature_scales.ravel().tobytes())