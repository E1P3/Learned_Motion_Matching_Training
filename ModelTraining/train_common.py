import struct
import numpy as np
import torch
import torch.nn as nn

class ONNXModel(nn.Module):
    def __init__(self, model, mean_in, std_in, mean_out, std_out):
        super(ONNXModel, self).__init__()
        self.model = model
        
        # Ensure the parameters are torch tensors and detached from the current graph
        if not isinstance(mean_in, torch.Tensor):
            mean_in = torch.tensor(mean_in).float()
        if not isinstance(std_in, torch.Tensor):
            std_in = torch.tensor(std_in).float()
        if not isinstance(mean_out, torch.Tensor):
            mean_out = torch.tensor(mean_out).float()
        if not isinstance(std_out, torch.Tensor):
            std_out = torch.tensor(std_out).float()
        
        # Register buffers, properly detached and not requiring gradients
        self.register_buffer('mean_in', mean_in.clone().detach())
        self.register_buffer('std_in', std_in.clone().detach())
        self.register_buffer('mean_out', mean_out.clone().detach())
        self.register_buffer('std_out', std_out.clone().detach())

    def forward(self, x):
        # Normalize input
        x = (x - self.mean_in) / self.std_in
        
        # Process data through the model
        x = self.model(x)
        
        # Denormalize output
        x = x * self.std_out + self.mean_out
        return x



def load_database(filename):

    with open(filename, 'rb') as f:
        
        nframes, nbones = struct.unpack('II', f.read(8))
        bone_positions = np.frombuffer(f.read(nframes*nbones*3*4), dtype=np.float32, count=nframes*nbones*3).reshape([nframes, nbones, 3])
        
        nframes, nbones = struct.unpack('II', f.read(8))
        bone_velocities = np.frombuffer(f.read(nframes*nbones*3*4), dtype=np.float32, count=nframes*nbones*3).reshape([nframes, nbones, 3])
        
        nframes, nbones = struct.unpack('II', f.read(8))
        bone_rotations = np.frombuffer(f.read(nframes*nbones*4*4), dtype=np.float32, count=nframes*nbones*4).reshape([nframes, nbones, 4])
        
        nframes, nbones = struct.unpack('II', f.read(8))
        bone_angular_velocities = np.frombuffer(f.read(nframes*nbones*3*4), dtype=np.float32, count=nframes*nbones*3).reshape([nframes, nbones, 3])
        
        nbones = struct.unpack('I', f.read(4))[0]
        bone_parents = np.frombuffer(f.read(nbones*4), dtype=np.int32, count=nbones).reshape([nbones])
        
        nranges = struct.unpack('I', f.read(4))[0]
        range_starts = np.frombuffer(f.read(nranges*4), dtype=np.int32, count=nranges).reshape([nranges])
        
        nranges = struct.unpack('I', f.read(4))[0]
        range_stops = np.frombuffer(f.read(nranges*4), dtype=np.int32, count=nranges).reshape([nranges])
        
        nframes, ncontacts = struct.unpack('II', f.read(8))
        contact_states = np.frombuffer(f.read(nframes*ncontacts), dtype=np.int8, count=nframes*ncontacts).reshape([nframes, ncontacts])
        
    return {
        'bone_positions': bone_positions,
        'bone_rotations': bone_rotations,
        'bone_velocities': bone_velocities,
        'bone_angular_velocities': bone_angular_velocities,
        'bone_parents': bone_parents,
        'range_starts': range_starts,
        'range_stops': range_stops,
        'contact_states': contact_states,
    }
        

def load_features(filename):

    with open(filename, 'rb') as f:
        
        nframes, nfeatures = struct.unpack('II', f.read(8))
        features = np.frombuffer(f.read(nframes*nfeatures*4), dtype=np.float32, count=nframes*nfeatures).reshape([nframes, nfeatures])
        
        nfeatures = struct.unpack('I', f.read(4))[0]
        features_offset = np.frombuffer(f.read(nfeatures*4), dtype=np.float32, count=nfeatures).reshape([nfeatures])
        
        nfeatures = struct.unpack('I', f.read(4))[0]
        features_scale = np.frombuffer(f.read(nfeatures*4), dtype=np.float32, count=nfeatures).reshape([nfeatures])
        
    return {
        'features': features,
        'features_offset': features_offset,
        'features_scale': features_scale,
    }
    
    
def load_latent(filename):

    with open(filename, 'rb') as f:
        
        nframes, nfeatures = struct.unpack('II', f.read(8))
        latent = np.frombuffer(f.read(nframes*nfeatures*4), dtype=np.float32, count=nframes*nfeatures).reshape([nframes, nfeatures])
        
    return {
        'latent': latent,
    }
    
    
def save_network(filename, layers, mean_in, std_in, mean_out, std_out):
    
    with torch.no_grad():
        
        with open(filename, 'wb') as f:
            f.write(struct.pack('I', mean_in.shape[0]) + mean_in.cpu().numpy().astype(np.float32).ravel().tobytes())
            f.write(struct.pack('I', std_in.shape[0]) + std_in.cpu().numpy().astype(np.float32).ravel().tobytes())
            f.write(struct.pack('I', mean_out.shape[0]) + mean_out.cpu().numpy().astype(np.float32).ravel().tobytes())
            f.write(struct.pack('I', std_out.shape[0]) + std_out.cpu().numpy().astype(np.float32).ravel().tobytes())
            f.write(struct.pack('I', len(layers)))
            for layer in layers:
                f.write(struct.pack('II', *layer.weight.T.shape) + layer.weight.T.cpu().numpy().astype(np.float32).ravel().tobytes())
                f.write(struct.pack('I', *layer.bias.shape) + layer.bias.cpu().numpy().astype(np.float32).ravel().tobytes())


def save_std_mean(filename, mean_in, std_in, mean_out, std_out):
    with open(filename, 'wb') as f:
        f.write(struct.pack('I', mean_in.shape[0]) + mean_in.cpu().numpy().astype(np.float32).ravel().tobytes())
        f.write(struct.pack('I', std_in.shape[0]) + std_in.cpu().numpy().astype(np.float32).ravel().tobytes())
        f.write(struct.pack('I', mean_out.shape[0]) + mean_out.cpu().numpy().astype(np.float32).ravel().tobytes())
        f.write(struct.pack('I', std_out.shape[0]) + std_out.cpu().numpy().astype(np.float32).ravel().tobytes())

def save_onnx_network(filename, model, mean_in, std_in, mean_out, std_out, sample_input):
    model = ONNXModel(model, mean_in, std_in, mean_out, std_out)
    torch.onnx.export(model, sample_input, filename, verbose=False)
    