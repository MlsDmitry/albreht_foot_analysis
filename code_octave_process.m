hidden                           histeq                           history_save
hilb                             history                          history_size
hist                             history_control                  history_timestamp_format_string
histc                            history_file
>> hist
hist                             history                          history_save
histc                            history_control                  history_size
histeq                           history_file                     history_timestamp_format_string
>> help hist
'hist' is a function from the file /usr/local/share/octave/10.2.0/m/plot/draw/hist.m

 -- hist (Y)
 -- hist (Y, NBINS)
 -- hist (Y, X)
 -- hist (Y, X, NORM)
 -- hist (..., PROP, VAL, ...)
 -- hist (HAX, ...)
 -- [NN, XX] = hist (...)
     Produce histogram counts or plots.

     With one vector input argument, Y, plot a histogram of the values
     with 10 bins.  The range of the histogram bins is determined by the
     range of the data (difference between maximum and minimum value in
     Y).  Extreme values are lumped into the first and last bins.  If Y
     is a matrix then plot a histogram where each bin contains one bar
     per input column of Y.

     If the optional second argument is a scalar, NBINS, it defines the
     number of bins.

     If the optional second argument is a vector, X, it defines the
     centers of the bins.  The width of the bins is determined from the
     adjacent values in the vector.  The total number of bins is 'numel
     (X)'.

     If a third argument NORM is provided, the histogram is normalized.
     In case NORM is a positive scalar, the resulting bars are
     normalized to NORM.  If NORM is a vector of positive scalars of
     length 'columns (Y)', then the resulting bar of 'Y(:,i)' is
     normalized to 'NORM(i)'.

          [nn, xx] = hist (rand (10, 3), 5, [1 2 3]);
          sum (nn, 1)
          => ans =
                1   2   3

     The histogram's appearance may be modified by specifying
     property/value pairs to the underlying patch object.  For example,
     the face and edge color may be modified:

          hist (randn (1, 100), 25, "facecolor", "r", "edgecolor", "b");

     The full list of patch properties is documented at Patch
     Properties.  property.  If not specified, the default colors for
     the histogram are taken from the "Colormap" property of the axes or
     figure.

     If the first argument HAX is an axes handle, then plot into this
     axes, rather than the current axes returned by 'gca'.

     If an output is requested then no plot is made.  Instead, return
     the values NN (numbers of elements) and XX (bin centers) such that
     'bar (XX, NN)' will plot the histogram.  If Y is a vector, NN and
     XX will be row vectors.  If Y is an array, NN will be a 2-D array
     with one column of element counts for each column in Y, and XX will
     be a column vector of bin centers.

     See also: histc, bar, pie, rose.

Additional help for built-in functions and operators is
available in the online version of the manual.  Use the command
'doc <topic>' to search the manual index.

Help and information about Octave is also available on the WWW
at https://www.octave.org and https://octave.discourse.group/c/help/
>> hist(imMatG)

>> imMatGHist = hist(imMatG);
>> imswarning: opengl_selector::select: selection buffer overflow

error: 'ims' undefined near line 1, column 1
>> figure;
>>
>> imshow(imMatG);
>> mean
mean    mean2   meansq
>> meansq(imMatG)
ans =

 Columns 1 through 9:

   5.8055e-04   5.8139e-04   5.8124e-04   5.9629e-04   6.0042e-04   6.0750e-04   6.0568e-04   6.0349e-04   5.8282e-04

 Columns 10 through 18:

   5.9639e-04   6.1071e-04   6.0937e-04   6.0359e-04   5.9863e-04   5.9668e-04   5.9788e-04   6.2999e-04   6.3777e-04

 Columns 19 through 27:

   6.4327e-04   6.4188e-04   6.3064e-04   6.2913e-04   6.4259e-04   6.6161e-04   6.2099e-04   6.2765e-04   6.4642e-04

 Columns 28 through 36:

   6.5573e-04   6.5097e-04   6.5952e-04   6.5928e-04   6.6960e-04   6.4985e-04   6.5593e-04   6.6348e-04   6.6148e-04

 Columns 37 through 45:

   6.4237e-04   6.3560e-04   6.3107e-04   6.4012e-04   6.3773e-04   6.3696e-04   6.4845e-04   6.5120e-04   6.6201e-04

 Columns 46 through 54:

   6.6556e-04   6.6815e-04   6.7000e-04   6.6544e-04   6.8146e-04   6.9314e-04   6.9755e-04   6.7975e-04   6.7165e-04

 Columns 55 through 63:

   6.7017e-04   6.8318e-04   6.7090e-04   6.7511e-04   6.7846e-04   6.7511e-04   6.7540e-04   6.8340e-04   6.9107e-04

 Columns 64 through 72:

   7.0060e-04   7.1917e-04   7.2587e-04   7.2424e-04   7.1837e-04   7.0446e-04   7.1255e-04   7.1451e-04   7.2476e-04

 Columns 73 through 81:

   7.0702e-04   7.2264e-04   7.3334e-04   7.2633e-04   7.1164e-04   7.0960e-04   7.2589e-04   7.3191e-04   7.3597e-04

 Columns 82 through 90:

   7.4513e-04   7.4389e-04   7.4255e-04   7.3788e-04   7.3953e-04   7.3241e-04   7.3922e-04   7.2348e-04   7.4050e-04

 Columns 91 through 99:

   7.5670e-04   7.4010e-04   7.3764e-04   7.5310e-04   7.7783e-04   7.7724e-04   7.5542e-04   7.6696e-04   7.7634e-04

 Columns 100 through 108:

   7.7772e-04   7.7093e-04   7.6633e-04   7.5947e-04   7.7335e-04   7.3493e-04   7.4833e-04   7.7371e-04   7.6938e-04

 Columns 109 through 117:

   7.5626e-04   7.6254e-04   7.8198e-04   7.9072e-04   7.7385e-04   7.6929e-04   7.6078e-04   7.5655e-04   7.4417e-04

 Columns 118 through 126:

   7.5199e-04   7.5124e-04   7.6070e-04   7.5770e-04   7.5276e-04   7.6026e-04   7.6283e-04   7.5450e-04   7.5357e-04

 Columns 127 through 135:

   7.5276e-04   7.6570e-04   7.7141e-04   7.6643e-04   7.7751e-04   7.8404e-04   7.6184e-04   7.4034e-04   7.2212e-04

 Columns 136 through 144:

   7.3628e-04   7.2409e-04   7.2760e-04   7.3675e-04   7.2673e-04   7.2209e-04   7.1955e-04   7.2811e-04   7.3758e-04

 Columns 145 through 153:

   7.5780e-04   7.5777e-04   7.4248e-04   7.2791e-04   7.1008e-04   7.1629e-04   6.9438e-04   6.9322e-04   6.6789e-04

 Columns 154 through 162:

   6.6813e-04   6.6970e-04   6.6262e-04   6.6241e-04   6.6776e-04   6.7360e-04   6.7215e-04   6.6829e-04   6.8868e-04

 Columns 163 through 171:

   6.8246e-04   6.6239e-04   6.3430e-04   6.2455e-04   6.1291e-04   6.1310e-04   5.9258e-04   5.8556e-04   5.7378e-04

 Columns 172 through 180:

   5.7011e-04   5.6633e-04   5.5922e-04   5.5425e-04   5.5765e-04   5.3927e-04   5.3588e-04   5.2497e-04   5.2498e-04

 Columns 181 through 189:

   5.0237e-04   5.0088e-04   4.7543e-04   4.7348e-04   4.4279e-04   4.4264e-04   4.2808e-04   4.2310e-04   4.0950e-04

 Columns 190 through 198:

   4.0665e-04   4.0870e-04   4.1243e-04   4.0133e-04   3.9889e-04   3.7840e-04   3.7709e-04   3.4350e-04   3.4297e-04

 Columns 199 through 207:

   3.1767e-04   3.1764e-04   2.8019e-04   2.7975e-04   2.5295e-04   2.5258e-04   2.4220e-04   2.4229e-04   2.3857e-04

 Columns 208 through 216:

   2.3860e-04   1.8721e-04   1.8721e-04   1.6739e-04   1.6739e-04   1.4220e-04   1.4220e-04   1.1024e-04   1.1024e-04

 Columns 217 through 225:

   8.6534e-05   8.6534e-05   6.9546e-05   6.9546e-05   5.9877e-05   5.9877e-05   5.8866e-05   5.8866e-05   5.1519e-05

 Columns 226 through 234:

   5.1576e-05   4.8756e-05   4.8927e-05   4.5324e-05   4.5211e-05   4.5752e-05   4.5695e-05   4.7119e-05   4.7062e-05

 Columns 235 through 243:

   5.1291e-05   5.1334e-05   5.9279e-05   5.9308e-05   6.6655e-05   6.6655e-05   7.4644e-05   7.4871e-05   7.0899e-05

 Columns 244 through 252:

   7.1881e-05   7.0286e-05   7.1055e-05   7.3675e-05   7.4031e-05   7.8972e-05   8.1350e-05   9.7754e-05   1.0314e-04

 Columns 253 through 261:

   1.1412e-04   1.2088e-04   1.4049e-04   1.5507e-04   2.0928e-04   2.6382e-04   4.4288e-04   9.5019e-04   1.9800e-03

 Columns 262 through 270:

   3.6570e-03   7.0110e-03   1.0350e-02   1.5605e-02   2.0121e-02   2.4560e-02   2.6906e-02   3.0091e-02   3.3110e-02

 Columns 271 through 279:

   4.2600e-02   6.6029e-02   1.1092e-01   1.9987e-01   3.0595e-01   3.9065e-01   4.7695e-01   5.3478e-01   5.8250e-01

 Columns 280 through 288:

   5.9387e-01   6.0482e-01   6.0732e-01   6.1471e-01   6.1718e-01   6.2211e-01   6.2902e-01   6.3616e-01   6.4111e-01

 Columns 289 through 297:

   6.5636e-01   6.5999e-01   6.6229e-01   6.6247e-01   6.5961e-01   6.5833e-01   6.5215e-01   6.4895e-01   6.4095e-01

 Columns 298 through 306:

   6.3960e-01   6.3465e-01   6.3366e-01   6.2999e-01   6.2785e-01   6.2359e-01   6.2116e-01   6.2207e-01   6.2272e-01

 Columns 307 through 315:

   6.2315e-01   6.2365e-01   6.2500e-01   6.2649e-01   6.2793e-01   6.2847e-01   6.2798e-01   6.2804e-01   6.2647e-01

 Columns 316 through 324:

   6.2544e-01   6.2336e-01   6.2336e-01   6.2301e-01   6.2394e-01   6.2160e-01   6.2393e-01   6.2612e-01   6.2889e-01

 Columns 325 through 333:

   6.3148e-01   6.3458e-01   6.3608e-01   6.3674e-01   6.3568e-01   6.3672e-01   6.3724e-01   6.3681e-01   6.3608e-01

 Columns 334 through 342:

   6.3647e-01   6.3701e-01   6.3792e-01   6.3863e-01   6.3883e-01   6.3814e-01   6.3651e-01   6.3440e-01   6.3413e-01

 Columns 343 through 351:

   6.3403e-01   6.3459e-01   6.3308e-01   6.3239e-01   6.3073e-01   6.3052e-01   6.3053e-01   6.3077e-01   6.2985e-01

 Columns 352 through 360:

   6.2952e-01   6.2539e-01   6.2472e-01   6.2354e-01   6.2318e-01   6.2057e-01   6.1893e-01   6.1530e-01   6.1434e-01

 Columns 361 through 369:

   6.1115e-01   6.1136e-01   6.1092e-01   6.1065e-01   6.0925e-01   6.0764e-01   6.0573e-01   6.0353e-01   6.0256e-01

 Columns 370 through 378:

   5.9993e-01   5.9751e-01   5.9396e-01   5.9157e-01   5.8852e-01   5.8629e-01   5.8416e-01   5.7928e-01   5.7689e-01

 Columns 379 through 387:

   5.7684e-01   5.7349e-01   5.7292e-01   5.6724e-01   5.6356e-01   5.5586e-01   5.5313e-01   5.4592e-01   5.4309e-01

 Columns 388 through 396:

   5.3804e-01   5.3967e-01   5.3676e-01   5.3774e-01   5.3563e-01   5.3539e-01   5.3280e-01   5.3399e-01   5.3061e-01

 Columns 397 through 405:

   5.3151e-01   5.2866e-01   5.3022e-01   5.2914e-01   5.3233e-01   5.3108e-01   5.3315e-01   5.3215e-01   5.3799e-01

 Columns 406 through 414:

   5.3733e-01   5.4341e-01   5.4066e-01   5.4472e-01   5.3865e-01   5.4193e-01   5.3096e-01   5.3641e-01   5.2512e-01

 Columns 415 through 423:

   5.2468e-01   5.1527e-01   5.1516e-01   5.1172e-01   5.1148e-01   5.0680e-01   5.0389e-01   4.9854e-01   4.9689e-01

 Columns 424 through 432:

   4.9236e-01   4.9045e-01   4.8701e-01   4.8636e-01   4.8068e-01   4.7935e-01   4.7413e-01   4.7243e-01   4.6704e-01

 Columns 433 through 441:

   4.6564e-01   4.6057e-01   4.5959e-01   4.5537e-01   4.5700e-01   4.5488e-01   4.5668e-01   4.5627e-01   4.5686e-01

 Columns 442 through 450:

   4.5694e-01   4.5895e-01   4.5883e-01   4.5923e-01   4.5829e-01   4.5796e-01   4.5718e-01   4.5662e-01   4.5663e-01

 Columns 451 through 459:

   4.5613e-01   4.5435e-01   4.5366e-01   4.5354e-01   4.5566e-01   4.5647e-01   4.5807e-01   4.5859e-01   4.6081e-01

 Columns 460 through 468:

   4.6059e-01   4.6163e-01   4.6034e-01   4.6044e-01   4.5877e-01   4.5916e-01   4.5765e-01   4.5778e-01   4.5750e-01

 Columns 469 through 477:

   4.6050e-01   4.6093e-01   4.6372e-01   4.6376e-01   4.6571e-01   4.6644e-01   4.6891e-01   4.6749e-01   4.6812e-01

 Columns 478 through 486:

   4.6867e-01   4.7242e-01   4.7394e-01   4.7803e-01   4.7983e-01   4.8414e-01   4.8634e-01   4.9124e-01   4.9308e-01

 Columns 487 through 495:

   4.9735e-01   4.9878e-01   5.0071e-01   5.0161e-01   5.0345e-01   5.0412e-01   5.0612e-01   5.0697e-01   5.0907e-01

 Columns 496 through 504:

   5.1061e-01   5.1352e-01   5.1506e-01   5.1648e-01   5.1774e-01   5.1910e-01   5.1999e-01   5.2140e-01   5.2193e-01

 Columns 505 through 513:

   5.2225e-01   5.2240e-01   5.2254e-01   5.2237e-01   5.2265e-01   5.2213e-01   5.2254e-01   5.2245e-01   5.2103e-01

 Columns 514 through 522:

   5.2100e-01   5.1961e-01   5.1762e-01   5.1447e-01   5.1240e-01   5.0880e-01   5.0770e-01   5.0232e-01   5.0171e-01

 Columns 523 through 531:

   4.9686e-01   4.9494e-01   4.8911e-01   4.8569e-01   4.8010e-01   4.7755e-01   4.7154e-01   4.7081e-01   4.6739e-01

 Columns 532 through 540:

   4.6571e-01   4.6082e-01   4.5771e-01   4.5074e-01   4.4753e-01   4.4173e-01   4.4084e-01   4.3679e-01   4.3559e-01

 Columns 541 through 549:

   4.3126e-01   4.3010e-01   4.2690e-01   4.2619e-01   4.2065e-01   4.2090e-01   4.1807e-01   4.1720e-01   4.1162e-01

 Columns 550 through 558:

   4.0862e-01   4.0056e-01   3.9644e-01   3.8941e-01   3.8877e-01   3.8460e-01   3.8370e-01   3.7963e-01   3.7835e-01

 Columns 559 through 567:

   3.7496e-01   3.7427e-01   3.7108e-01   3.7164e-01   3.7047e-01   3.7082e-01   3.7098e-01   3.7243e-01   3.7521e-01

 Columns 568 through 576:

   3.7665e-01   3.7791e-01   3.7917e-01   3.8032e-01   3.7900e-01   3.8072e-01   3.8033e-01   3.8308e-01   3.8329e-01

 Columns 577 through 585:

   3.8618e-01   3.8826e-01   3.9277e-01   3.9442e-01   4.0052e-01   4.0237e-01   4.0656e-01   4.0822e-01   4.1241e-01

 Columns 586 through 594:

   4.1477e-01   4.2028e-01   4.2273e-01   4.2809e-01   4.3150e-01   4.3683e-01   4.3863e-01   4.4240e-01   4.4497e-01

 Columns 595 through 603:

   4.4924e-01   4.5140e-01   4.5435e-01   4.5631e-01   4.5925e-01   4.6000e-01   4.5974e-01   4.5733e-01   4.5343e-01

 Columns 604 through 612:

   4.4683e-01   4.4336e-01   4.4212e-01   4.4441e-01   4.4702e-01   4.5111e-01   4.5805e-01   4.6301e-01   4.6848e-01

 Columns 613 through 621:

   4.7162e-01   4.7202e-01   4.7225e-01   4.7301e-01   4.7344e-01   4.7433e-01   4.7447e-01   4.7478e-01   4.7395e-01

 Columns 622 through 630:

   4.7385e-01   4.7301e-01   4.7307e-01   4.7181e-01   4.7210e-01   4.6975e-01   4.6896e-01   4.6540e-01   4.6244e-01

 Columns 631 through 639:

   4.5759e-01   4.5649e-01   4.5297e-01   4.5277e-01   4.4853e-01   4.4737e-01   4.4334e-01   4.4271e-01   4.3960e-01

 Columns 640 through 648:

   4.3947e-01   4.3439e-01   4.3645e-01   4.3613e-01   4.4103e-01   4.4183e-01   4.4544e-01   4.4295e-01   4.4502e-01

 Columns 649 through 657:

   4.4330e-01   4.4640e-01   4.4647e-01   4.4885e-01   4.4710e-01   4.4774e-01   4.4677e-01   4.4777e-01   4.4582e-01

 Columns 658 through 666:

   4.4692e-01   4.4556e-01   4.4712e-01   4.4619e-01   4.4823e-01   4.4669e-01   4.4736e-01   4.4441e-01   4.4612e-01

 Columns 667 through 675:

   4.4506e-01   4.4767e-01   4.4987e-01   4.5526e-01   4.6241e-01   4.6846e-01   4.7147e-01   4.7436e-01   4.7592e-01

 Columns 676 through 684:

   4.7894e-01   4.7940e-01   4.7764e-01   4.7435e-01   4.7378e-01   4.7437e-01   4.7677e-01   4.7927e-01   4.8078e-01

 Columns 685 through 693:

   4.8174e-01   4.8340e-01   4.8415e-01   4.8461e-01   4.8174e-01   4.8254e-01   4.8143e-01   4.8127e-01   4.7944e-01

 Columns 694 through 702:

   4.7971e-01   4.7830e-01   4.7837e-01   4.7663e-01   4.7753e-01   4.7635e-01   4.7738e-01   4.7655e-01   4.7819e-01

 Columns 703 through 711:

   4.7833e-01   4.8068e-01   4.8094e-01   4.8594e-01   4.8904e-01   4.9372e-01   4.9486e-01   4.9843e-01   4.9962e-01

 Columns 712 through 720:

   5.0233e-01   5.0267e-01   5.0688e-01   5.0778e-01   5.1065e-01   5.0850e-01   5.0952e-01   5.0980e-01   5.1291e-01

 Columns 721 through 729:

   5.1793e-01   5.2527e-01   5.2359e-01   5.2331e-01   5.2079e-01   5.2119e-01   5.1876e-01   5.1825e-01   5.1563e-01

 Columns 730 through 738:

   5.1548e-01   5.1202e-01   5.1107e-01   5.0772e-01   5.0778e-01   5.0628e-01   5.0704e-01   5.0326e-01   5.0327e-01

 Columns 739 through 747:

   5.0055e-01   5.0010e-01   4.9590e-01   4.9364e-01   4.8830e-01   4.8635e-01   4.8277e-01   4.8158e-01   4.7935e-01

 Columns 748 through 756:

   4.7860e-01   4.7635e-01   4.7560e-01   4.7449e-01   4.7533e-01   4.7409e-01   4.7474e-01   4.7469e-01   4.7510e-01

 Columns 757 through 765:

   4.7388e-01   4.7301e-01   4.7204e-01   4.7315e-01   4.7243e-01   4.7267e-01   4.7278e-01   4.7300e-01   4.7355e-01

 Columns 766 through 774:

   4.7517e-01   4.7647e-01   4.7548e-01   4.7497e-01   4.7486e-01   4.7457e-01   4.7359e-01   4.7222e-01   4.7068e-01

 Columns 775 through 783:

   4.6969e-01   4.6909e-01   4.6784e-01   4.6456e-01   4.6123e-01   4.6059e-01   4.6148e-01   4.6193e-01   4.6196e-01

 Columns 784 through 792:

   4.6295e-01   4.6449e-01   4.6555e-01   4.6598e-01   4.6925e-01   4.7088e-01   4.6546e-01   4.5833e-01   4.5540e-01

 Columns 793 through 801:

   4.5257e-01   4.5175e-01   4.5029e-01   4.4982e-01   4.4899e-01   4.4869e-01   4.4771e-01   4.4786e-01   4.4694e-01

 Columns 802 through 810:

   4.4681e-01   4.4648e-01   4.4665e-01   4.4582e-01   4.4382e-01   4.4086e-01   4.4022e-01   4.3796e-01   4.3652e-01

 Columns 811 through 819:

   4.3409e-01   4.3275e-01   4.3110e-01   4.2861e-01   4.2509e-01   4.2330e-01   4.2191e-01   4.2108e-01   4.2010e-01

 Columns 820 through 828:

   4.1877e-01   4.1672e-01   4.1438e-01   4.1175e-01   4.1082e-01   4.0918e-01   4.0850e-01   4.0742e-01   4.0701e-01

 Columns 829 through 837:

   4.0592e-01   4.0512e-01   4.0321e-01   4.0194e-01   3.9980e-01   3.9926e-01   3.9833e-01   3.9866e-01   3.9969e-01

 Columns 838 through 846:

   4.0113e-01   4.0192e-01   4.0206e-01   4.0201e-01   4.0298e-01   4.0326e-01   4.0323e-01   4.0204e-01   4.0144e-01

 Columns 847 through 855:

   4.0209e-01   4.0357e-01   4.0424e-01   4.0545e-01   4.0565e-01   4.0440e-01   4.0281e-01   4.0269e-01   4.0323e-01

 Columns 856 through 864:

   4.0440e-01   4.0445e-01   4.0551e-01   4.0607e-01   4.0570e-01   4.0449e-01   4.0393e-01   4.0388e-01   4.0479e-01

 Columns 865 through 873:

   4.0632e-01   4.0735e-01   4.0721e-01   4.0682e-01   4.0582e-01   4.0617e-01   4.0600e-01   4.0623e-01   4.0567e-01

 Columns 874 through 882:

   4.0559e-01   4.0673e-01   4.0693e-01   4.0771e-01   4.0922e-01   4.1011e-01   4.1085e-01   4.1065e-01   4.1242e-01

 Columns 883 through 891:

   4.1367e-01   4.1447e-01   4.1383e-01   4.1179e-01   4.1119e-01   4.1288e-01   4.1428e-01   4.1714e-01   4.2231e-01

 Columns 892 through 900:

   4.2640e-01   4.2962e-01   4.3249e-01   4.3434e-01   4.3520e-01   4.3406e-01   4.3495e-01   4.3582e-01   4.3575e-01

 Columns 901 through 909:

   4.3503e-01   4.3479e-01   4.3442e-01   4.3430e-01   4.3225e-01   4.3120e-01   4.3063e-01   4.2997e-01   4.3044e-01

 Columns 910 through 918:

   4.3095e-01   4.3090e-01   4.2992e-01   4.2819e-01   4.2877e-01   4.2816e-01   4.2689e-01   4.2605e-01   4.2552e-01

 Columns 919 through 927:

   4.2281e-01   4.2098e-01   4.1894e-01   4.1624e-01   4.0960e-01   4.0025e-01   3.9051e-01   3.6926e-01   3.4987e-01

 Columns 928 through 936:

   3.4446e-01   3.4463e-01   3.4483e-01   3.4272e-01   3.4430e-01   3.4047e-01   3.3892e-01   3.2875e-01   2.8187e-01

 Columns 937 through 945:

   2.1339e-01   1.4205e-01   1.1051e-01   8.8512e-02   7.4750e-02   7.0684e-02   6.9519e-02   6.9076e-02   6.5263e-02

 Columns 946 through 954:

   6.4597e-02   6.2902e-02   6.2650e-02   6.1010e-02   6.0806e-02   5.9510e-02   5.9310e-02   5.9024e-02   5.9328e-02

 Columns 955 through 963:

   5.9897e-02   6.0094e-02   6.0390e-02   6.0513e-02   6.0774e-02   6.1002e-02   6.1601e-02   6.2633e-02   6.4453e-02

 Columns 964 through 972:

   6.4996e-02   6.7918e-02   6.7464e-02   7.0566e-02   7.8181e-02   9.4213e-02   1.2295e-01   1.7753e-01   2.6148e-01

 Columns 973 through 981:

   3.1445e-01   3.3301e-01   3.3097e-01   3.3141e-01   3.3012e-01   3.2972e-01   3.2903e-01   3.2879e-01   3.3001e-01

 Columns 982 through 990:

   3.3500e-01   3.4017e-01   3.4535e-01   3.4889e-01   3.5391e-01   3.5760e-01   3.5804e-01   3.5771e-01   3.5640e-01

 Columns 991 through 999:

   3.5564e-01   3.5547e-01   3.5481e-01   3.5505e-01   3.5532e-01   3.5521e-01   3.5501e-01   3.5564e-01   3.5633e-01

 Columns 1000 through 1008:

   3.5783e-01   3.5841e-01   3.5990e-01   3.6118e-01   3.6274e-01   3.6342e-01   3.6402e-01   3.6502e-01   3.6707e-01

 Columns 1009 through 1017:

   3.7254e-01   3.8101e-01   3.8638e-01   3.8711e-01   3.8741e-01   3.8821e-01   3.8888e-01   3.8946e-01   3.9007e-01

 Columns 1018 through 1026:

   3.9091e-01   3.9240e-01   3.9414e-01   3.9634e-01   4.0008e-01   4.0328e-01   4.0401e-01   4.0278e-01   4.0233e-01

 Columns 1027 through 1035:

   4.0217e-01   4.0179e-01   4.0124e-01   4.0088e-01   4.0004e-01   3.9961e-01   3.9922e-01   3.9751e-01   3.9364e-01

 Columns 1036 through 1044:

   3.9005e-01   3.8836e-01   3.8925e-01   3.9134e-01   3.9409e-01   3.9390e-01   3.9472e-01   3.9543e-01   3.9560e-01

 Columns 1045 through 1053:

   3.9588e-01   3.9579e-01   3.9565e-01   3.9363e-01   3.9047e-01   3.8830e-01   3.8579e-01   3.8307e-01   3.8145e-01

 Columns 1054 through 1062:

   3.7987e-01   3.7742e-01   3.7478e-01   3.7110e-01   3.7033e-01   3.6959e-01   3.6767e-01   3.6514e-01   3.6316e-01

 Columns 1063 through 1071:

   3.6115e-01   3.5870e-01   3.5640e-01   3.5555e-01   3.5424e-01   3.5229e-01   3.5023e-01   3.4860e-01   3.4766e-01

 Columns 1072 through 1080:

   3.4678e-01   3.4680e-01   3.4610e-01   3.4474e-01   3.4288e-01   3.4127e-01   3.4082e-01   3.4035e-01   3.3986e-01

 Columns 1081 through 1089:

   3.3909e-01   3.3874e-01   3.3843e-01   3.3731e-01   3.3688e-01   3.3690e-01   3.3680e-01   3.3620e-01   3.3634e-01

 Columns 1090 through 1098:

   3.3626e-01   3.3638e-01   3.3602e-01   3.3549e-01   3.3497e-01   3.3436e-01   3.3376e-01   3.3224e-01   3.3165e-01

 Columns 1099 through 1107:

   3.3115e-01   3.3037e-01   3.2967e-01   3.2890e-01   3.2800e-01   3.2716e-01   3.2625e-01   3.2615e-01   3.2536e-01

 Columns 1108 through 1116:

   3.2388e-01   3.2305e-01   3.2190e-01   3.2142e-01   3.2056e-01   3.1873e-01   3.1838e-01   3.1865e-01   3.1841e-01

 Columns 1117 through 1125:

   3.1785e-01   3.1692e-01   3.1641e-01   3.1591e-01   3.1535e-01   3.1431e-01   3.1296e-01   3.1195e-01   3.1101e-01

 Columns 1126 through 1134:

   3.0980e-01   3.0914e-01   3.0863e-01   3.0782e-01   3.0780e-01   3.0781e-01   3.0639e-01   3.0430e-01   3.0181e-01

 Columns 1135 through 1143:

   2.9907e-01   2.9694e-01   2.9539e-01   2.9523e-01   2.9652e-01   2.9848e-01   2.9785e-01   2.9642e-01   2.9366e-01

 Columns 1144 through 1152:

   2.9223e-01   2.9045e-01   2.8950e-01   2.8821e-01   2.9075e-01   2.9440e-01   2.9977e-01   3.0282e-01   3.0544e-01

 Columns 1153 through 1161:

   3.0748e-01   3.0904e-01   3.1112e-01   3.1265e-01   3.1402e-01   3.1562e-01   3.1840e-01   3.1954e-01   3.2101e-01

 Columns 1162 through 1170:

   3.2328e-01   3.2812e-01   3.3305e-01   3.3781e-01   3.4316e-01   3.4975e-01   3.5472e-01   3.6183e-01   3.6621e-01

 Columns 1171 through 1179:

   3.7137e-01   3.7634e-01   3.8020e-01   3.8404e-01   3.8797e-01   3.9217e-01   3.9600e-01   3.9967e-01   4.0448e-01

 Columns 1180 through 1188:

   4.0871e-01   4.1298e-01   4.1567e-01   4.1911e-01   4.2030e-01   4.2448e-01   4.2604e-01   4.2933e-01   4.3032e-01

 Columns 1189 through 1197:

   4.3423e-01   4.3654e-01   4.4217e-01   4.4476e-01   4.5100e-01   4.5366e-01   4.5996e-01   4.6094e-01   4.6698e-01

 Columns 1198 through 1206:

   4.6879e-01   4.7403e-01   4.7596e-01   4.8288e-01   4.8449e-01   4.8995e-01   4.9255e-01   4.9734e-01   4.9853e-01

 Columns 1207 through 1215:

   5.0378e-01   5.0514e-01   5.0659e-01   5.0536e-01   5.0510e-01   5.0189e-01   5.0130e-01   4.9646e-01   4.9333e-01

 Columns 1216 through 1224:

   4.8537e-01   4.7868e-01   4.7494e-01   4.7499e-01   4.7384e-01   4.7555e-01   4.7460e-01   4.7470e-01   4.7232e-01

 Columns 1225 through 1233:

   4.7057e-01   4.6857e-01   4.6774e-01   4.6525e-01   4.6500e-01   4.6302e-01   4.6285e-01   4.6144e-01   4.6060e-01

 Columns 1234 through 1242:

   4.5943e-01   4.5827e-01   4.5605e-01   4.5506e-01   4.5392e-01   4.5253e-01   4.4942e-01   4.4675e-01   4.4418e-01

 Columns 1243 through 1251:

   4.4191e-01   4.3768e-01   4.3399e-01   4.3053e-01   4.2668e-01   4.2268e-01   4.1804e-01   4.1158e-01   4.0633e-01

 Columns 1252 through 1260:

   4.0382e-01   4.0390e-01   4.0383e-01   4.0520e-01   4.0559e-01   4.0835e-01   4.0954e-01   4.1420e-01   4.1531e-01

 Columns 1261 through 1269:

   4.1909e-01   4.1861e-01   4.2073e-01   4.1988e-01   4.2428e-01   4.2228e-01   4.2265e-01   4.1915e-01   4.2084e-01

 Columns 1270 through 1278:

   4.2026e-01   4.2417e-01   4.2260e-01   4.2323e-01   4.2333e-01   4.2793e-01   4.2926e-01   4.3499e-01   4.3633e-01

 Columns 1279 through 1287:

   4.4185e-01   4.4411e-01   4.5102e-01   4.5235e-01   4.5596e-01   4.5709e-01   4.6132e-01   4.6222e-01   4.6650e-01

 Columns 1288 through 1296:

   4.6800e-01   4.6998e-01   4.7081e-01   4.7297e-01   4.7347e-01   4.7504e-01   4.7511e-01   4.7670e-01   4.7688e-01

 Columns 1297 through 1305:

   4.7899e-01   4.7966e-01   4.8074e-01   4.8075e-01   4.8175e-01   4.8157e-01   4.8176e-01   4.8125e-01   4.8171e-01

 Columns 1306 through 1314:

   4.8216e-01   4.8276e-01   4.8327e-01   4.8360e-01   4.8298e-01   4.8204e-01   4.8112e-01   4.7884e-01   4.7791e-01

 Columns 1315 through 1323:

   4.7615e-01   4.7565e-01   4.7566e-01   4.7623e-01   4.7468e-01   4.7223e-01   4.6889e-01   4.6821e-01   4.6585e-01

 Columns 1324 through 1332:

   4.6446e-01   4.6060e-01   4.5719e-01   4.5303e-01   4.5124e-01   4.4536e-01   4.4322e-01   4.3680e-01   4.3320e-01

 Columns 1333 through 1341:

   4.2652e-01   4.2311e-01   4.1619e-01   4.1264e-01   4.0610e-01   4.0466e-01   3.9791e-01   3.9647e-01   3.8932e-01

 Columns 1342 through 1350:

   3.8762e-01   3.8209e-01   3.8076e-01   3.7304e-01   3.7268e-01   3.6786e-01   3.6741e-01   3.6227e-01   3.6179e-01

 Columns 1351 through 1359:

   3.5720e-01   3.5712e-01   3.5260e-01   3.5317e-01   3.5155e-01   3.5126e-01   3.4891e-01   3.4806e-01   3.4666e-01

 Columns 1360 through 1368:

   3.4675e-01   3.4577e-01   3.4599e-01   3.4588e-01   3.4450e-01   3.4286e-01   3.4117e-01   3.4052e-01   3.4022e-01

 Columns 1369 through 1377:

   3.4025e-01   3.3990e-01   3.4108e-01   3.4234e-01   3.4804e-01   3.5318e-01   3.5581e-01   3.5582e-01   3.5870e-01

 Columns 1378 through 1386:

   3.5998e-01   3.6326e-01   3.6342e-01   3.6725e-01   3.6778e-01   3.7300e-01   3.7371e-01   3.7781e-01   3.7942e-01

 Columns 1387 through 1395:

   3.8563e-01   3.8837e-01   3.9423e-01   3.9562e-01   4.0134e-01   4.0385e-01   4.1237e-01   4.1476e-01   4.2049e-01

 Columns 1396 through 1404:

   4.2267e-01   4.2987e-01   4.3377e-01   4.4077e-01   4.4353e-01   4.4713e-01   4.4903e-01   4.5374e-01   4.5538e-01

 Columns 1405 through 1413:

   4.5882e-01   4.6092e-01   4.6376e-01   4.6505e-01   4.7023e-01   4.7322e-01   4.7790e-01   4.8113e-01   4.8484e-01

 Columns 1414 through 1422:

   4.8672e-01   4.9062e-01   4.9251e-01   4.9334e-01   4.9564e-01   4.9770e-01   4.9865e-01   4.9920e-01   5.0064e-01

 Columns 1423 through 1431:

   5.0147e-01   5.0276e-01   5.0307e-01   5.0388e-01   5.0249e-01   5.0315e-01   5.0317e-01   5.0510e-01   5.0522e-01

 Columns 1432 through 1440:

   5.0560e-01   5.0335e-01   5.0367e-01   5.0194e-01   5.0173e-01   5.0106e-01   5.0215e-01   5.0201e-01   5.0246e-01

 Columns 1441 through 1449:

   5.0079e-01   5.0190e-01   5.0140e-01   5.0194e-01   5.0097e-01   5.0145e-01   4.9982e-01   4.9978e-01   4.9808e-01

 Columns 1450 through 1458:

   4.9929e-01   4.9688e-01   4.9550e-01   4.9269e-01   4.9542e-01   4.9608e-01   4.9760e-01   4.9521e-01   4.9852e-01

 Columns 1459 through 1467:

   4.9887e-01   5.0011e-01   5.0070e-01   5.0139e-01   5.0215e-01   5.0456e-01   5.0532e-01   5.0642e-01   5.0727e-01

 Columns 1468 through 1476:

   5.0851e-01   5.0948e-01   5.1020e-01   5.0913e-01   5.0930e-01   5.0601e-01   5.0581e-01   5.0572e-01   5.0320e-01

 Columns 1477 through 1485:

   4.9350e-01   4.8987e-01   4.8560e-01   4.8509e-01   4.8161e-01   4.8178e-01   4.7663e-01   4.7520e-01   4.7057e-01

 Columns 1486 through 1494:

   4.7036e-01   4.6829e-01   4.6889e-01   4.6551e-01   4.6667e-01   4.6403e-01   4.6371e-01   4.5957e-01   4.5915e-01

 Columns 1495 through 1503:

   4.5565e-01   4.5702e-01   4.5521e-01   4.5681e-01   4.5518e-01   4.5363e-01   4.5307e-01   4.5452e-01   4.5475e-01

 Columns 1504 through 1512:

   4.5670e-01   4.5568e-01   4.5765e-01   4.5446e-01   4.5447e-01   4.4774e-01   4.4646e-01   4.4224e-01   4.4386e-01

 Columns 1513 through 1521:

   4.3878e-01   4.4261e-01   4.4261e-01   4.4411e-01   4.4338e-01   4.4909e-01   4.4835e-01   4.5207e-01   4.5123e-01

 Columns 1522 through 1530:

   4.5992e-01   4.5853e-01   4.6162e-01   4.5551e-01   4.5902e-01   4.5572e-01   4.5927e-01   4.5329e-01   4.5592e-01

 Columns 1531 through 1539:

   4.4830e-01   4.4847e-01   4.3984e-01   4.4098e-01   4.3840e-01   4.4122e-01   4.3886e-01   4.4545e-01   4.4689e-01

 Columns 1540 through 1548:

   4.5245e-01   4.5237e-01   4.5712e-01   4.5900e-01   4.6260e-01   4.6165e-01   4.6340e-01   4.6476e-01   4.6878e-01

 Columns 1549 through 1557:

   4.7127e-01   4.7403e-01   4.7374e-01   4.7354e-01   4.7297e-01   4.7388e-01   4.7412e-01   4.7341e-01   4.7209e-01

 Columns 1558 through 1566:

   4.7128e-01   4.7128e-01   4.7077e-01   4.6880e-01   4.6918e-01   4.6959e-01   4.6943e-01   4.6814e-01   4.6645e-01

 Columns 1567 through 1575:

   4.6531e-01   4.6515e-01   4.6323e-01   4.6402e-01   4.6495e-01   4.6453e-01   4.6298e-01   4.6153e-01   4.5999e-01

 Columns 1576 through 1584:

   4.5915e-01   4.5889e-01   4.5499e-01   4.5093e-01   4.4912e-01   4.5145e-01   4.5432e-01   4.5661e-01   4.5605e-01

 Columns 1585 through 1593:

   4.5053e-01   4.4442e-01   4.4125e-01   4.4248e-01   4.4596e-01   4.4756e-01   4.5035e-01   4.5191e-01   4.5355e-01

 Columns 1594 through 1602:

   4.5342e-01   4.5384e-01   4.5189e-01   4.5026e-01   4.4862e-01   4.4665e-01   4.4420e-01   4.4298e-01   4.4271e-01

 Columns 1603 through 1611:

   4.4308e-01   4.4407e-01   4.4463e-01   4.4445e-01   4.4578e-01   4.4563e-01   4.4915e-01   4.5104e-01   4.5877e-01

 Columns 1612 through 1620:

   4.6226e-01   4.7104e-01   4.7238e-01   4.7690e-01   4.7785e-01   4.8521e-01   4.8875e-01   4.8742e-01   4.8391e-01

 Columns 1621 through 1629:

   4.7350e-01   4.6581e-01   4.5709e-01   4.5421e-01   4.4578e-01   4.4287e-01   4.3765e-01   4.3662e-01   4.3610e-01

 Columns 1630 through 1638:

   4.3585e-01   4.3125e-01   4.2726e-01   3.8205e-01   2.9955e-01   1.6375e-01   9.0120e-02   5.9069e-02   5.7974e-02

 Columns 1639 through 1647:

   6.8454e-02   7.6004e-02   7.5667e-02   7.4420e-02   7.2755e-02   7.3963e-02   6.8102e-02   6.4986e-02   5.1351e-02

 Columns 1648 through 1656:

   2.9563e-02   8.0917e-03   1.5402e-03   4.4809e-04   3.5616e-04   2.6864e-04   3.2243e-04   3.0868e-04   3.6325e-04

 Columns 1657 through 1665:

   2.5077e-04   1.7006e-04   1.0866e-04   1.0724e-04   9.5063e-05   9.2016e-05   8.2903e-05   8.6320e-05   8.2091e-05

 Columns 1666 through 1674:

   8.2091e-05   7.5484e-05   7.5484e-05   7.0329e-05   7.0329e-05   6.4875e-05   6.4875e-05   5.9336e-05   5.9336e-05

 Columns 1675 through 1683:

   5.1647e-05   5.1647e-05   5.0921e-05   5.0921e-05   5.4993e-05   5.4993e-05   5.2430e-05   5.3000e-05   4.2904e-05

 Columns 1684 through 1692:

   4.2690e-05   3.3719e-05   3.3420e-05   3.2366e-05   3.2594e-05   3.7820e-05   3.7820e-05   5.1348e-05   5.1348e-05

 Columns 1693 through 1701:

   7.2921e-05   7.2921e-05   9.3155e-05   9.3155e-05   1.3237e-04   1.3221e-04   1.3804e-04   1.3737e-04   1.4940e-04

 Columns 1702 through 1710:

   1.4950e-04   1.7439e-04   1.7488e-04   2.0155e-04   2.0209e-04   2.2590e-04   2.2661e-04   2.4345e-04   2.4483e-04

 Columns 1711 through 1719:

   2.6439e-04   2.6692e-04   3.1988e-04   3.2385e-04   3.4216e-04   3.3877e-04   3.5263e-04   3.6040e-04   3.7776e-04

 Columns 1720 through 1728:

   3.7386e-04   3.9528e-04   3.9398e-04   4.2686e-04   4.2669e-04   4.4417e-04   4.4432e-04   4.6314e-04   4.6274e-04

 Columns 1729 through 1737:

   5.1544e-04   5.1701e-04   5.3176e-04   5.3670e-04   5.5294e-04   5.5107e-04   5.6240e-04   5.5943e-04   5.6811e-04

 Columns 1738 through 1746:

   5.7209e-04   5.9592e-04   5.9672e-04   6.0673e-04   6.0485e-04   6.1689e-04   6.1878e-04   6.5369e-04   6.5630e-04

 Columns 1747 through 1755:

   6.5238e-04   6.5690e-04   6.5399e-04   6.5600e-04   6.4937e-04   6.4478e-04   6.4421e-04   6.5580e-04   6.7605e-04

 Columns 1756 through 1764:

   6.8035e-04   6.9586e-04   6.9819e-04   7.1048e-04   7.2015e-04   7.3178e-04   7.3486e-04   7.4345e-04   7.3806e-04

 Columns 1765 through 1773:

   7.2989e-04   7.4236e-04   7.7829e-04   8.2297e-04   8.3422e-04   8.8455e-04   9.1700e-04   9.5829e-04   1.0015e-03

 Columns 1774 through 1782:

   1.0588e-03   1.1222e-03   1.2061e-03   1.3279e-03   1.3978e-03   1.4977e-03   1.5575e-03   1.6023e-03   1.7051e-03

 Columns 1783 through 1791:

   1.7906e-03   1.8351e-03   1.8712e-03   1.8927e-03   1.9591e-03   2.0396e-03   2.1504e-03   2.2431e-03   2.3497e-03

 Columns 1792 through 1800:

   2.4524e-03   2.4014e-03   2.4422e-03   2.5460e-03   2.5455e-03   2.5380e-03   2.5989e-03   2.6871e-03   2.7389e-03

 Columns 1801 through 1809:

   2.6905e-03   2.6142e-03   2.5902e-03   2.6320e-03   2.6624e-03   2.7082e-03   2.7814e-03   2.8606e-03   2.8250e-03

 Columns 1810 through 1818:

   2.7764e-03   2.7554e-03   2.7466e-03   2.7418e-03   2.7610e-03   2.7886e-03   2.8168e-03   2.6796e-03   2.7026e-03

 Columns 1819 through 1827:

   2.6917e-03   2.6267e-03   2.6247e-03   2.6670e-03   2.6685e-03   2.6493e-03   2.6402e-03   2.6831e-03   2.6451e-03

 Columns 1828 through 1836:

   2.5656e-03   2.5130e-03   2.5414e-03   2.5051e-03   2.4716e-03   2.4382e-03   2.4813e-03   2.4672e-03   2.3650e-03

 Columns 1837 through 1845:

   2.3100e-03   2.3020e-03   2.3049e-03   2.3168e-03   2.3086e-03   2.3098e-03   2.2749e-03   2.2417e-03   2.2151e-03

 Columns 1846 through 1854:

   2.1665e-03   2.0888e-03   2.0703e-03   2.0685e-03   2.0973e-03   2.1094e-03   2.0965e-03   2.1108e-03   2.0995e-03

 Columns 1855 through 1863:

   2.0506e-03   2.0458e-03   2.0407e-03   2.0246e-03   2.0100e-03   2.0090e-03   1.9678e-03   1.9222e-03   1.8582e-03

 Columns 1864 through 1872:

   1.8683e-03   1.7677e-03   1.8050e-03   1.8450e-03   1.8264e-03   1.7985e-03   1.7735e-03   1.7368e-03   1.7374e-03

 Columns 1873 through 1881:

   1.6340e-03   1.6109e-03   1.6124e-03   1.6097e-03   1.5823e-03   1.5510e-03   1.5216e-03   1.5150e-03   1.4780e-03

 Columns 1882 through 1890:

   1.4979e-03   1.5446e-03   1.5568e-03   1.5121e-03   1.4965e-03   1.5119e-03   1.5171e-03   1.4923e-03   1.4598e-03

 Columns 1891 through 1899:

   1.4499e-03   1.4423e-03   1.4364e-03   1.4311e-03   1.4382e-03   1.4701e-03   1.4516e-03   1.4573e-03   1.4285e-03

 Columns 1900 through 1908:

   1.3719e-03   1.3290e-03   1.3284e-03   1.3232e-03   1.2983e-03   1.2897e-03   1.3397e-03   1.3282e-03   1.3032e-03

 Columns 1909 through 1917:

   1.2814e-03   1.2650e-03   1.2300e-03   1.2331e-03   1.1747e-03   1.1741e-03   1.1789e-03   1.1823e-03   1.1873e-03

 Columns 1918 through 1920:

   1.1733e-03   1.1322e-03   1.1196e-03

>>
>> meansq(imMatG);
>> imMatGMeanSq = meansq(imMatG);
>> imshow(imMatGMeanSq)
>> imMatGMean = mean(imMatGMeanSq);
>> size(imMatGMean)
ans =

   1   1

>> imMatGmean
error: 'imMatGmean' undefined near line 1, column 1
>> imMatGMean
imMatGMean = 0.3131
>> imMatGMeanSq = std(imMatG);
std      std2     stderr   stdfilt  stdin    stdout
>> imMatGMeanSq = std(imMatG);
std      std2     stderr   stdfilt  stdin    stdout
>> imMatGStd = std(imMatG);
>> imshow(imMatGStd)
>> imMatGGrad = gradient(imMatG);
>> imshow(imMatGGrad)
>> imMatGGrad = gradient(imMatG
>> imMatGGrad = imgradient(imMatG)(1);
>> imMatGGrad = imgradient(imMatG);
>> imshow(imMatGGrad)
>> figure;
>> imMatGGrad2 = imgradient(imMatGGrad);
error: imgradientxy: IMG must be a gray-scale image
error: called from
    imgradientxy at line 58 column 5
    imgradient at line 46 column 6
>> size(imMatGGrad)
ans =

   1080   1920

>> imMatGGrad(400,400)
ans = 0.035511
>> fspecial("laplacian")
ans =

   0.1667   0.6667   0.1667
   0.6667  -3.3333   0.6667
   0.1667   0.6667   0.1667

>> help conv2
'conv2' is a built-in function from the file libinterp/corefcn/conv2.cc

 -- C = conv2 (A, B)
 -- C = conv2 (V1, V2, M)
 -- C = conv2 (..., SHAPE)
     Return the 2-D convolution of A and B.

     The size of the result is determined by the optional SHAPE argument
     which takes the following values

     SHAPE = "full"
          Return the full convolution.  (default)

     SHAPE = "same"
          Return the central part of the convolution with the same size
          as A.  The central part of the convolution begins at the
          indices 'floor ([size(B)/2] + 1)'.

     SHAPE = "valid"
          Return only the parts which do not include zero-padded edges.
          The size of the result is 'max (size (A) - size (B) + 1, 0)'.

     When the third argument is a matrix, return the convolution of the
     matrix M by the vector V1 in the column direction and by the vector
     V2 in the row direction.

     See also: conv, convn.

Additional help for built-in functions and operators is
available in the online version of the manual.  Use the command
'doc <topic>' to search the manual index.

Help and information about Octave is also available on the WWW
at https://www.octave.org and https://octave.discourse.group/c/help/
>> imMatGLaplacian = conv2(imMatG, fspecial ("laplacian"), "same");
>> imshow(imMatGLaplacian )
>> imMatGLaplacian = conv2(imMatG, fspecial ("laplacian"), "full");
>> imshow(imMatGLaplacian )
>> imMatGLaplacian = conv2(imMatG, fspecial ("sobel"), "same");
>> imshow(imMatGLaplacian )
(i-search)`':
