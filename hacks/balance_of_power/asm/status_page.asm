m=8,x=16

label_c20006=C2/0006

label_c301f1=C3/01F1
  ptr label_c31c46

label_c30341=C3/0341

label_c30486=C3/0486

label_c304a3=C3/04A3

label_c304c0=C3/04C0

label_c304e0=C3/04E0

label_c3052e=C3/052E

label_c30582=C3/0582

label_c30c6c=C3/0C6C

label_c311b0=C3/11B0

label_c31c46=C3/1C46
  JSR label_c3352f
  JSR label_c3620b
  JSR label_c35d05
  JSR label_c31c5d
  LDA #$01
  STA $26
  LDA #$0C
  STA $27
  JMP label_c33541
label_c31c5d

label_c334cf=C3/34CF

label_c334e5=C3/34E5

label_c334e6=C3/34E6

label_c3352f=C3/352F

label_c33541=C3/3541

label_c35d05=C3/5D05
  JSR label_c35d17
  JSR label_c35dc1
  JSR label_c35d3c
  JSR label_c35f8d
  JSR label_c35d77
  JMP label_c361ac
label_c35d17
  JSR label_c36a15
  JSR label_c36a23
  JSR label_c36a3c
  JSR label_c36a41
  JSR label_c36a46
  JSR label_c36a4b
  LDY #$815F
  JSR label_c30341
  LDY #$795F
  JSR label_c30341
  LDY #$7D5F
  JSR label_c30341
  RTS
label_c35d3c
  JSR label_c35d41
  BRA label_c35d5c
label_c35d41
  LDA #$20
  STA $29
  LDX #$5B64
  LDY #$0800
  JSR label_c369ba
  LDA #$24
  STA $29
  LDX #$5564
  LDY #$0600
  JSR label_c369ba
  RTS
label_c35d5c
  LDA #$2C
  STA $29
  LDX #$3764
  LDY #$1E00
  JSR label_c369ba
  LDA #$2C
  STA $29
  LDX #$6364
  LDY #$0C00
  JSR label_c369ba
  RTS
label_c35d77

label_c35dc1=C3/5DC1

label_c35f79=C3/5F79
  $8B58 | $0601
  $EB5A | $0906
  $8B58 | $1C18
  $C758 | $0012
  $8760 | $0712
label_c35f8d

label_c35fc2=C3/5FC2
  JSL label_c20006
  LDY $67
  JSR label_c399e8
  LDA #$20
  STA $29
  LDA $A611
  JSR label_c304e0
  LDX #$E17E
  JSR label_c304c0
  LDA $A411
  JSR label_c304e0
  LDX #$617F
  JSR label_c304c0
  LDA $A211
  JSR label_c304e0
  LDX #$E17F
  JSR label_c304c0
  LDA $A011
  JSR label_c304e0
  LDX #$6188
  JSR label_c304c0
  JSR label_c39371
  LDA $AC11
  CLC
  ADC $AD11
  STA $F3
  TDC
  ADC #$00
  STA $F4
  JSR label_c3052e
  LDX #$7D7E
  JSR label_c30486
  LDA $BA11
  JSR label_c304e0
  LDX #$FD7E
  JSR label_c304c0
  LDA $A811
  JSR label_c304e0
  LDX #$7D7F
  JSR label_c304c0
  LDA $BB11
  JSR label_c304e0
  LDX #$FD7F
  JSR label_c304c0
  LDA $AA11
  JSR label_c304e0
  LDX #$7D88
  JSR label_c304c0
  LDY #$8F39
  JSR label_c334cf
  LDY #$9D39
  JSR label_c334e5
  LDY #$B139
  JSR label_c334e6
  JSR label_c36102
  LDA #$20
  STA $29
  LDX #$9660
  JSR label_c30c6c
  LDX $67
  LDA $1100,X
  STA $F1
  LDA $1200,X
  STA $F2
  LDA $1300,X
  STA $F3
  JSR label_c30582
  LDX #$D77C
  JSR label_c304a3
  JSR label_c360a0
  JSR label_c30582
  LDX #$D77D
  JSR label_c304a3
  STZ $47
  JSR label_c311b0
  JMP label_c3625b
  $273A
  $633A
  $6D3A
  $A33A
  $AD3A
label_c360a0

label_c36102=C3/6102

label_c361ac=C3/61AC

label_c3620b=C3/620B
  LDA #$02
  STA $5043
  LDA #$12
  STA $5143
  LDY #$2A62
  STY $5243
  LDA #$C3
  STA $5443
  LDA #$C3
  STA $5743
  LDA #$20
  TSB $43
  RTS
  $27 | $00 | $00
  $0C | $04 | $00
  $0C | $08 | $00
  $0C | $0C | $00
  $0C | $10 | $00
  $0C | $14 | $00
  $0C | $18 | $00
  $0C | $1C | $00
  $0C | $20 | $00
  $0C | $24 | $00
  $0C | $28 | $00
  $0C | $2C | $00
  $0C | $30 | $00
  $0C | $34 | $00
  $0C | $38 | $00
  $0C | $3C | $00
  $00 | $A0 | $9D

label_c3625b=C3/625B

label_c36437=C3/6437
  ptr label_c36497
  ptr label_c3649f
  ptr label_c364a9
  ptr label_c364b3
  ptr label_c364bd
  ptr label_c364c7
  ptr label_c364cb
  ptr label_c364cf
  ptr label_c364d3
  ptr label_c364d7
  ptr label_c364db
  ptr label_c364df
  ptr label_c364e3
  ptr label_c364e7
  ptr label_c3646f
  ptr label_c36488
  ptr label_c3648d
  ptr label_c36492
  ptr label_c36478
  ptr label_c3647c
  ptr label_c36480
  ptr label_c36484
  ptr label_c364eb
  ptr label_c364f3
  ptr label_c364fd
  ptr label_c36507
  ptr label_c36511
  ptr label_c3651d
label_c3646f
  $CD78 | "Status",$00
label_c36478
  $6B3A | "/",$00
label_c3647c
  $AB3A | "/",$00
label_c36480
  $837F | "%",$00
label_c36484
  $8388 | "%",$00
label_c36488
  $1D3A | "LV",$00
label_c3648d
  $5D3A | "HP",$00
label_c36492
  $9D3A | "MP",$00
label_c36497
  $CF7E | "Vigor",$00
label_c3649f
  $CF7F | "Stamina",$00
label_c364a9
  $4F88 | "Mag.Pwr",$00
label_c364b3
  $697F | "Evade %",$00
label_c364bd
  $6988 | "MBlock%",$00
label_c364c7
  $DD7E | "¨",$00
label_c364cb
  $5D7F | "¨",$00
label_c364cf
  $DD7F | "¨",$00
label_c364d3
  $5D88 | "¨",$00
label_c364d7
  $FB7E | "¨",$00
label_c364db
  $7B7F | "¨",$00
label_c364df
  $7B7E | "¨",$00
label_c364e3
  $FB7F | "¨",$00
label_c364e7
  $7B88 | "¨",$00
label_c364eb
  $4F7F | "Speed",$00
label_c364f3
  $697E | "Bat.Pwr",$00
label_c364fd
  $E97E | "Defense",$00
label_c36507
  $E97F | "Mag.Def",$00
label_c36511
  $4D7C | "Your Exp:",$00
label_c3651d
  $4D7D | "For level up:",$00

label_c369ba=C3/69BA

label_c36a15=C3/6A15

label_c36a23=C3/6A23

label_c36a3c=C3/6A3C

label_c36a41=C3/6A41

label_c36a46=C3/6A46

label_c36a4b=C3/6A4B

label_c39371=C3/9371

label_c399e8=C3/99E8