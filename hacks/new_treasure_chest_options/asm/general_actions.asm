m=true,x=false
start=C0/D617

gen_act_66
  LDA $EB
  JSR $D621
  LDA #$02
  JMP $9B5C
  CMP #$08
  BNE gen_act_66_not_coral
  LDX $1FD0
  INX
  BVC gen_act_66_storing_coral_value
  LDX #$FFFF
gen_act_66_storing_coral_value
  STX $1FD0
gen_act_66_not_coral
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

m=true,x=false

gen_act_84
  LDX $EB
  STX $22
  JSR $D653
  LDA #$03
  JMP $9B5C
gen_act_84_end_of_wrapper
  REP #$21
  LDA $1860
  ADC $22
  STA $1860
  TDC
  SEP #$20
  ADC $1862
  STA $1862
  CMP #$98
  BCC gen_act_84_finish
  LDX $1860
  CPX #$967F
  BCC gen_act_84_finish
  LDX #$967F
  STX $1860
  LDA #$98
  STA $1862
gen_act_84_finish
  RTS

m=true,x=false

gen_act_86
  LDA $EB
  STA $1A
  SEC
  SBC #$36
  JSR $D68D
  LDA #$02
  JMP $9B5C
  STA $1A
  AND #$07
  TAX
  LDA $1A
  LSR
  LSR
  LSR
  TAY
  LDA $1A69,Y
  ORA $C0BAFC,X
  STA $1A69,Y
  RTS
