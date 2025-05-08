This project contains OOT modules. They can be built by navigating to
the root of the repo and running:

    ./build.sh

This build script has been tested on the 2025 ECE 531 VM and may not work
on other operating systems. The build script creates a custom GNU radio
module for each block.yml file in the code subdirectory of the repo. It is
based on the instructions located here:
    
    https://wiki.gnuradio.org/index.php?title=Creating_Python_OOT_with_gr-modtool
    
In hindset, a submodule with the custom modules would be better suited for
maintaining the OOT module. If the build script fails to run you can create the
OOT module from the code subdirectory following the instructions in the URL with
"xm_module" as the OOT module name.

Once the OOT modules are installed, navigate to the code directory, and run
the following flowchart to collect XM Radio data. 

    xm_radio_collect.grc

Note that you will need to have an active antenna installed to collect any
meaningful data. For convenience, we have included our collect with the submission.
It can also be downloaded from the following folder of data.

https://drive.google.com/drive/folders/1gwz4DzkwB8t1OXDoFmxDWub_xLWsoNEI?usp=drive_link

To bypass the collect, you will want copy "XM_test_x2.dat" from the drive link and/or
submission folder into the code subdirectory.

To perform time and frequency synchronization on the collected data, you will want
to run the following flowchart

    XM_FREQ_DETECT.grc

The results of this analysis should also be included in the drive and/or submission
folder and should be titled "XM_test_x2_sync.dat". Once you have the synchronized data,
you should be able to run the following python script to determine the FSP:

    XM_find_FSP.py

Next, to determine the MFP. You should be able to execute the following python script:

    XM_find_MFP.py
    
Then, you can create perform frame synchronization on the collected data by running:

    XM_extract_frames.py
    
This script should generate a .npy file titled "mfp_data.npy". This file can also be
copied from the drive and/or submission folder. Alternatively, this step and the
frame synchronization can be run entirely in GNU radio by running:

    XM_FREQ_DETECT_with_preamble.grc

To perform time deinterleaving on the output run the following python script:

    XM_parse_frame.py
    
This script should generate a .npy file and a .mat file with the outputs titled
"mfp_deinterleave2.npy" and "mfp_deinterleave2.mat"

Finally, these files can be run through the Viterbi decoder in MATLAB by
running:

    Viterbi_mfp.m

The Reed Solomon Decoder input can be generated in MATLAB using

    genRSTestData.m

To test the GNU Radio Reed Solomon Decoder in an XM Radio configuration, we can run
the following flowchart:

    rs_test.grc
