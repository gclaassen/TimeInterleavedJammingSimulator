SNRdB = [-5,-3,0,3,5];
NumPulses = 4;
[Pd,Pfa] = rocsnr(SNRdB,'SignalType','NonfluctuatingNonCoherent', 'NumPulses',NumPulses);
semilogx(Pfa,Pd, 'LineWidth', 2)
set(gca,'YTick',[0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.85 0.9 0.95 0.98 1] );
grid on
xlabel('P_{fa}')
ylabel('P_d')
legend('SNR -5 dB', 'SNR -3 dB', 'SNR 0 dB', 'SNR 3 dB', 'SNR 5 dB', 'location','northwest')