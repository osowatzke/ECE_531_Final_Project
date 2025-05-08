load('mfp_deinterleave.mat');
fid = fopen('XM_test_x2_sync.dat','r');
data = fread(fid,'single');
fclose(fid);
bits = pskdemod(data,4,pi/4);

data = complex(data(1:2:end),data(2:2:end));
for i = 1:10000:(length(data)-9999)
    scatter(real(data(i:i+9999)),imag(data(i:i+9999)));
    pause(0.01)
end

rate=1/2;
if rate==1/3
    trellis = poly2trellis(7, [163 135 147]);
else
    trellis = poly2trellis(7, [163 135]);
end
vDec = comm.ViterbiDecoder(trellis);
receivedBits = vDec(data(:));
