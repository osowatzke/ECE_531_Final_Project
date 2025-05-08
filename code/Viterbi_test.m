clc
clear all
close all

rate=1/2;
if rate==1/3
    trellis = poly2trellis(7, [163 135 147]);
else
    trellis = poly2trellis(7, [163 135]);
end
conEnc = comm.ConvolutionalEncoder(trellis);
modBPSK = comm.BPSKModulator;
chan = comm.AWGNChannel('NoiseMethod','Signal to noise ratio (SNR)','SNR',0);
demodBPSK = comm.BPSKDemodulator('PhaseOffset',0,'DecisionMethod','Log-likelihood ratio');
vDec = comm.ViterbiDecoder(trellis);
%vDec.TerminationMethod="Terminated"
error = comm.ErrorRate('ComputationDelay',3,'ReceiveDelay',34);

for counter = 1:20
    data = randi([0 1],3000,1);
    encodedData = conEnc(data);
    modSignal = modBPSK(encodedData);
    receivedSignal = chan(modSignal);
    demodSignal = demodBPSK(receivedSignal);
    %puncture effect
    if rate==1/3
        demodSignal(3:9:end)=0;
        demodSignal(5:9:end)=0;
        demodSignal(6:9:end)=0;
        demodSignal(8:9:end)=0;
        demodSignal(9:9:end)=0;
    else
        demodSignal(4:6:end)=0;
        demodSignal(6:6:end)=0;
    end
    receivedBits = vDec(demodSignal);
    errors = error(data,receivedBits);
end
errors(1)
errors(2)
