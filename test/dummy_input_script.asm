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

  blob $1234
  blob $5678 $FF
  blob $ABCD $00
  "<0x00>A<KNIFE> "