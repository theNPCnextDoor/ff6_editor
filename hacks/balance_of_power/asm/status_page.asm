m=8,x=16

reset_function=C2/0006

init_status_menu_pointer=C3/01F1
  ptr init_status_menu

draw_window=C3/0341

draw_3_digits=C3/0486

draw_8_digits=C3/04A3

draw_3_digits_8_bits=C3/04C0

convert_8_bit_number_into_text_blank_leading_zeros=C3/04E0

convert_16_bit_number_into_text_blank_leading_zeros=C3/052E

convert_24_bit_number_into_text_blank_leading_zeros=C3/0582

draw_lv_hp_and_mp=C3/0C6C # To be disassembled

process_animation_queue=C3/11B0

init_status_menu=C3/1C46
  JSR reset_oam_and_anim_queue
  JSR condense_bg3_text
  JSR draw_status_menu
  JSR initialize_cursor_data
  LDA #$01
  STA $26
  LDA #$0C
  STA $27
  JMP prepare_fade_in
initialize_cursor_data

draw_actor_name=C3/34CF

draw_actor_class=C3/34E5

draw_equipped_esper=C3/34E6

reset_oam_and_anim_queue=C3/352F

prepare_fade_in=C3/3541

draw_status_menu=C3/5D05
  JSR draw_windows
  JSR draw_gogo_commands
  JSR draw_blue_text_and_symbols
  JSR draw_actor_info
  JSR upload_tilemap
  JMP create_portrait
draw_windows
  JSR label_c36a15
  JSR label_c36a23
  JSR label_c36a3c
  JSR label_c36a41
  JSR label_c36a46
  JSR label_c36a4b
  LDY #$815F
  JSR draw_window
  LDY #$795F
  JSR draw_window
  LDY #$7D5F
  JSR draw_window
  RTS
draw_blue_text_and_symbols
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
upload_tilemap

draw_gogo_commands=C3/5DC1

label_c35f79=C3/5F79
  $8B58 | $0601
  $EB5A | $0906
  $8B58 | $1C18
  $C758 | $0012
  $8760 | $0712
draw_actor_info

label_c35fc2=C3/5FC2
  JSL reset_function
  LDY $67
  JSR label_c399e8
  LDA #$20
  STA $29
  LDA $A611
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$E17E
  JSR draw_3_digits_8_bits
  LDA $A411
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$617F
  JSR draw_3_digits_8_bits
  LDA $A211
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$E17F
  JSR draw_3_digits_8_bits
  LDA $A011
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$6188
  JSR draw_3_digits_8_bits
  JSR label_c39371
  LDA $AC11
  CLC
  ADC $AD11
  STA $F3
  TDC
  ADC #$00
  STA $F4
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDX #$7D7E
  JSR draw_3_digits
  LDA $BA11
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$FD7E
  JSR draw_3_digits_8_bits
  LDA $A811
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7D7F
  JSR draw_3_digits_8_bits
  LDA $BB11
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$FD7F
  JSR draw_3_digits_8_bits
  LDA $AA11
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7D88
  JSR draw_3_digits_8_bits
  LDY #$8F39
  JSR draw_actor_name
  LDY #$9D39
  JSR draw_actor_class
  LDY #$B139
  JSR draw_equipped_esper
  JSR label_c36102
  LDA #$20
  STA $29
  LDX #$9660
  JSR draw_lv_hp_and_mp
  LDX $67
  LDA $1100,X
  STA $F1
  LDA $1200,X
  STA $F2
  LDA $1300,X
  STA $F3
  JSR convert_24_bit_number_into_text_blank_leading_zeros
  LDX #$D77C
  JSR draw_8_digits
  JSR label_c360a0
  JSR convert_24_bit_number_into_text_blank_leading_zeros
  LDX #$D77D
  JSR draw_8_digits
  STZ $47
  JSR process_animation_queue
  JMP label_c3625b
  $273A
  $633A
  $6D3A
  $A33A
  $AD3A
label_c360a0

label_c36102=C3/6102

create_portrait=C3/61AC

condense_bg3_text=C3/620B
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