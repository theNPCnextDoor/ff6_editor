m=true,x=false

start=C0/840F
  CMP #$1B
  BNE is_rare_item_name
  JSR $D6A3
  BRA jumping
is_rare_item_name
  CMP #$1C
  BNE label_844B
  JSR $D6DD
jumping
  JMP $8263

label_844B=C0/844B

character_1B=C0/D6A3
  LDA $0584
  CMP #$54
  STA $4202
  LDA #$08
  STA $4203
  NOP
  NOP
  NOP
  LDX $4216
  LDY $00
  LDA #$7E
  PHA
  PLB

label_842A
  LDA $E6F6E1,X
  SEC
  SBC #$60
  STA $9183,Y
  CMP #$9F
  BEQ label_843F
  INX
  INY
  CPY #$0008
  BNE label_842A

label_843F
  TDC           
  STA $9183,Y   
  TDC           
  PHA           
  PLB           
  STZ $CF
  RTS
  JMP $8263     

character_1C=C0/D6DD
  LDA $0584
  CMP #$54
  STA $4202
  LDA #$0D
  STA $4203
  NOP
  NOP
  NOP
  LDX $4216
  LDY $00
  LDA #$7E
  PHA
  PLB

label_842A_2
  LDA $CEFBA0,X
  SEC
  SBC #$60
  STA $9183,Y
  CMP #$9F
  BEQ label_843F_2
  INX
  INY
  CPY #$000D
  BNE label_842A_2

label_843F_2
  TDC
  STA $9183,Y
  TDC
  PHA
  PLB
  STZ $CF
  RTS


