import numpy as np
import matplotlib.pyplot as plt
import sys
import signal
import os
import XM_constants as XM
def signal_handler(sig, frame):
    global mfp_file
    print('You pressed Ctrl+C!')
    mfp_file.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
XM=XM.XM_sat()
interleaver1=XM.XM_interleaver(54400, 2)
interleaver2=XM.XM_interleaver(680, 16)
interleaver3=XM.XM_interleaver(1360, 8)
interleaver4=XM.XM_interleaver(2720, 1)
mfp_file = open('../data/mfp_data.npy', 'rb')
mfp_bit_length=2*((XM.FSP_per_frame-1)*XM.data_symbols + XM.data_symbols_last)

sat=1
if sat==1:
    filename = '../data/mfp_deinterleave2.npy'
else:
    filename = '../data/mfp_deinterleave.npy'

try:
    os.remove(filename)
except:
    pass

mfp_out_file = open(filename, 'wb')

data_array = np.load(mfp_file)
TSCC_in=np.zeros(5440*2, dtype=float)
TSCC_out=np.zeros(5440*2, dtype=float)
mfp_index=0
while(len(data_array)>0):
    #take first 4 bits, may be second 4 depending on Satellite
    TSCC_in[0+sat*4:2*5440:8]=data_array[0:5440:4]
    TSCC_in[1+sat*4:2*5440:8]=data_array[1:5440:4]
    TSCC_in[2+sat*4:2*5440:8]=data_array[2:5440:4]
    TSCC_in[3+sat*4:2*5440:8]=data_array[3:5440:4]
    for tscc_idx in range(2*5440):
        out1=interleaver1.advance(TSCC_in[tscc_idx])
        out2=interleaver2.advance(out1)
        out3=interleaver3.advance(out2)
        out=interleaver4.advance(out3)
        TSCC_out[tscc_idx]=out
    #load next frame
    np.save(mfp_out_file,TSCC_out)
    try: data_array = np.load(mfp_file)
    except: break
    print("MFP FRAME = ", mfp_index)
    mfp_index+=1

# Close numpy file
mfp_out_file.close()

# Save data to .mat file
if True:

    # Read all data from a .mat file
    samples = []
    with open(filename, 'rb') as mfp_out_file:
        while True:
            try:
                samples.append(np.load(mfp_out_file))
            except:
                break

    samples = np.array(samples)

    # Save to .mat file
    import scipy.io as sio
    if sat==1:
        sio.savemat('../data/mfp_deinterleave2.mat',{'data': samples})
    else:
        sio.savemat('../data/mfp_deinterleave.mat',{'data': samples})
 
