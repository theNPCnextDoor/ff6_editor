m=8,x=16

start=C0/0001
  ptr $3412
  ptr $0500

archie=C0/0005
  TAX
  LDA ($12,X)
  LDX #$DCFE
  REP #$30
  LDA #$5634
  LDX #$DCFE
  SEP #$30
  LDA #$BB
  LDX #$CC
  MVP #$12,#$34

  JMP archie
  BRA start

  $1234
  $5678,$FF
  $ABCD,$00
  "<0x00>A<KNIFE> ",$88
  $AA | "a" | $BB,$FF | "b",$00