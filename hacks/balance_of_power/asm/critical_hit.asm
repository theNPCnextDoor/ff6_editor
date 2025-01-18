m=true,x=true

start=C2/340C
  JSR $FAA4
  LDA #$20
  TSB $A0
  NOP

end=C2/3414

crit_mult=C2/FAA4
  INC $BC               ; Each increase of $BC result in 50% more damage.
  INC $BC
  LDA $3ED8,X
  CMP #$03              ; If attacker isn't Shadow, exit.
  BNE crit_mult_exit
  LDA $BC
  ADC #$04
  STA $BC

crit_mult_exit
  RTS