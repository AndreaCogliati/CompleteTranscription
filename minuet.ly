\version "2.18.2"
\header { tagline = "" }
upper = { \clef treble {  } 
{ \time 3/4

  } 
 <<  { d' 2  b' 8  r 4  c'' 8  d'' 4  r 4  g' 4  r 2  g' 4  e'' 4  r 2.  c'' 8  d'' 8  e'' 8  fis'' 8  g'' 4  r 2.  g' 4  g' 4  c'' 4  r 2.  d'' 8  c'' 8  b' 8  a' 8  b' 4  r 2.  c'' 8  b' 8  a' 8  g' 8  fis' 4  r 2.  g' 8  a' 8  b' 8  g' 8  a' 2.  r 2.  d'' 4  r 2.  g' 8  a' 8  b' 8  c'' 8  d'' 4  r 2.  g' 4  g' 4  e'' 4   ~ e'' 16  r 2.  c'' 16  d'' 8  e'' 8  fis'' 8  g'' 4  r 2.  g' 4  g' 4  c'' 4  r 2.  d'' 8  c'' 8  b' 8  a' 8  b' 4  r 2.  c'' 8  b' 8  a' 8  g' 8  a' 4  r 2.  b' 8  a' 8  g' 8  fis' 8  g' 2  r 2.  b'' 4  r 2.  g'' 8  a'' 8  b'' 8  g'' 8  a'' 4  r 2.  d'' 8  e'' 8  fis'' 8  d'' 8  g'' 4  r 2.  e'' 8  fis'' 8  g'' 8  d'' 8  cis'' 4  r 2.  b' 8  cis'' 8  a' 4  a' 8  r 2.  b' 8  cis'' 8  d'' 8  e'' 8  fis'' 8  g'' 4  r 2.  fis'' 4  e'' 4  fis'' 4  r 2.  a' 4  cis'' 4  d'' 2.  r 2.  d'' 4  r 2.  g' 8  fis' 8  g' 4  e'' 4  r 2.  g' 8  fis' 8  g' 4  d'' 4  r 2.  c'' 4  b' 4  a' 8  r 2.  g' 8  fis' 8  g' 8  a' 4  d' 8  r 2.  e' 8  fis' 8  g' 8  a' 8  b' 8  c'' 4  r 2.  b' 4  a' 4  b' 8  r 2.  d'' 8  g' 4  fis' 4  g' 2.  ~  r 2.  g' 4  r 4  r 2   }  \\  { d'' 4  g' 8   a' 8   s 2  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  r 2.  d' 2  ~  r 2.  d' 4  e' 2  s 2.  s 2.  s 2.  s 2.  s 2.  d' 2.  ~  r 2.  d' 4  r 4  r 2   }  >> \bar "|."  }
lower = { \clef bass {  } 
{ \time 3/4

  } 
 <<  { g 2  a 4  b 2.  r 2.  c' 2.  r 2.  b 2.  r 2.  a 2.  r 2.  g 2.  r 2.  d' 4  r 2.  b 4  g 4  d' 4  r 2.  d 8  c' 8  b 8  a 8  b 2  r 2.  a 4  g 4  r 2.  b 4  g 4  c' 2.  r 2.  b 4  r 2.  c' 8  b 8  a 8  g 8  a 2  r 2.  fis 4  g 2  r 2.  b 4  c' 4  r 2.  d' 4  d 4  g 2.  r 2.  g 2.  r 2.  fis 2.  r 2.  e 4  r 2.  g 4  e 4  a 2.  r 2.  a 2.  r 2.  b 4  r 2.  d' 4  cis' 4  d' 4  r 2.  fis 4  a 4  d' 4  r 2.  d 4  c' 4  b 2  r 2.  b 4  c' 2  r 2.  c' 4  b 4  r 2.  a 4  g 4  d' 2.  r 2.  d 2.  r 2.  e 4  r 2.  g 4  fis 4  g 4  r 2.  b, 4  d 4  g 4  r 2.  d 4  g, 4  ~  r 4  g, 4  r 2   }  \\  { b 2  r 2  r 16  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  r 2.  g, 4  s 2.  s 2.  s 2.  r 2.  a, 4  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  s 2.  r 2.  fis 4  s 2.  s 2.  b 2.  ~  r 2.  b 8.  r 8.  r 2  r 16   }  >> \bar "|."  }
\score { \new PianoStaff
    <<
    % \set PianoStaff.instrumentName = #"Piano  "
    \new Staff = "upper" \upper
    \new Staff = "lower" \lower >> }