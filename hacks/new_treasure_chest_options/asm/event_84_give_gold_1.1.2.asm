m=true,x=false
start=C0/D617

  LDX $EB
  STX $22
  JSR $D61F
  LDA #$03
  JMP $9B5C
beginning
  REP #$21
  LDA $1860
  ADC $22
  STA $1860
  TDC
  SEP #$20
  ADC $1862
  STA $1862
  CMP #$98
  BCC finish
  LDX $1860
  CPX #$967F
  BCC finish
  LDX #$967F
  STX $1860
  LDA #$98
  STA $1862
finish
  RTS

