# It would be better to have a separate Gnuplot file for each figure because that could
#  lead to more efficient compilation because only the new plots would have to be
#  generated each time.

# The actual column width in an IEEE paper is 21 pica = 3.5 in, but this leaves some
#  space around the figure.


# The split across two lines helps when comparing files using diff.
set terminal postscript eps enhanced rounded color \
  "Times,20" lw 2 dl 1 size 3.45,2.5

set grid
#set grid lw 0.5
set border 31 lw 0.75
set style data lines
set clip two

set for [i=1:12] linetype i dashtype i
set dashtype 11 (5, 5.5) 

set linetype 1 lc rgb "red"
set linetype 2 lc rgb "blue"
set linetype 3 lc rgb "#00B300"  # green
set linetype 4 lc rgb "#FF8000"  # orange
set linetype 5 lc rgb "#FF00FF"  # magenta
set linetype 6 lc rgb "#CEE600"  # yellow
set linetype 7 lc rgb "#00CCE6"  # dark cyan
set linetype 8 lc rgb "#000099"  # navy


# My palettes
# Weird (dark to light)
#set palette defined (0 1 1 1, 0 0 0 0, 0.11402 0 0 1, 0.41296 1 0 1, 0.88598 1 1 0, 1 1 1 1)
# Weird (dark to light with boundary)
# 0.1 to 0.9
#set palette defined (0 1 1 1, 0 0 0 0.87704, 0.01752 0 0 1, 0.39120 1 0 1, 0.98248 1 1 0, 1 1 1 0.12296)
# 0.05 to 0.95
set palette defined (0 1 1 1, 0 0 0 0.43852, 0.07113 0 0 1, 0.40329 1 0 1, 0.92887 1 1 0, 1 1 1 0.56148)
# Weird (light to dark, 1 to 0)
#set palette defined (0 1 1 1, 0 1 1 1, 0.11402 1 1 0, 0.58704 1 0 1, 0.88598 0 0 1, 1 0 0 0)
# Weird (light to dark, 0.975 to 0.075, white below zero black above 1)
#set palette defined (0 1 1 1, 0 1 1 0.78074, 0.09891 1 1 0, 0.62449 1 0 1, 0.95664 0 0 1, 1 0 0 0.65777, 1 0 0 0)
# Red-orange-yellow-green
#set palette defined ( 1 1 0 0 , 2 0.87 0.54 0 , 3 0.67 0.79 0 , 4 0 1 0)




set terminal postscript eps enhanced rounded color \
  "Times,20" lw 2 dl 3 size 1.65,3.95

unset border

set grid front x2tics lw 1

set tmargin 3.3
set bmargin 2.05
set lmargin 4.6
set rmargin 0

set pointsize 0.7

set size ratio -1

unset key

set x2label "Radar"
set ylabel offset 1 "Interval"

set x2range [ 1 : 20 ]
set yrange [ 60 : 0 ] reverse

unset xtics
set x2tics out
set x2tics 5,5
set x2tics add (1)
set ytics out
set ytics 0,5
#set ytics add (1)

#set key outside right center vertical Left reverse height 0 width 0 samplen -1 notitle
set key at 11.0,62.5 Left reverse maxrows 1 height 0 width 0.5 samplen 0 notitle

set output 'modesChangeLog_colour.eps'

f(x, y, z) = x==y?z-1:-1000

set multiplot

plot for [c=2:21] 'modesChangeLog.dat' using (f(column(c),0,c)):1 notitle \
         axes x2y1 with points ps 0.4 pt 2  lc rgb "#00B300", \
     for [c=2:21] 'modesChangeLog.dat' using (f(column(c),1,c)):1 notitle \
         axes x2y1 with points ps 0.9 pt 15 lc rgb "#BBD500", \
     for [c=2:21] 'modesChangeLog.dat' using (f(column(c),2,c)):1 notitle \
         axes x2y1 with points ps 0.9 pt 7  lc rgb "#FF8000", \
     for [c=2:21] 'modesChangeLog.dat' using (f(column(c),3,c)):1 notitle \
         axes x2y1 with points ps 1   pt 5  lc rgb "red"

unset x2label
unset ylabel

unset x2tics
unset ytics

set pointsize 1

plot NaN title "TS" with points ps 0.72 lw 1.8 pt 2  lc rgb "#00B300", \
     NaN title "TA" with points ps 1.65 pt 15 lc rgb "#BBD500", \
     NaN title "TT" with points ps 1.65 pt 7  lc rgb "#FF8000", \
     NaN title "MG" with points ps 1.8  pt 5  lc rgb "red"

unset multiplot







set x2label "Radar"
set ylabel offset 1 "Interval"

unset xtics
set x2tics out
set x2tics 5,5
set x2tics add (1)
set ytics out
set ytics 0,5
#set ytics add (1)

set output 'lethalrangeLog_colour.eps'

set multiplot

plot for [c=2:21] 'lethalrangeLog.dat' using (f(column(c),0,c)):1 notitle \
         axes x2y1 with points ps 0.4 pt 2  lc rgb "#00B300", \
     for [c=2:21] 'lethalrangeLog.dat' using (f(column(c),1,c)):1 notitle \
         axes x2y1 with points ps 1   pt 5  lc rgb "red"

#set key outside right center vertical Left reverse height 0 width 0 samplen -1 notitle
set key at 16.2,62.5 Left reverse maxrows 1 height 0 width -3 samplen 0 notitle

unset x2label
unset ylabel

unset x2tics
unset ytics

set pointsize 1

plot NaN title "Out of range" with points ps 0.72 lw 1.8 pt 2  lc rgb "#00B300", \
     NaN title "In range"     with points ps 1.8         pt 5  lc rgb "red"

unset multiplot





set terminal postscript eps enhanced rounded color \
  "Times,20" lw 2 dl 3 size 1.65,4.3

set tmargin 3.3
set bmargin 4.6
set lmargin 4.6
set rmargin 0

set x2label "Radar"
set ylabel offset 1 "Interval"
set cblabel offset 0,0.5 "Coincidence rate"

set x2range [ 1 : 20 ]
set yrange [ 60 : 0 ] reverse
set cbrange [ 0.5 : 1 ]

set x2tics out
set x2tics 5,5
set x2tics add (1)
set ytics out
set ytics 0,5
#set ytics add (1)

#set key outside right center vertical Left reverse height 0 width 0 samplen -1 notitle
#set key at 11.0,62 Left reverse maxrows 1 height 0 width 0.5 samplen 0 notitle
set colorbox horizontal user origin 0.14,0.09 size 0.812,0.02

set output 'coincidenePercLog_colour.eps'

#set palette defined (0 0 0 0.43852, 0.07113 0 0 1, 0.40329 1 0 1, 0.92887 1 1 0, 1 1 1 0.56148)
set palette defined (0 1 1 0.56148, 0.07113 1 1 0, 0.40329 1 0 1, 0.92887 0 0 1, 1 0 0 0.43852)

#plot 'coincidenePercLog.dat' using 1:2:3 notitle axes x2y1 with points ps 1 pt 5 lc pal z
plot for [c=2:21] 'coincidenePercLog.dat' using (c - 1):1:(column(c)) notitle \
     axes x2y1 with points ps 1 pt 5 lc pal z




set cblabel offset 0,0.5 "Jamming rate"

set cbrange [ * : * ]

set cbtics 0.2

set output 'resultJammingLog_colour.eps'

plot for [c=2:21] 'resultJammingLog.dat' using (c - 1):1:(column(c)) notitle \
     axes x2y1 with points ps 1 pt 5 lc pal z




set cblabel offset 0,0.5 "Zone assessment?"

set cbrange [ * : * ]

set cbtics 0.1

set output 'rangeLog_colour.eps'

plot for [c=2:21] 'rangeLog.dat' using (c - 1):1:(column(c)) notitle \
     axes x2y1 with points ps 1 pt 5 lc pal z







reset

set terminal postscript eps enhanced rounded color \
  "Times,20" lw 2 dl 3 size 3.5,2.5

set tmargin 0.45
set bmargin 5.7
set lmargin 5.75
set rmargin 1.45

set linetype 1 lc rgb "red"
set linetype 2 lc rgb "blue"
set linetype 3 lc rgb "#00B300"  # green
set linetype 4 lc rgb "#FF8000"  # orange
set linetype 5 lc rgb "#FF00FF"  # magenta
set linetype 6 lc rgb "#CEE600"  # yellow
set linetype 7 lc rgb "#00CCE6"  # dark cyan
set linetype 8 lc rgb "#000099"  # navy

set for [i=1:12] linetype i dashtype i
set dashtype 11 (5, 5.5) 

set grid
#set grid lw 0.5
set border 31 lw 0.75
set style data lines
set clip two

set size ratio -1

set xlabel 'X position (km)'
set ylabel offset 1.5 'Y position (km)'

set xrange [ -100 : 100 ]
set yrange [ -8 : 100 ]

set xtics 20

#set key at 5.85,0.7e-1 reverse Left spacing 1 height 0.6 width -4 samplen 4.6 opaque
set key at 0,-53 center maxrows 2 reverse Left spacing 1.2 height 0.6 width -2 samplen 2.5

set output 'map_colour.eps'

f(x, y, z) = x==y?z:-1000

set pointsize 1.5

plot 'waypoints.dat' using ($2/1000):($3/1000) title 'Way points' with linespoints pt 2, \
     'threats.dat' using (f($2,1,$3/1000)):(f($2,1,$4/1000)) title 'Type 1' with points ls 2 pt 5, \
     'threats.dat' using (f($2,2,$3/1000)):(f($2,2,$4/1000)) title 'Type 2' with points ls 3 pt 7, \
     'threats.dat' using (f($2,3,$3/1000)):(f($2,3,$4/1000)) title 'Type 3' with points ls 4 pt 9, \
     'threats.dat' using (f($2,4,$3/1000)):(f($2,4,$4/1000)) title 'Type 4' with points ls 5 pt 11, \
     'threats.dat' using (f($2,5,$3/1000)):(f($2,5,$4/1000)) title 'Type 5' with points ls 6 pt 13, \
     'waypoints.dat' using (($1==1)?($2/1000-8):(($1==4)?($2/1000+8):($2/1000))):((($1==2)||($1==3))?($3/1000+8):($3/1000)):(sprintf('%d', int($1))) \
       notitle with labels tc lt 1, \
     'threats.dat' using (f($2,1,$3/1000)):(($4/1000>=90)?($4/1000-8):($4/1000+8)):(sprintf('%d', int($1))) \
       notitle with labels tc ls 2, \
     'threats.dat' using (f($2,2,$3/1000)):(($4/1000>=90)?($4/1000-8):($4/1000+8)):(sprintf('%d', int($1))) \
       notitle with labels tc ls 3, \
     'threats.dat' using (f($2,3,$3/1000)):(($4/1000>=90)?($4/1000-8):($4/1000+8)):(sprintf('%d', int($1))) \
       notitle with labels tc ls 4, \
     'threats.dat' using (f($2,4,$3/1000)):(($4/1000>=90)?($4/1000-8):($4/1000+8)):(sprintf('%d', int($1))) \
       notitle with labels tc ls 5, \
     'threats.dat' using (f($2,5,$3/1000)):(($4/1000>=90)?($4/1000-8):($4/1000+8)):(sprintf('%d', int($1))) \
       notitle with labels tc ls 6 #offset 0,char 0.8


