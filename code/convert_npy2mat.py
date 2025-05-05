import numpy as np
import scipy.io
import argparse
parser = argparse.ArgumentParser(description="convert npy array to matlab.")
parser.add_argument("-i", type=str, default=None,  help="input file name")
parser.add_argument("-o", type=str, default=None, help="output file name")
args = parser.parse_args()
if args.i==None:
    print("Need and input file")
    exit()
input_split=args.i.split('.')
args.i=input_split[0]+'.npy'
if args.o==None:
    args.o=input_split[0]+'.mat'
print("reading input file ", args.i)
print("writing output file ", args.o)

npy_data=args.i
data_file = open(npy_data, 'rb')
data_full=[]
while(1):
    try:
        data_array = np.load(data_file)
        data_full.append(data_array)
    except:
        print (np.shape(data_full))
        mdic = {"samples": data_full, "label": "NUMPY data"}
        scipy.io.savemat(args.o, mdic)
        print("done")
        exit()
