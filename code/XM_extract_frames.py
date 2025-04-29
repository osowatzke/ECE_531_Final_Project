import numpy as np
import matplotlib.pyplot as plt
import sys
import signal
sys.path.append("/media/sf_VM_shared/ECE531/Final/python_tools")
import XM_constants as XM
import os
os.remove('mfp_data.npy')
mfp_file = open('mfp_data.npy', 'ab')
def signal_handler(sig, frame):
    global mfp_file
    print('You pressed Ctrl+C!')
    mfp_file.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
filename = "XM_test_x2_sync.dat"
data_type = np.complex64  # Replace with the correct data type
XM=XM.XM_sat()
#jump into file as AGC may not be stable
idx=int(.0*XM.fs)
samples = XM.samples_between_FSP
FSP_SYNC=False
MFP_SYNC=False
MFP_symbols=np.zeros((XM.FSP_per_frame*XM.Data_symbols), dtype=data_type)
MFP_bits=np.zeros(2*((XM.FSP_per_frame-1)*XM.Data_symbols+XM.Data_symbols_last), dtype=float)
with open(filename, "rb") as file:
    while(1):
        data_array = np.fromfile(file, dtype=data_type,  count=1*samples)
        if not FSP_SYNC:
            corr_out=np.correlate(data_array,XM.FSP)
            max_index=np.argmax(np.abs(corr_out))
            ave=np.sum(np.abs(corr_out))/len(corr_out)
            if ((np.abs(corr_out[max_index])/ ave)>4):
                FSP_SYNC=True
                #plt.plot(np.abs(corr_out))
                print(int(idx/8)+max_index,max_index, np.abs(corr_out[max_index])/ ave)
                #plt.show()
                idx=idx+max_index*8
                file.seek(idx)
                print("FOUND  FSP", idx)
            else:
                idx+=samples*8
        elif not MFP_SYNC:
            #data_array = np.fromfile(file, dtype=data_type,  count=1*samples)
            corr_out=np.correlate(data_array,XM.MFP)
            max_index=np.argmax(np.abs(corr_out))
            ave=np.sum(np.abs(corr_out))/len(corr_out)
            idx+=samples*8
            #print(1*(data_array[:XM.FSP_symbols]>0))
            #print(1*(XM.FSP>0))
            if ((np.abs(corr_out[max_index])/ ave)>4 and max_index>=samples-XM.MFP_symbols):
                #print(1*(data_array[samples-XM.MFP_symbols:]>0))
                #print(1*(XM.MFP>0))
                #plt.plot(np.abs(corr_out))
                #plt.show()
                print("FOUND MFP", idx)
                MFP_SYNC=True
                FSP_index=0
                MFP_frame_index=0
                MFP_SYMBOLS=[]
        else:
            idx+=samples*8
            #print(FSP_index, (data_array[0:XM.FSP_symbols]>0)*1)
            #print (XM.FSP_per_frame-1, (XM.FSP>0)*1)
            if (FSP_index==(XM.FSP_per_frame)):
                print(MFP_frame_index, "MFP FRAME COMPLETE", idx)
                MFP_frame_index+=1
                FSP_index=0
                print (len(MFP_SYMBOLS))
                MFP_bits[0:len(MFP_bits):2]=np.real(MFP_SYMBOLS[:-XM.MFP_symbols-XM.PAD_symbols])
                MFP_bits[1:len(MFP_bits):2]=np.imag(MFP_SYMBOLS[:-XM.MFP_symbols-XM.PAD_symbols])
                np.save(mfp_file,MFP_bits)
            else:
                MFP_SYMBOLS[FSP_index*XM.Data_symbols:(FSP_index+1)*XM.Data_symbols]= (data_array[XM.FSP_symbols:])
                FSP_index+=1
        if (len(data_array)==0): break;
                
                
           
            

