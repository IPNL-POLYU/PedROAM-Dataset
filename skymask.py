"""Decode frames from PedROAM's per-session skymask.npz files."""
from operator import index

import numpy as np


def read_skymask_frame(path, frame_index):
    """Read one zero-based assessment-track frame without loading all masks.

    Returns sky (a masked uint8 array), valid, row_index and utc_seconds.
    In valid pixels, 1 denotes modeled sky and 0 denotes obstruction.
    Pixels outside valid_disk and all pixels in invalid frames are masked.
    frame_index is an array index, not a phone epoch or source row index.
    """
    frame_index = index(frame_index)
    with np.load(path, allow_pickle=False) as data:
        if not 0 <= frame_index < len(data['row_indices']):
            raise IndexError('Sky-mask frame index out of range')
        batch_size = int(data['batch_size'])
        start = frame_index // batch_size * batch_size
        disk = data['valid_disk']
        packed = data[f'sky_packed_{start:06d}'][frame_index - start]
        sky = np.unpackbits(packed, axis=-1, count=disk.shape[1], bitorder='big')
        valid = bool(data['valid'][frame_index])
        return {
            'sky': np.ma.array(sky, mask=~disk | (not valid)),
            'valid': valid,
            'row_index': int(data['row_indices'][frame_index]),
            'utc_seconds': float(data['utc_seconds'][frame_index]),
        }
