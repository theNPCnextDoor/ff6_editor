m=true,x=false
start=C0/D800

  LDA $EB
  JSR $D80A
  LDA #$02
  JMP $9B5C

  CMP #$08
  BNE not_coral
  LDX $1FD0
  INX
  BVC storing_coral_value
  LDX #$FFFF
storing_coral_value
  STX $16F0
not_coral
  STA $1A
  AND #$07
  TAX
  LDA $1A
  LSR
  LSR
  LSR
  TAY
  LDA $1EBA,Y
  ORA $C0BAFC,X
  STA $1EBA,Y
  RTS