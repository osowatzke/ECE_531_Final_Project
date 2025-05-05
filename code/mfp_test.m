clc
clear all
close all
load('mfp_data.mat') %samples in mfp bit frames
trellis = poly2trellis(7, [135 147]);
[frames, frame_length]=size(samples);
conEnc = comm.ConvolutionalEncoder(trellis);
modBPSK = comm.BPSKModulator;
chan = comm.AWGNChannel('NoiseMethod','Signal to noise ratio (SNR)','SNR',10);
demodBPSK = comm.BPSKDemodulator('PhaseOffset',0,'DecisionMethod','Log-likelihood ratio');
vDec = comm.ViterbiDecoder(trellis);
vDec.TerminationMethod="Terminated"
flip=1;
decoded_data=[];
for counter = 1:frames
    temp_data=zeros(1,255*8*2*2);
    for loop = 1:1360
        temp_data((loop-1)*6+5)=flip*samples(counter,(loop-1)*4+1);
        temp_data((loop-1)*6+2)=flip*samples(counter,(loop-1)*4+2);
        temp_data((loop-1)*6+4)=flip*samples(counter,(loop-1)*4+3);
        temp_data((loop-1)*6+6)=flip*samples(counter,(loop-1)*4+4); 
    end
    receivedBits = vDec(temp_data(1:4080)');
    decoded_data=[decoded_data;receivedBits'];
    receivedBits = vDec(temp_data(4080+1:2*4080)');
    decoded_data=[decoded_data;receivedBits'];
end