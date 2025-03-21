import numpy as np
import matplotlib.pyplot as plt

FSP = np.array([-1,  1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,
        1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1])
FSP=FSP*(1+1j)
FSP_early=np.roll(FSP,-1)
FSP_late=np.roll(FSP,1)
test_freq=True
symbol_rate=1.64e6 
fs=symbol_rate
frame_time=.432
MFP_symbols=64
FSP_symbols=32
Data_symbols=3424
Data_symbols_last=3264 #note, last FSP has shorter Data_symbols + PAD
PAD_symbols=96
FSP_per_frame=205
samples_per_frame=MFP_symbols+FSP_per_frame*(FSP_symbols+Data_symbols)+PAD_symbols-(Data_symbols-Data_symbols_last)
filename = "XM_test_x1.dat"
data_type = np.complex64  # Replace with the correct data type
print("samples between MFP = ", int(frame_time*fs))
print("samples per MFP = ", (MFP_symbols*fs/symbol_rate))
print("samples per FSP = ", (FSP_symbols*fs/symbol_rate))
print("samples between FSP = ", Data_symbols*fs/symbol_rate)
print("samples per frame = ",samples_per_frame*fs/symbol_rate )
samples_between_frames=samples_per_frame*fs/symbol_rate
samples_between_FSP=int((Data_symbols+FSP_symbols)*fs/symbol_rate)
print("samples per second = ",samples_per_frame*fs/(symbol_rate*frame_time) )
flip=1
freq=14883
samples=samples_between_FSP
file_offset=0
t=0
phase=0
with open(filename, "rb") as file:
    data_array = np.fromfile(file, dtype=data_type)

freq=14883
t=np.arange(np.power(2,16))/fs
temp_data=data_array[0:np.power(2,16)]*np.exp(-1j*2*np.pi*freq*t)
fft=np.fft.fft(data_array[0:np.power(2,16)])
plt.plot(np.abs(np.fft.fftshift(fft)))
plt.show()
plt.plot(np.angle(temp_data),'b.')
plt.show()
