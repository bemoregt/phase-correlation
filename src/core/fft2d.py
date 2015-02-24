'''
Created on Dec 11, 2012

@author: bxs003
'''

from PIL import Image
import numpy as np
import math

# Phase Correlation
# Hamming or Lanczos Windowing on input signals
# Take 2D FFTs of the input signals
# Perform cross power correlation
# Take IFFT of the correlated signal
# Find location of peak intensity on output signal

# Automatic Calibration Step
# Place a uniformly spaced black and white checkerboard
# pattern under the camera
# The spatial period of the checkerboard, d, is known
# The DFT of the pattern should return some peak discrete freq., f0
# d and f0 can be used to map real world coord.s to discrete (for initial frame)

def phase_corrleation(img1, img2):
    img1 = img1.convert('L')
    img2 = img2.convert('L')
    
    pix1 = np.asarray(img1)
    pix2 = np.asarray(img2)
    
    fft1 = np.fft.fft2(pix1)
    fft2 = np.fft.fft2(pix2)
    R = cross_power_spectrum(fft1, fft2)
    cor = np.fft.ifft2(R)
    row, col = np.unravel_index(cor.argmax(), cor.shape)
    return col, row

def gen_test_img(size, freq):
    x = np.linspace(0.0, freq*2.0*math.pi, size)
    sinv = np.vectorize(math.sin)
    y = sinv(x)
    y = y**2
    y = 255*y
    y = np.uint8(y)
    
    a = np.array([y, y])
    
    img = Image.fromarray(a, 'L')
    img.save('../../imgs/test2.png', 'PNG')
    return img

def cross_power_spectrum(A, B):
    R = A*B.conjugate()
    R = R/R.max()
    return R

def main():
    img1 = Image.open('../../imgs/img1.png')
    img1 = img1.convert('L')
    
    img2 = Image.open('../../imgs/img2.png')
    img2 = img2.convert('L')
    
    pix1 = np.asarray(img1)
    pix2 = np.asarray(img2)
    
    fft1 = np.fft.fft2(pix1)
    fft2 = np.fft.fft2(pix2)
    R = cross_power_spectrum(fft1, fft2)
    cor = np.fft.ifft2(R)
    print np.unravel_index(cor.argmax(), cor.shape)
    
    cor_mag = (cor*cor.conjugate()).real
    cor_mag = cor_mag*(255.0/cor_mag.max())
    phase = Image.fromarray(np.uint8(cor_mag))
    phase.save("../../imgs/phase_corr.png", 'PNG')
    
#    img = gen_test_img(1000, 10.0)
    
#    pixels = np.asarray(img)
#    ft_pix = np.fft.fft2(pixels)
#    
#    ft_abs = (ft_pix*ft_pix.conjugate()).real
#    ft_abs = ft_abs**0.5
#    
#    ft_abs = ft_abs*(255.0/ft_abs.max())
#    ft_abs = np.uint8(ft_abs)
#    print ft_abs
#    ft_img = Image.fromarray(ft_abs)
#    ft_img.save("C:/Users/bxs003/Pictures/ft.png", 'PNG')
    
def test():
    a = 1 + 1j
    b = 3 + 7j
    print math.sqrt((a*a.conjugate()).real)
    
    A = np.array([[1,2], [3,4]])
    B = np.array([[1, 1],[2, 2]])
    print A**B
    
    
if __name__ == '__main__':
    main()
    #test()
        
    