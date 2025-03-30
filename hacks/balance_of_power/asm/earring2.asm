m=16,x=16

start=C2/0D4A
  CLC
  PEA #$0000
  BRA label_c20d57
  LDA $EA
  LSR
  PHA
  LDA $E8
  ROR
label_c20d57
  ADC $E8
  STA $E8
  PLA
  ADC $EA
  STA $EA
  RTS
  BIT #$02
  BCS label_c20d69
  BNE label_c20d71
  XBA
  LSR
label_c20d69
  LSR
  LDA $E8
  BCC label_c20d77
  LSR
  BRA label_c20d73
label_c20d71
  LDA $E8
label_c20d73
  LSR
  JSR start
label_c20d77
  LDA $EA
  BEQ label_c20d7f
  TDC
  DEC
  BRA label_c20d81
label_c20d7f
  LDA $E8
label_c20d81
  STA $B011
  PLP
  RTS