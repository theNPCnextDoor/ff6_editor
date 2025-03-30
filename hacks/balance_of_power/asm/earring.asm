m=8,x=8

start=C2/0D4A
  CLC
  PEA #$0000
  BRA #$07
  LDA $EA
  LSR
  PHA
  LDA $E8
  ROR
  ADC $E8
  STA $E8
  PLA
  ADC $EA
  STA $EA
  RTS

  BIT #$02
  BCS #$04
  BNE #$0A
  XBA
  LSR
  LSR
  LDA $E8
  BCC #$09
  LSR
  BRA #$02
  LDA $E8
  LSR
  JSR $4A0D
  LDA $EA
  BEQ #$04
  TDC
  DEC
  BRA #$02
  LDA $E8
  STA $B011
  PLP
  RTS