import numpy as np
import matplotlib.pyplot as plt

test_freq=False
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
filename = "XM_test"
filename = "XM_test_x1.dat"
data_type = np.complex64  # Replace with the correct data type
print("samples between MFP = ", int(frame_time*fs))
print("samples per MFP = ", (MFP_symbols*fs/symbol_rate))
print("samples per FSP = ", (FSP_symbols*fs/symbol_rate))
print("samples between FSP = ", Data_symbols*fs/symbol_rate)
print("samples per frame = ",samples_per_frame*fs/symbol_rate )
samples_between_frames=samples_per_frame*fs/symbol_rate
samples_between_FSP=int(Data_symbols*fs/symbol_rate)
print("samples per second = ",samples_per_frame*fs/(symbol_rate*frame_time) )

with open(filename, "rb") as file:
    data_array = np.fromfile(file, dtype=data_type)
print(len(data_array)/fs)
corr_length=int(FSP_symbols*fs/symbol_rate)#+int(MFP_symbols*fs/symbol_rate)
span=int(samples_between_FSP)
if test_freq:
    t=np.arange(2*span)/fs
    for freq in range(10800,15200,100):
        print ("frequency=", freq)
        temp_data=data_array[0:2*span]*np.exp(-1j*2*np.pi*freq*t)
        plt.clf()
        plt.plot(np.angle(temp_data),'b.')
        plt.pause(.5)

#704 start of FSP
freq=14883
if (0):
    t=np.arange(10*span)/fs
    temp_data=data_array[0:10*span]*np.exp(-1j*2*np.pi*freq*t)
    plt.plot(np.angle(temp_data),'b.')
    plt.show()
    test_out1=temp_data[span:2*span]
    test_out2=temp_data[2*span:3*span]
    test_out3=temp_data[2*span:3*span]
    test_out4=temp_data[2*span:3*span]
    test_out5=temp_data[2*span:3*span]
    max_value=0
    max_loop=0
    for loop in range(span):
        base_out=temp_data[0+loop:FSP_symbols+loop]
        corr_out1=np.correlate(test_out1,base_out)
        corr_out2=np.correlate(test_out2,base_out)
        corr_out3=np.correlate(test_out3,base_out)
        corr_out4=np.correlate(test_out4,base_out)
        corr_out5=np.correlate(test_out5,base_out)
        plt.clf()
        corr_out=corr_out1+corr_out2+corr_out3+corr_out4+corr_out5
        if max(abs(corr_out))>max_value:
            max_value=max(abs(corr_out))
            max_loop=loop
        print (loop, max(abs(corr_out)), max_loop, max_value)
        plt.plot(corr_out)
        plt.pause(0.5)
t=np.arange(span)/fs
if (1):
    fsp_start=704
    span=span+FSP_symbols
    t=np.arange(span)/fs
    fsp_data=data_array[fsp_start:fsp_start+FSP_symbols]*np.exp(-1j*2*np.pi*freq*t[0:FSP_symbols])
    t=t+span/fs
    fsp_start=fsp_start+span
    desired_index=16
    phase=0
    last=100
    block=0
    mrc=np.zeros((1,100))
    while(1):
        temp_data=data_array[fsp_start:fsp_start+span]*np.exp(-1j*2*np.pi*(freq*t+phase))
        corr_out=np.correlate(temp_data,fsp_data, 'same')
        plt.plot(np.real(corr_out),'b.-')
        plt.plot(np.imag(corr_out),'r.-')
        plt.axis([0,100, -2, 2])
        max_index=np.argmax(np.abs(corr_out))
        phase_diff=np.angle(corr_out[max_index])
        print (max_index,max(np.abs(corr_out)), 180*phase_diff/np.pi)
        phase=phase+phase_diff/10
        if max_index<desired_index:
            fsp_start-=1
        elif max_index>desired_index:
            fsp_start+=1
        plt.pause(.1)
        plt.clf()
        mrc=mrc+temp_data[0:100]
        t=t+span/fs
        fsp_start=fsp_start+span
        block+=1
        if block>last:
            break
plt.clf()
print (mrc)
const=mrc*np.exp(+1j*np.pi/7)
real_data=np.real(const)
print (real_data[0])
plt.plot(np.real(const),np.imag(const),'b.-')
plt.show()
plt.figure()
plt.plot(real_data[0],'b.-')
plt.show()
