m=8,x=16

start=C3/04E0
  JSR $F904
  LDY $00
  LDX #$0200
label_c304e8
  LDA $F700,Y
  CMP #$B4
  BNE label_c304f8
  LDA #$FF
  STA $F700,Y
  INY
  DEX
  BNE label_c304e8
label_c304f8
  RTS
label_c304f9