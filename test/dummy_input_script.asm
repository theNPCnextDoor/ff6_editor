m=8,x=16

start=C00001
  ptr $1234
  ptr $0005

archie=C00005
  TAX ; some comment
  LDA ($12,X)
  LDX #$FEDC
  REP #$30
  LDA #$3456
  LDX #$FEDC
  SEP #$30
  LDA #$BB
  LDX #$CC
  MVP #$34,#$12

  JMP archie
  BRA start ; some other comment

  $1234
  $5678,$FF
  $ABCD,$00
  "<0x00>A<KNIFE> ",$88
  $AA | "a" | $BB,$FF | "b",$00

; some final comment