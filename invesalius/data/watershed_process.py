import numpy as np
from scipy import ndimage
from scipy.ndimage import watershed_ift, generate_binary_structure
from skimage.morphology import watershed
from skimage import filter


def get_LUT_value(data, window, level):
    return np.piecewise(data, 
                        [data <= (level - 0.5 - (window-1)/2),
                         data > (level - 0.5 + (window-1)/2)],
                        [0, 255, lambda data: ((data - (level - 0.5))/(window-1) + 0.5)*(255-0)])



def do_watershed(image, markers,  tfile, shape, bstruct, algorithm, mg_size, use_ww_wl, wl, ww, q):
    mask = np.memmap(tfile, shape=shape, dtype='uint8', mode='r+')
                
    if use_ww_wl:
        if algorithm == 'Watershed':
            tmp_image = ndimage.morphological_gradient(
                           get_LUT_value(image, ww, wl).astype('uint16'),
                           mg_size)
            tmp_mask = watershed(tmp_image, markers.astype('int16'), bstruct)
        else:
            tmp_image = get_LUT_value(image, ww, wl).astype('uint16')
            #tmp_image = ndimage.gaussian_filter(tmp_image, self.config.mg_size)
            #tmp_image = ndimage.morphological_gradient(
                           #get_LUT_value(image, ww, wl).astype('uint16'),
                           #self.config.mg_size)
            tmp_mask = watershed_ift(tmp_image, markers.astype('int16'), bstruct)
    else:
        if algorithm == 'Watershed':
            tmp_image = ndimage.morphological_gradient((image - image.min()).astype('uint16'), mg_size)
            tmp_mask = watershed(tmp_image, markers.astype('int16'), bstruct)
        else:
            tmp_image = (image - image.min()).astype('uint16')
            #tmp_image = ndimage.gaussian_filter(tmp_image, self.config.mg_size)
            #tmp_image = ndimage.morphological_gradient((image - image.min()).astype('uint16'), self.config.mg_size)
            tmp_mask = watershed_ift(tmp_image, markers.astype('int8'), bstruct)
    mask[:] = tmp_mask
    mask.flush()
    q.put(1)
