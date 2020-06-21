SNRdB = [-5,-3,0,3,5];
NumPulses = 16;
[Pd,Pfa] = rocsnr(SNRdB,'SignalType','NonfluctuatingNonCoherent', 'NumPulses',NumPulses);
semilogx(Pfa,Pd)
grid on
xlabel('P_{fa}')
ylabel('P_d')
legend('SNR -5 dB', 'SNR -3 dB', 'SNR 0 dB', 'SNR 3 dB', 'SNR 5 dB', 'location','northwest')
title('Receiver Operating Characteristic (ROC) Curves')