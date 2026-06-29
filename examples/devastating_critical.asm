; This hack changes the calculation of critical hit damage so that
; when Shadow makes one, he deals 300% damage instead of the usual
; 200%.

map: HiROM

let shadow_id = $03
let damage_mult = $BC ; Each increase of $BC result in 50% more damage.
let attacker = $3ED8

@start = $C2340C
m = 8, x = 8
  JSR !crit_mult_subroutine
  LDA #$20
  TSB $A0
  NOP

@crit_mult_subroutine = $C2FAA4
  INC damage_mult
  INC damage_mult
  LDA attacker,X
  CMP #shadow_id
  BNE crit_mult_subroutine_exit          ; If attacker isn't Shadow, exit.
  INC damage_mult
  INC damage_mult
@crit_mult_subroutine_exit
  RTS