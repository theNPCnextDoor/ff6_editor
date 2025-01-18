m=8,x=16

label_c20006=C2/0006

label_c302f9=C3/02F9

label_c302ff=C3/02FF

label_c30486=C3/0486

label_c304a3=C3/04A3

label_c304c0=C3/04C0

label_c304e0=C3/04E0

label_c3052e=C3/052E

label_c30582=C3/0582

label_c30acc=C3/0ACC

label_c30c6c=C3/0C6C

label_c311b0=C3/11B0

label_c31206=C3/1206

label_c33427=C3/3427

label_c334cf=C3/34CF

label_c334e5=C3/34E5

label_c334e6=C3/34E6

label_c33519=C3/3519

prepare_lv_blue_text=C3/5D41
  LDA #$20
  STA $29
  LDX #$5B64
  LDY #$0600
  JSR draw_multiple_strings
  LDA #$24
  STA $29
  LDX #$5564
  LDY #$0A00
  JSR draw_multiple_strings
  RTS

start=C3/5D5C
  LDA #$2C
  STA $29
  LDX #$3764
  LDY #$1200
  JSR draw_multiple_strings
  RTS

label_c35ee1=C3/5EE1

label_c35f79=C3/5F79
  $B758 | $0601
  $2F5A | $0906
  $8B58 | $1C18
  $C758 | $0012
  $8760 | $0712

label_c35fbb=C3/5FBB
  LDX $73
  STX $67
  TDC
  LDA $6C
  JSL label_c20006
  LDY $67
  JSR label_c399e8
  LDA #$20
  STA $29
  LDA $A611
  JSR label_c304e0
  LDX #$5D7C
  JSR label_c304c0
  LDA $A411
  JSR label_c304e0
  LDX #$DD7C
  JSR label_c304c0
  LDA $A211
  JSR label_c304e0
  LDX #$5D7D
  JSR label_c304c0
  LDA $A011
  JSR label_c304e0
  LDX #$DD7D
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
  LDX #$5D7E
  JSR label_c30486
  LDA $BA11
  JSR label_c304e0
  LDX #$DD7E
  JSR label_c304c0
  LDA $A811
  JSR label_c304e0
  LDX #$5D7F
  JSR label_c304c0
  LDA $BB11
  JSR label_c304e0
  LDX #$DD7F
  JSR label_c304c0
  LDA $AA11
  JSR label_c304e0
  LDX #$5D88
  JSR label_c304c0
  LDY #$CD38
  JSR label_c334cf
  LDY #$9D39
  JSR label_c334e5
  LDY #$AD3C
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
  LDX #$F579
  JSR label_c304a3
  JSR label_c360a0
  JSR label_c30582
  LDX #$E179
  JSR label_c304a3
  STZ $47
  JSR label_c311b0
  JMP label_c3625b
  $E738
  $2339
  $2D39
  $6339
  $6D39
label_c360a0

label_c36102=C3/6102
label_c36102
  LDY #$F57A
  JSR label_c33519
  JSR label_c35ee1
  LDY #$757B
  JSR label_c33519
  INY
  JSR label_c35ee1
  LDY #$F57B
  JSR label_c33519
  INY
  INY
  JSR label_c35ee1
  LDY #$757C
  JSR label_c33519
  INY
  INY
  INY
  JMP label_c35ee1

label_c361fb=C3/61FB
  JSR label_c30acc
  REP #$20
  LDA #$2000
  STA $4A34,X
  SEP #$20
  JMP label_c31206

label_c3625b=C3/625B
label_c3625b
  LDY #$5D3A
  LDX #$5038
  STX $E7
  JSR label_c33519
  LDA $1400,Y
  BMI label_c362e7
  AND #$70
  STA $E1
  LDA $1400,Y
  AND #$07
  ASL
  STA $E2
  LDA $1500,Y
  AND #$80
  ORA $E1
  ORA $E2
  STA $E1
  BEQ label_c362e1
  STZ $F1
  STZ $F2
  LDX #$0700

label_c362e1=C3/62E1

label_c362e7=C3/62E7

pointers_to_blue_text=C3/6437
  ptr label_c3646f
  ptr label_c36478
  ptr label_c3647c
  ptr label_c36480
  ptr label_c36484

  ptr blue_text_lv
  ptr blue_text_hp
  ptr blue_text_mp
  ptr blue_text_xp
  ptr blue_text_next_lv_in

  ptr label_c36497
  ptr label_c3649f
  ptr label_c364a9
  ptr label_c364b3
  ptr label_c364bd
  ptr label_c364eb
  ptr label_c364f3
  ptr label_c364fd
  ptr label_c36507



label_c3646f=C3/646F
  $F978 | "Status",$00
label_c36478
  $2B39 | "/",$00
label_c3647c
  $6B39 | "/",$00
label_c36480
  $637F | "%",$00
label_c36484
  $6388 | "%",$00
blue_text_lv
  $DD38 | "LV",$00
blue_text_hp
  $1D39 | "HP",$00
blue_text_mp
  $5D39 | "MP",$00
blue_text_xp
  $9D39 | "XP",$00
blue_text_next_lv_in
  $B339 | "→",$00
label_c36497
  $4D7C | "Vigor  ¨",$00
label_c3649f
  $4D7D | "Stamina¨",$00
label_c364a9
  $CD7D | "Mag.Pwr¨",$00
label_c364b3
  $4D7F | "Evade %¨",$00
label_c364bd
  $4D88 | "MBlock%¨",$00
label_c364eb
  $CD7C | "Speed  ¨",$00
label_c364f3
  $4D7E | "Bat.Pwr¨",$00
label_c364fd
  $CD7E | "Defense¨",$00
label_c36507
  $CD7F | "Mag.Def¨",$00

draw_multiple_strings=C3/69BA
  STX $F1
  STY $EF
  LDA #$C3
  STA $F3
  LDY $00
label_c369c4
  REP #$20
  LDA [$F1],Y
  STA $E7
  PHY
  SEP #$20
  LDA #$C3
  STA $E9
  JSR label_c302ff
  PLY
  INY
  INY
  CPY $EF
  BNE label_c369c4
  RTS

label_c37953=C3/7953
  JSR label_c379ac
  TDC
  LDA $4B
  CLC
  ADC $4A
  ADC $5A
  TAX
  LDA $899D7E,X
  BMI label_c379ab
  STA $C9
  ASL
  TAX
  REP #$20
  LDA $6969C3,X
  STA $67
  SEP #$20
  LDA #$24
  STA $29
  LDX #$C979
  LDY #$0A00
  JSR draw_multiple_strings
  LDY #$5B3A
  LDX #$4830
  LDA #$01
  STA $48
  JSR label_c33427
  LDY #$DB3A
  JSR label_c334cf
  LDY #$5B3B
  JSR label_c334e6
  LDY #$DE79
  JSR label_c302f9
  LDY #$E279
  JSR label_c302f9
  LDX #$E679
  JSR label_c30c6c
label_c379ab
  RTS
label_c379ac

label_c39371=C3/9371

label_c399e8=C3/99E8