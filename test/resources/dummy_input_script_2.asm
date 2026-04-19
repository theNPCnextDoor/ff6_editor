m=8,x=16

db alfa = $12
dw bravo = $1234
db delta = $00

@archie = $C00005
  TAX ; some comment
  LDA (alfa,X)
  LDX #$FEDC
  REP #$30
  LDA #bravo
  LDX #$FEDC
  SEP #$30
  LDA #$BB
  LDX #$CC
  MVP #$34,#alfa

  JMP !archie
  BRA start ; some other comment

  bravo
  $5678,$FF
  $ABCD,delta
  "<0x00>A<KNIFE> ",$88
  $AA | "a" | $BB,$FF | "b",$00

  desc "Bob<LINE><FIRE>",$00

#anchor_1
  rptr !rptr_1
  rptr !rptr_2

#$D20002
  rptr !rptr_2

@anchor_1 = $D20001
@rptr_1 = $D23456
@rptr_2 = $D23457