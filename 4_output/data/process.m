% Process the threat and platform files.

if (~exist('threats'))

  threats = loadjson('threats.json');
  platform = loadjson('platform.json');

end

% $$$ fprintf('\n')
% $$$ 
% $$$ fprintf('noise_figure_dB')
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf(' %.2f', threats.threats(counter).emitters.noise_figure_dB)
% $$$ end
% $$$ fprintf('\n\n')
% $$$ 
% $$$ fprintf('start_mode')
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf(' %d', threats.threats(counter).start_mode)
% $$$ end
% $$$ fprintf('\n\n')
% $$$ 
% $$$ fprintf('ws_range_km')
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf(' %.2f', threats.threats(counter).ws_range_km)
% $$$ end
% $$$ fprintf('\n\n')
% $$$ 
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf('%2d power_peak_kW', counter)
% $$$   fprintf('  %6.2f', threats.threats(counter).emitters.modes.power_peak_kW)
% $$$   fprintf('\n')
% $$$ end
% $$$ fprintf('\n')
% $$$ 
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf('%2d gain', counter)
% $$$   fprintf(' %6.2f', threats.threats(counter).emitters.modes.gain)
% $$$   fprintf('\n')
% $$$ end
% $$$ fprintf('\n')
% $$$ 
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf('%2d frequency_MHz', counter)
% $$$   fprintf(' %8.2f', threats.threats(counter).emitters.modes.frequency_MHz)
% $$$   fprintf('\n')
% $$$ end
% $$$ fprintf('\n')
% $$$ 
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf('%2d cpi', counter)
% $$$   fprintf('  %3d', threats.threats(counter).emitters.modes.cpi)
% $$$   fprintf('\n')
% $$$ end
% $$$ fprintf('\n')
% $$$ 
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf('%2d Pd', counter)
% $$$   fprintf(' %6.2f', threats.threats(counter).emitters.modes.Pd)
% $$$   fprintf('\n')
% $$$ end
% $$$ fprintf('\n')
% $$$ 
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf('%2d Pfa', counter)
% $$$   fprintf('  %.2e', threats.threats(counter).emitters.modes.Pfa)
% $$$   fprintf('\n')
% $$$ end
% $$$ fprintf('\n')
% $$$ 
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf('%2d Pd_min', counter)
% $$$   fprintf(' %6.2f', threats.threats(counter).emitters.modes.Pd_min)
% $$$   fprintf('\n')
% $$$ end
% $$$ fprintf('\n')
% $$$ 
% $$$ for counter = 1:numel(threats.threats)
% $$$   fprintf('%2d Pd_cumulative', counter)
% $$$   fprintf(' %6.2f', threats.threats(counter).emitters.modes.Pd_cumulative)
% $$$   fprintf('\n')
% $$$ end
% $$$ fprintf('\n')


% The frequencies need to be rounded to the nearest 0.1 GHz.
% The peak powers need to be rounded to the nearest kW.
% The pulse widths need to be rounded to the nearest 100 ns.
% The PRIs need to be rounded to the nearest 100 microsecond.
% The frequencies need to be rounded to the nearest 0.1 GHz.


% $$$ % Select the threats to use in order of weapon ranges.
% $$$ use(1) = threats.threats(19);
% $$$ use(2) = threats.threats(1);
% $$$ use(3) = threats.threats(20);
% $$$ use(4) = threats.threats(4);
% $$$ use(5) = threats.threats(7);
% $$$ 
% $$$ use(1).radar_name = '1';
% $$$ use(2).radar_name = '2';
% $$$ use(3).radar_name = '3';
% $$$ use(4).radar_name = '4';
% $$$ use(5).radar_name = '5';
% $$$ 
% $$$ % $$$ use(1).ws_range_km = 25;
% $$$ % $$$ use(2).ws_range_km = 50;
% $$$ use(3).ws_range_km = 75;
% $$$ % $$$ use(4).ws_range_km = 100;
% $$$ use(5).ws_range_km = 125;
% $$$ 
% $$$ indx = 0;
% $$$ clear new_threats
% $$$ % Three short-range threats
% $$$ for counter = 1:4
% $$$   indx = indx + 1;
% $$$   new_threats(indx) = use(1);
% $$$ end
% $$$ % Medium-range threats with short pulses
% $$$ for counter = 1:4
% $$$   indx = indx + 1;
% $$$   new_threats(indx) = use(2);
% $$$ end
% $$$ % medium-range threats with long duty cycle
% $$$ for counter = 1:4
% $$$   indx = indx + 1;
% $$$   new_threats(indx) = use(3);
% $$$ end
% $$$ % long-range threats with long pulses
% $$$ for counter = 1:4
% $$$   indx = indx + 1;
% $$$   new_threats(indx) = use(4);
% $$$ end
% $$$ % long-range threats with large variation
% $$$ for counter = 1:4
% $$$   indx = indx + 1;
% $$$   new_threats(indx) = use(5);
% $$$ end 
% $$$ 
% $$$ % Check that there are 20 threats
% $$$ indx
% $$$ 
% $$$ 
% $$$ % Update the radar_id values
% $$$ for counter = 1:numel(new_threats)
% $$$   new_threats(counter).radar_id = counter;
% $$$ end
new_threats = threats.threats;


% Try randomly positioning the threats

% Repeatable results
rand('seed', 11);
rand('state', rand(625, 1));

% Sort the threats by range to start with those with the shortest ranges.
ranges = zeros(1, numel(new_threats));
for counter = 1:numel(new_threats)
  ranges(counter) = new_threats(counter).ws_range_km;
end
% $$$ [ ~, indx ] = sort(ranges);
% $$$ 
% $$$ % Fix the first three threats to make the flight path reasonable.
% $$$ new_threats(indx(1)).location.X_coord =  10e3;
% $$$ new_threats(indx(1)).location.Y_coord =  20e3;
% $$$ new_threats(indx(2)).location.X_coord =  20e3;
% $$$ new_threats(indx(2)).location.Y_coord =   0e3;
% $$$ new_threats(indx(3)).location.X_coord = -30e3;
% $$$ new_threats(indx(3)).location.Y_coord =  10e3;
% $$$ new_threats(indx(4)).location.X_coord = -10e3;
% $$$ new_threats(indx(4)).location.Y_coord =  30e3;
% $$$ 
% $$$ % Randomise the other positions.
% $$$ for counter = 5:numel(new_threats)
% $$$ 
% $$$   do
% $$$     % Random X position rounded to the nearest 10 km.
% $$$ % $$$     do
% $$$       new_threats(indx(counter)).location.X_coord = round((95 - 190*rand)/10)*10e3;
% $$$ % $$$     until (abs(new_threats(indx(counter)).location.X_coord) ...
% $$$ % $$$            >= 10e3)%0.5*new_threats(indx(counter)).ws_range_km
% $$$ 
% $$$     % Ensure that the origin is within the maximum weapon range.
% $$$     temp = sqrt(new_threats(indx(counter)).ws_range_km^2 ...
% $$$                 - (new_threats(indx(counter)).location.X_coord/1000)^2);
% $$$     % Random Y position rounded to the nearest 10 km.
% $$$     new_threats(indx(counter)).location.Y_coord = floor((min(95, temp)*rand)/10)*10e3;
% $$$ 
% $$$     % Determine the ranges to the other threats.
% $$$     distance = 1e6;
% $$$     for counter2 = 1:(counter - 1)
% $$$       temp = sqrt((new_threats(indx(counter)).location.X_coord ...
% $$$                    - new_threats(indx(counter2)).location.X_coord)^2 ...
% $$$                   + (new_threats(indx(counter)).location.Y_coord ...
% $$$                      - new_threats(indx(counter2)).location.Y_coord)^2);
% $$$       distance = min(temp, distance);
% $$$     end
% $$$ 
% $$$   until ((imag(new_threats(indx(counter)).location.Y_coord) == 0) ...
% $$$          & (sqrt(new_threats(indx(counter)).location.X_coord^2 ...
% $$$                  + new_threats(indx(counter)).location.Y_coord^2)/1e3 ...
% $$$             >= 0.85*new_threats(indx(counter)).ws_range_km) ...
% $$$          & (sqrt(new_threats(indx(counter)).location.X_coord^2 ...
% $$$                  + new_threats(indx(counter)).location.Y_coord^2)/1e3 ...
% $$$             <= new_threats(indx(counter)).ws_range_km) ...
% $$$          & (distance >= 20e3))
% $$$ 
% $$$   new_threats(indx(counter)).location.Z_coord = 0;
% $$$ 
% $$$   [ counter indx(counter) ...
% $$$     new_threats(indx(counter)).ws_range_km ...
% $$$     new_threats(indx(counter)).location.X_coord ...
% $$$     new_threats(indx(counter)).location.Y_coord ]
% $$$ end

% Store the positions
positions = zeros(numel(new_threats), 3);
for counter = 1:numel(new_threats)
  positions(counter, :) = ...
      [ new_threats(counter).location.X_coord/1000 ...
        new_threats(counter).location.Y_coord/1000 ...
        new_threats(counter).location.Z_coord/1000 ];
end

% $$$ % Compute the distances between threats.
% $$$ distances = zeros(numel(new_threats), numel(new_threats));
% $$$ for counter = 1:numel(new_threats)
% $$$   distances(:, counter) = sqrt(sum((positions - positions(counter, :)).^2, 2));
% $$$ end
% $$$ min(distances + 1000*eye(size(distances)))
% $$$ 
% $$$ % Check how the ranges to the origin compare to the weapon ranges.
% $$$ [ positions(:, 1:2) sqrt(sum((positions).^2, 2)) ranges' sqrt(sum((positions).^2, 2))./ranges' ]


% Set the waypoints.

% Copy from the file.
new_platform = platform.platform;
% $$$ new_platform.flightpath(end) = [];

% $$$ % $$$ % Set new way points.
% $$$ % $$$ new_platform.flightpath(1).X_coord = -20e3;
% $$$ % $$$ new_platform.flightpath(1).Y_coord =   0e3;
% $$$ % $$$ new_platform.flightpath(1).Z_coord =   1e3; %2e3;
% $$$ % $$$ new_platform.flightpath(2).X_coord = -10e3;
% $$$ % $$$ new_platform.flightpath(2).Y_coord =  10e3;
% $$$ % $$$ new_platform.flightpath(2).Z_coord =   1e3; %1e3;
% $$$ % $$$ new_platform.flightpath(3).X_coord = -10e3;
% $$$ % $$$ new_platform.flightpath(3).Y_coord =  20e3;
% $$$ % $$$ new_platform.flightpath(3).Z_coord =   1e3; %150;
% $$$ % $$$ new_platform.flightpath(4).X_coord =  10e3;
% $$$ % $$$ new_platform.flightpath(4).Y_coord =  10e3;
% $$$ % $$$ new_platform.flightpath(4).Z_coord =   1e3; %1e3;
% $$$ % $$$ new_platform.flightpath(5).X_coord =   0e3;
% $$$ % $$$ new_platform.flightpath(5).Y_coord =   0e3;
% $$$ % $$$ new_platform.flightpath(5).Z_coord =   1e3; %2e3;
% $$$ new_platform.flightpath(1).X_coord = -10e3;
% $$$ new_platform.flightpath(1).Y_coord =   0e3;
% $$$ new_platform.flightpath(1).Z_coord =   1e3; %1e3;
% $$$ new_platform.flightpath(2).X_coord = -10e3;
% $$$ new_platform.flightpath(2).Y_coord =  10e3;
% $$$ new_platform.flightpath(2).Z_coord =   1e3; %150;
% $$$ new_platform.flightpath(3).X_coord =   0e3;
% $$$ new_platform.flightpath(3).Y_coord =  10e3;
% $$$ new_platform.flightpath(3).Z_coord =   1e3; %1e3;
% $$$ new_platform.flightpath(4).X_coord =   0e3/2;
% $$$ new_platform.flightpath(4).Y_coord =   0e3/2;
% $$$ new_platform.flightpath(4).Z_coord =   1e3; %2e3;

% Store the waypoints.
waypoints = zeros(numel(new_platform(1).flightpath), 3);
for counter = 1:numel(new_platform(1).flightpath)
  waypoints(counter, :) = ...
      [ new_platform(1).flightpath(counter).X_coord/1000 ...
        new_platform(1).flightpath(counter).Y_coord/1000 ...
        new_platform(1).flightpath(counter).Z_coord/1000 ];
end

% $$$ % Total distance travelled
% $$$ sum(sqrt(sum((waypoints(2:end, 1:2) - waypoints(1:(end - 1), 1:2)).^2, 2)))

% Distances from the threats to each of the waypoints.
positions_waypoints = zeros(size(positions, 1), size(waypoints, 1));
for counter = 1:size(waypoints, 1)
  positions_waypoints(:, counter) = sqrt(sum((positions(:, 1:2) - waypoints(counter, 1:2)).^2, 2));
end

% $$$ % Check how many waypoints are in weapon range.
% $$$ [ positions ranges' (positions_waypoints <= ranges') sum(positions_waypoints <= ranges', 2) ]



% $$$ savejson('threats', new_threats, 'threats_new.json');
% $$$ savejson('platform', new_platform, 'platform_new.json');


% Save data for gnuplot

temp = [];
for counter = 1:numel(new_threats)
  temp = [ temp ; ...
           new_threats(counter).radar_id str2double(new_threats(counter).radar_name) ...
           new_threats(counter).location.X_coord ...
           new_threats(counter).location.Y_coord ...
           new_threats(counter).location.Z_coord ...
         ];
end
% $$$ temp
save -ascii threats.dat temp

temp = [];
for counter = 1:numel(new_platform.flightpath)
  temp = [ temp ; ...
           counter ...
           new_platform.flightpath(counter).X_coord ...
           new_platform.flightpath(counter).Y_coord ...
           new_platform.flightpath(counter).Z_coord ...
         ];
end
% $$$ temp
save -ascii waypoints.dat temp



% $$$ figure(1)
% $$$ 
% $$$ % Set the default font and font size.
% $$$ % Use Times or Helvetica to best match the font in the document.
% $$$ set(0, "defaulttextfontname", "Times"); %"Helvetica");
% $$$ set(0, "defaultaxesfontname", "Times"); %"Helvetica");
% $$$ set(0, "defaultaxesfontsize", 18);
% $$$ 
% $$$ % Set the default plot line width and axis line width
% $$$ set(0, "defaultlinelinewidth", 2);
% $$$ set(0, "defaultaxeslinewidth", 2);
% $$$ 
% $$$ % Try plotting the positions of the threats
% $$$ for counter = 1:numel(new_threats)
% $$$   plot3(positions(counter, 1), positions(counter, 2), positions(counter, 3), 'kx')
% $$$   hold on
% $$$   text(positions(counter, 1), positions(counter, 2) + 7, positions(counter, 3), ...
% $$$        sprintf('%d', new_threats(counter).radar_id), ...
% $$$        'horizontalalignment', 'center', 'verticalalignment', 'middle', ...
% $$$        'fontname', 'Times', 'fontsize', 18)
% $$$ end
% $$$ 
% $$$ % Flight path
% $$$ for counter = 1:numel(new_platform(1).flightpath)
% $$$   text(waypoints(counter, 1) + (5 - 10*(min(abs(counter - [ 3 4 ])) > 0)), ...
% $$$        waypoints(counter, 2), ...
% $$$        waypoints(counter, 3)*10, ...
% $$$        sprintf('%d', counter), ...
% $$$        'horizontalalignment', 'center', 'verticalalignment', 'middle', ...
% $$$        'fontname', 'Times', 'fontsize', 18, 'color', [ 0 0 1 ])
% $$$ end
% $$$ plot3(waypoints(:, 1), waypoints(:, 2), waypoints(:, 3)*10, 'b')
% $$$ plot3(waypoints(:, 1), waypoints(:, 2), waypoints(:, 3)*10, 'bo')
% $$$ 
% $$$ hold off
% $$$ 
% $$$ view(0, 90)  % Top view
% $$$ 
% $$$ axis equal
% $$$ grid on
% $$$ 
% $$$ xlim([ -100 100 ])
% $$$ xticks(-100:20:100)
% $$$ ylim([ -7 100 ])
% $$$ 
% $$$ xlabel('X (km)')
% $$$ ylabel('Y (km)')
% $$$ zlabel('Z (\times100 m)')
% $$$ 
% $$$ print -dpdf -color positions.pdf






% $$$ % Generate the first table.
% $$$ fprintf('\\begin{table*}[t]\n')
% $$$ fprintf('  \\centering%%\n')
% $$$ fprintf('  \\warren{This is the newest version of this table, and is automatically generated from the threats.json file.}%%\n')
% $$$ fprintf('  \\caption{Radar simulation parameters}\n')
% $$$ fprintf('  \\label{tab:radars}\n')
% $$$ fprintf('    \\renewcommand{\\arraystretch}{1.1}\n')
% $$$ fprintf('    \\glsunset{pri}\n')
% $$$ %fprintf('    \\begin{tabulary}{\\textwidth}{\n')
% $$$ fprintf('    \\begin{tabular}{\n')
% $$$ 
% $$$ fprintf('        >{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Radar}}\n')
% $$$ fprintf('        |\n')
% $$$ fprintf('        >{\\raggedleft\\arraybackslash\\hspace{0pt}}m{\\widthof{0\\,000}}\n')
% $$$ fprintf('        m{(\\widthof{Width}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')
% $$$ fprintf('        m{(\\widthof{(pulses)}-\\widthof{128})/2} @{} r @{} c\n')
% $$$ fprintf('        |\n')
% $$$ fprintf('        >{\\raggedleft\\arraybackslash\\hspace{0pt}}m{\\widthof{0\\,000}}\n')
% $$$ fprintf('        m{(\\widthof{Width}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')
% $$$ fprintf('        m{(\\widthof{(pulses)}-\\widthof{128})/2} @{} r @{} c\n')
% $$$ fprintf('        |\n')
% $$$ fprintf('        >{\\raggedleft\\arraybackslash\\hspace{0pt}}m{\\widthof{\\gls{pri}}}\n')
% $$$ fprintf('        m{(\\widthof{Width}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')
% $$$ fprintf('        m{(\\widthof{(pulses)}-\\widthof{128})/2} @{} r @{} c\n')
% $$$ fprintf('        |\n')
% $$$ fprintf('        >{\\raggedleft\\arraybackslash\\hspace{0pt}}m{\\widthof{0\\,000}}\n')
% $$$ fprintf('        m{(\\widthof{Width}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')
% $$$ fprintf('        m{(\\widthof{(pulses)}-\\widthof{128})/2} @{} r @{} c\n')
% $$$ 
% $$$ fprintf('      }\n')
% $$$ fprintf('      \\hline\n')
% $$$ fprintf('      & \\multicolumn{8}{c|}{\\glsreset{ts}\\Gls{ts}}\n')
% $$$ fprintf('      & \\multicolumn{8}{c|}{\\glsreset{ta}\\Gls{ta}}\n')
% $$$ fprintf('      & \\multicolumn{8}{c|}{\\glsreset{tt}\\Gls{tt}}\n')
% $$$ fprintf('      & \\multicolumn{8}{c }{\\glsreset{mg}\\Gls{mg}} \\\\\n')
% $$$ fprintf('      Radar ID \n')
% $$$ fprintf('            & \\centering\\gls{pri}\n')
% $$$ fprintf('            & \\multicolumn{4}{>{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Width}}}{Pulse Width}\n')
% $$$ fprintf('            & \\multicolumn{3}{c|}{\\gls{cpi}}\n')
% $$$ fprintf('            & \\centering\\gls{pri}\n')
% $$$ fprintf('            & \\multicolumn{4}{>{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Width}}}{Pulse Width}\n')
% $$$ fprintf('            & \\multicolumn{3}{c|}{\\gls{cpi}}\n')
% $$$ fprintf('            & \\centering\\gls{pri}\n')
% $$$ fprintf('            & \\multicolumn{4}{>{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Width}}}{Pulse Width}\n')
% $$$ fprintf('            & \\multicolumn{3}{c|}{\\gls{cpi}}\n')
% $$$ fprintf('            & \\centering\\gls{pri}\n')
% $$$ fprintf('            & \\multicolumn{4}{>{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Width}}}{Pulse Width}\n')
% $$$ fprintf('            & \\multicolumn{3}{c}{\\gls{cpi}} \\\\%%[-0.3em]\n')
% $$$ fprintf('            & \\centering(\\textmu{}s) & \\multicolumn{4}{c}{(\\textmu{}s)} & \\multicolumn{3}{c|}{(pulses)}\n')
% $$$ fprintf('            & \\centering(\\textmu{}s) & \\multicolumn{4}{c}{(\\textmu{}s)} & \\multicolumn{3}{c|}{(pulses)}\n')
% $$$ fprintf('            & \\centering(\\textmu{}s) & \\multicolumn{4}{c}{(\\textmu{}s)} & \\multicolumn{3}{c|}{(pulses)}\n')
% $$$ fprintf('            & \\centering(\\textmu{}s) & \\multicolumn{4}{c}{(\\textmu{}s)} & \\multicolumn{3}{c }{(pulses)} \\\\\n')
% $$$ fprintf('      \\hline\n')
% $$$ 
% $$$ for counter = 1:numel(new_threats)
% $$$ 
% $$$   fprintf('      %2d', counter)
% $$$ 
% $$$   for counter_modes = 1:numel(new_threats(1).emitters.modes)
% $$$ 
% $$$     temp = round(new_threats(counter).emitters.modes(counter_modes).pri_us);
% $$$     if (temp >= 1000)
% $$$       fprintf(' & %d\\,%03d', floor(temp/1000), rem(temp, 1000))
% $$$     else
% $$$       fprintf(' & %6d', temp)
% $$$     end
% $$$ 
% $$$     temp = round(new_threats(counter).emitters.modes(counter_modes).pulse_width_us*10)/10;
% $$$     fprintf(' & & %2d&%01d &', floor(temp), 10*(temp - floor(temp)))
% $$$ % $$$     % This looks strange.
% $$$ % $$$     if (temp == floor(temp))
% $$$ % $$$       fprintf(' & & %2d &    &', temp)
% $$$ % $$$     else
% $$$ % $$$       fprintf(' & & %2d & .%1d &', floor(temp), 10*(temp - floor(temp)))
% $$$ % $$$     end
% $$$ 
% $$$     temp = new_threats(counter).emitters.modes(counter_modes).cpi;
% $$$     fprintf(' & & %3d &', temp)
% $$$ 
% $$$   end
% $$$ 
% $$$   fprintf(' \\\\\n')
% $$$ 
% $$$ end
% $$$ 
% $$$ fprintf('      \\hline\n')
% $$$ fprintf('    \\end{tabular}\n')
% $$$ fprintf('    \\glsreset{pri}\n')
% $$$ fprintf('\\end{table*}\n\n\n')
% $$$ 
% $$$ 
% $$$ 
% $$$ 
% $$$ 
% $$$ 
% $$$ % Generate the second table.
% $$$ fprintf('\\begin{table}[t]\n')
% $$$ fprintf('  \\centering%%\n')
% $$$ fprintf('  \\warren{This is the newest version of this table, and is automatically generated from the threats.json file.}%%\n')
% $$$ fprintf('  \\caption{Other Radar simulation parameters}\n')
% $$$ fprintf('  \\smallrrr%%\n')
% $$$ fprintf('  %%  \\resizebox{21pc}{!}{%%\n')
% $$$ fprintf('  \\renewcommand{\\arraystretch}{1.1}%%\n')
% $$$ fprintf('  \\begin{tabular}{%%x}{30pc}{%%\n')
% $$$ fprintf('      @{~~}\n')
% $$$ fprintf('      c\n')
% $$$ %fprintf('      @{~\\,} | @{~\\,}\n')
% $$$ fprintf('      |\n')
% $$$ fprintf('      m{(\\widthof{Weapon}-\\widthof{000})/2} @{} r @{} c\n')
% $$$ %fprintf('      @{~\\,} | @{~\\,}\n')
% $$$ fprintf('      |\n')
% $$$ fprintf('      r\n') % Only one column here because the number is wider than the text
% $$$ fprintf('      @{~~~}\n')
% $$$ fprintf('      m{(\\widthof{(km)}-\\widthof{--00})/2} @{} r @{} c\n')
% $$$ %fprintf('      @{~\\,} | @{~\\,}\n')
% $$$ fprintf('      |\n')
% $$$ fprintf('      m{(\\widthof{Power}-\\widthof{000})/2} @{} r @{} c\n')
% $$$ fprintf('      @{~~~}\n')
% $$$ fprintf('      c\n')
% $$$ fprintf('      @{~~~}\n')
% $$$ fprintf('      m{(\\widthof{quency}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')
% $$$ fprintf('      @{~~}\n')
% $$$ fprintf('    }\n')
% $$$ fprintf('    \\hline\n')
% $$$ fprintf('    \\multirow{3}{*}{\\parbox{\\widthof{Radar}}{\\centering Radar ID}}\n')
% $$$ fprintf('    & \\multicolumn{3}{c|}{\\multirow{2}{*}{\\parbox{\\widthof{Weapon}}{\\centering Weapon Range}}}\n')
% $$$ fprintf('    & \\multicolumn{4}{c|}{Position}\n')
% $$$ fprintf('    & \\multicolumn{3}{c@{~~~}}{\\multirow{2}{*}{\\parbox{\\widthof{Power}}{\\centering Peak Power}}}\n')
% $$$ fprintf('    & \\multirow{2}{*}{\\parbox{\\widthof{Antenna}}{\\centering Antenna Gain}}\n')
% $$$ fprintf('    & \\multicolumn{4}{@{}c}{\\multirow{2}{*}{\\parbox{\\widthof{quency}}{\\centering Fre-quency}}} \\\\\n')
% $$$ fprintf('    & & & & \\multicolumn{1}{c}{X} & \\multicolumn{3}{@{}c|}{Y} \\\\\n')
% $$$ fprintf('    & \\multicolumn{3}{c|}{(km)} & \\multicolumn{1}{c}{(km)} & \\multicolumn{3}{@{}c|}{(km)} & \\multicolumn{3}{c@{~~~}}{(kW)} & (dBi) & \\multicolumn{4}{@{}c}{(GHz)} \\\\\n')
% $$$ fprintf('    \\hline\n')
% $$$ 
% $$$ for counter = 1:numel(new_threats)
% $$$ 
% $$$   fprintf('    %2d', counter)
% $$$ 
% $$$   fprintf(' & & %3d &', new_threats(counter).ws_range_km)
% $$$ 
% $$$   temp = round(new_threats(counter).location.X_coord/1000);
% $$$   if (temp < 0)
% $$$     fprintf(' &%s--%d', repmat(' ', 1, 3 - floor(log10(abs(temp)))), abs(temp))
% $$$   else
% $$$     fprintf(' & %5d', temp)
% $$$   end
% $$$ 
% $$$   temp = round(new_threats(counter).location.Y_coord/1000);
% $$$   if (temp < 0)
% $$$     fprintf(' & &%s--%d &', repmat(' ', 1, 3 - floor(log10(abs(temp)))), abs(temp))
% $$$   else
% $$$     fprintf(' & & %5d &', temp)
% $$$   end
% $$$ 
% $$$   temp = round(new_threats(counter).emitters.modes(1).power_peak_kW);
% $$$   fprintf(' & & %3d &', temp)
% $$$ 
% $$$   fprintf(' & %2d', new_threats(counter).emitters.modes(1).gain)
% $$$ 
% $$$   temp = round(new_threats(counter).emitters.modes(1).frequency_MHz/100)/10;
% $$$   fprintf(' & & %2d&%1d &', floor(temp), 10*(temp - floor(temp)))
% $$$ 
% $$$   fprintf(' \\\\\n')
% $$$ 
% $$$ end
% $$$ 
% $$$ fprintf('    \\hline\n')
% $$$ fprintf('  \\end{tabular}\n')
% $$$ fprintf('\\end{table}\n\n\n')
% $$$ 
% $$$ 
% $$$ 
% $$$ 
% $$$ % Generate the flightpath table.
% $$$ fprintf('\\begin{table}[t]\n')
% $$$ fprintf('  \\centering%%\n')
% $$$ fprintf('  \\warren{This is the newest version of this table, and is automatically generated from the threats.json file.}%%\n')
% $$$ fprintf('  \\warren{It is perhaps a little strange having the table oriented this way, but it uses less space than its transpose.}%%\n')
% $$$ fprintf('  \\caption{Flight-path Parameters}\n')
% $$$ fprintf('  \\renewcommand{\\arraystretch}{1.1}%%\n')
% $$$ fprintf('  \\begin{tabular}{ l | c @{~\\,\\,} *{4}{ c } }\n')
% $$$ fprintf('    \\hline\n')
% $$$ fprintf('    \\multirow{2}{*}{Parameter}\n')
% $$$ fprintf('                    & \\multicolumn{5}{c}{Waypoints} \\\\\n                   ')
% $$$ for counter = 1:size(waypoints, 1)
% $$$   fprintf(' & %3d', counter)
% $$$ end
% $$$ fprintf(' \\\\\n')
% $$$ fprintf('    \\hline\n')
% $$$ 
% $$$ fprintf('    X position (km)')
% $$$ for counter = 1:size(waypoints, 1)
% $$$   temp = waypoints(counter, 1);
% $$$   if (temp < 0)
% $$$     fprintf(' & --%d~', abs(temp))
% $$$   else
% $$$     fprintf(' & %3d ', temp)
% $$$   end
% $$$ end
% $$$ fprintf(' \\\\\n')
% $$$ 
% $$$ fprintf('    Y position (km)')
% $$$ for counter = 1:size(waypoints, 1)
% $$$   temp = waypoints(counter, 2);
% $$$   if (temp < 0)
% $$$     fprintf(' & --%d~', abs(temp))
% $$$   else
% $$$     fprintf(' & %3d ', temp)
% $$$   end
% $$$ end
% $$$ fprintf(' \\\\\n')
% $$$ 
% $$$ fprintf('    Z position (km)')
% $$$ for counter = 1:size(waypoints, 1)
% $$$   temp = waypoints(counter, 3);
% $$$   if (temp < 0)
% $$$     fprintf(' & --%d~', abs(temp))
% $$$   else
% $$$     fprintf(' & %3d ', temp)
% $$$   end
% $$$ end
% $$$ fprintf(' \\\\\n')
% $$$ 
% $$$ % $$$ fprintf('    Speed (m/s) &\n')
% $$$ % $$$ for counter = 2:size(waypoints, 1)
% $$$ % $$$   temp = new_platform(1).flightpath(counter).velocity_ms;
% $$$ % $$$   fprintf('              & \\multicolumn{3}{c}{%3d}\n', temp)
% $$$ % $$$ end
% $$$ % $$$ fprintf('              \\\\\n')
% $$$ 
% $$$ fprintf('    \\hline\n')
% $$$ fprintf('  \\end{tabular}\n')
% $$$ fprintf('\\end{table}\n\n\n')








% Generate a single table.

fprintf('\\begin{table*}[t]\n')
fprintf('  \\centering%%\n')
% $$$ fprintf('  \\warren{This is the newest version of this table, and is automatically generated from the threats.json file.}%%\n')
% $$$ fprintf('  \\warren{This table and Fig.~\\ref{fig:positions} replace all the other radar-data and position tables, so they should save a lot of space.}%%\n')
fprintf('  \\caption{Radar simulation parameters}\n')
fprintf('  \\label{tab:radars}\n')
fprintf('    \\renewcommand{\\arraystretch}{1.1}\n')
fprintf('    \\setlength{\\tabcolsep}{0.59em}\n')
fprintf('    \\glsunset{pri}\n')
%fprintf('    \\begin{tabulary}{\\textwidth}{\n')
fprintf('    \\begin{tabular}{\n')

fprintf('        >{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Radar}}\n')
fprintf('        |\n')
fprintf('        m{(\\widthof{Weapon}-\\widthof{000})/2} @{} r @{} c\n')
fprintf('        |\n')
fprintf('        m{(\\widthof{Power}-\\widthof{000})/2} @{} r @{} c\n')
fprintf('        >{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Antenna}}\n')
fprintf('        >{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{quency}}\n')
fprintf('        m{(\\widthof{(pulses)}-\\widthof{128})/2} @{} r @{} c\n')
fprintf('        |\n')
fprintf('        >{\\raggedleft\\arraybackslash\\hspace{0pt}}m{\\widthof{0\\,000}}\n')
fprintf('        m{(\\widthof{Width}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')
fprintf('        |\n')
fprintf('        >{\\raggedleft\\arraybackslash\\hspace{0pt}}m{\\widthof{0\\,000}}\n')
fprintf('        m{(\\widthof{Width}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')
fprintf('        |\n')
fprintf('        >{\\raggedleft\\arraybackslash\\hspace{0pt}}m{\\widthof{\\gls{pri}}}\n')
fprintf('        m{(\\widthof{Width}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')
fprintf('        |\n')
fprintf('        >{\\raggedleft\\arraybackslash\\hspace{0pt}}m{\\widthof{0\\,000}}\n')
fprintf('        m{(\\widthof{Width}-\\widthof{00.0})/2} @{} r @{.} l @{} c\n')

fprintf('      }\n')
fprintf('      \\hline\n')
fprintf('      & & &\n')
fprintf('      & \\multicolumn{8}{c|}{}\n')
fprintf('      & \\multicolumn{5}{c|}{\\Gls{ts}}\n')
fprintf('      & \\multicolumn{5}{c|}{\\Gls{ta}}\n')
fprintf('      & \\multicolumn{5}{c|}{\\Gls{tt}}\n')
fprintf('      & \\multicolumn{5}{c }{\\Gls{mg}} \\\\\n')
fprintf('      Radar Type\n')
fprintf('        & \\multicolumn{3}{c|}{\\parbox{\\widthof{Weapon}}{\\centering Weapon Range}}\n')
fprintf('        & \\multicolumn{3}{c}{\\parbox{\\widthof{Power}}{\\centering Peak Power}}\n')
fprintf('        & Antenna Gain\n')
fprintf('        & Fre-quency\n')
fprintf('        & \\multicolumn{3}{c|}{\\gls{cpi}}\n')
fprintf('        & \\centering\\gls{pri}\n')
fprintf('        & \\multicolumn{4}{>{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Width}}|}{Pulse Width}\n')
fprintf('        & \\centering\\gls{pri}\n')
fprintf('        & \\multicolumn{4}{>{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Width}}|}{Pulse Width}\n')
fprintf('        & \\centering\\gls{pri}\n')
fprintf('        & \\multicolumn{4}{>{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Width}}|}{Pulse Width}\n')
fprintf('        & \\centering\\gls{pri}\n')
fprintf('        & \\multicolumn{4}{>{\\centering\\arraybackslash\\hspace{0pt}}m{\\widthof{Width}}}{Pulse Width}\n')
fprintf('        \\\\%%[-0.3em]\n')
fprintf('        & \\multicolumn{3}{c|}{(km)}\n')
fprintf('        & \\multicolumn{3}{c}{(kW)}\n')
fprintf('        & (dBi)\n')
fprintf('        & (GHz)\n')
fprintf('        & \\multicolumn{3}{c|}{(pulses)}\n')
fprintf('        & \\centering(\\textmu{}s) & \\multicolumn{4}{c|}{(\\textmu{}s)}\n')
fprintf('        & \\centering(\\textmu{}s) & \\multicolumn{4}{c|}{(\\textmu{}s)}\n')
fprintf('        & \\centering(\\textmu{}s) & \\multicolumn{4}{c|}{(\\textmu{}s)}\n')
fprintf('        & \\centering(\\textmu{}s) & \\multicolumn{4}{c}{(\\textmu{}s)}\n')
fprintf('        \\\\\n')
fprintf('      \\hline\n')

previous = '0';
for counter = 1:numel(new_threats)

  if (~strcmp(new_threats(counter).radar_name, previous))
    previous = new_threats(counter).radar_name;
  
    fprintf('       %s', previous)

    fprintf(' & & %3d &', new_threats(counter).ws_range_km)

    temp = round(new_threats(counter).emitters.modes(1).power_peak_kW);
    fprintf(' & & %3d &', temp)

    fprintf(' & %2d', new_threats(counter).emitters.modes(1).gain)

    temp = round(new_threats(counter).emitters.modes(1).frequency_MHz/100)/10;
    fprintf(' & %2d.%1d', floor(temp), 10*(temp - floor(temp)))

    temp = new_threats(counter).emitters.modes(1).cpi;
    fprintf(' & & %3d &', temp)

    for counter_modes = 1:numel(new_threats(1).emitters.modes)

      temp = round(new_threats(counter).emitters.modes(counter_modes).pri_us);
      if (temp >= 1000)
        fprintf(' & %d\\,%03d', floor(temp/1000), rem(temp, 1000))
      else
        fprintf(' & %6d', temp)
      end

      temp = round(new_threats(counter).emitters.modes(counter_modes).pulse_width_us*10)/10;
      fprintf(' & & %2d&%01d &', floor(temp), 10*(temp - floor(temp)))
% $$$       % This looks strange.
% $$$       if (temp == floor(temp))
% $$$         fprintf(' & & %2d &    &', temp)
% $$$       else
% $$$         fprintf(' & & %2d & .%1d &', floor(temp), 10*(temp - floor(temp)))
% $$$       end

    end

    fprintf(' \\\\\n')

  end

end

fprintf('      \\hline\n')
fprintf('    \\end{tabular}\n')
fprintf('    \\glsreset{pri}\n')
fprintf('\\end{table*}\n\n\n')
