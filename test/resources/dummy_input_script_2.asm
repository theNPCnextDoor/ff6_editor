db alfa = $12
dw bravo = $1234
db delta = $00

@archie = $C00005
m = 8, x = 16
  TAX ; some comment
  LDA (alfa,X)
  LDX #$FEDC
  REP #$30
  LDA #bravo
  LDX #$FEDC
  SEP #$30
  LDA #.label_c0fedc
  LDX #$CC
  MVP #$34,#alfa

  JMP !archie
  BRA start ; some other comment

  bravo
  $5678,$FF
  $ABCD,delta
  "<0x00>A<KNIFE>_",$88
  $AA | "a" | $BB,$FF | "b",$00

  desc "Bob<LINE><FIRE>",$00

#anchor_1
  rptr !rptr_1
  rptr !rptr_2

#$D20002
  rptr !rptr_2
m = 8, x = 8 ; Unnecessary flags redifinition here.
  JSR !archie

@label_c0fedc = $C0FEDC
@anchor_1 = $D20001
@rptr_1 = $D23456
@rptr_2 = $D23457
m = 16, x = 16
  JSL archie