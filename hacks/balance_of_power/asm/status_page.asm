m=8,x=16

reset_function=C2/0006

init_status_menu_pointer=C3/01F1
  ptr init_status_menu

draw_window=C3/0341

draw_3_digits=C3/0486

draw_8_digits=C3/04A3

draw_2_digits=C3/04B6

draw_3_digits_8_bits=C3/04C0

convert_8_bit_number_into_text_blank_leading_zeros=C3/04E0

convert_16_bit_number_into_text_blank_leading_zeros=C3/052E

convert_24_bit_number_into_text_blank_leading_zeros=C3/0582

load_pointer_to_animation_table_for_portrait=C3/0ACC

set_portrait_x_position_based_on_row=C3/0AF1

draw_lv_hp_and_mp=C3/0C6C
  STX $EF
  LDA #$C3
  STA $F1
  LDX $67
  LDA $0800,X
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  REP #$20
  LDA [$EF]
  TAX
  SEP #$20
  JSR draw_2_digits
  LDX $67
  LDA $0B00,X
  STA $F3
  LDA $0C00,X
  STA $F4
  JSR determine_max_hp_or_mp_with_gear_bonus
  JSR enforce_hp_cap
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDY #$0400
  JSR draw_current_or_max_hp_or_mp
  LDY $67
  JSR prevent_hp_excess
  LDA $0900,Y
  STA $F3
  LDA $0A00,Y
  STA $F4
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDY #$0200
  JSR draw_current_or_max_hp_or_mp
  JSR determine_if_actor_is_magic_user
  BCC hide_mp
  LDX $67
  LDA $0F00,X
  STA $F3
  LDA $1000,X
  STA $F4
  JSR determine_max_hp_or_mp_with_gear_bonus
  JSR enforce_mp_cap
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDY #$0800
  JSR draw_current_or_max_hp_or_mp
  LDY $67
  JSR prevent_mp_excess
  LDA $0D00,Y
  STA $F3
  LDA $0E00,Y
  STA $F4
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDY #$0600
  JMP draw_current_or_max_hp_or_mp

hide_mp=C3/0CEF

draw_current_or_max_hp_or_mp=C3/0D21

determine_if_actor_is_magic_user=C3/0D2B

determine_max_hp_or_mp_with_gear_bonus=C3/0D65

enforce_hp_cap=C3/0D92

enforce_mp_cap=C3/0D9F

process_animation_queue=C3/11B0

init_m7=C3/1206

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

prevent_hp_excess=C3/2B9A

prevent_mp_excess=C3/2BBC

draw_actor_name=C3/34CF
  JSR draw_string
  LDX #$0600
draw_actor_name_loop_start
  LDA $0200,Y
  STA $8021
  INY
  DEX
  BNE draw_actor_name_loop_start
  STZ $8021
  JMP draw_memorized_string

draw_actor_class=C3/34E5

draw_equipped_esper=C3/34E6
  JSR prepare_name_drawing
  LDA $1E00,Y
  CMP #$FF
  BEQ blank_esper_name
  ASL
  ASL
  ASL
  TAX
  LDY #$0800
draw_equipped_esper_loop_start
  LDA $E1F6E6,X
  STA $8021
  INX
  DEY
  BNE draw_equipped_esper_loop_start
  STZ $8021
  JMP draw_memorized_string
blank_esper_name
  LDY #$0800
  LDA #$FF
blank_esper_name_loop_start
  STA $8021
  DEY
  BNE blank_esper_name_loop_start
  STZ $8021
  JMP draw_memorized_string
prepare_name_drawing=C3/3519


draw_string=C3/3519
  LDX #$899E
  STX $8121
  REP #$20
  TYA
  SEP #$20
  STA $8021
  XBA
  STA $8021
  TDC
  LDY $67
  RTS

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
  JSR clear_bg1_tilemap_a
  JSR clear_bg1_tilemap_d
  JSR clear_bg3_tilemap_a
  JSR clear_bg3_tilemap_b
  JSR clear_bg3_tilemap_c
  JSR clear_bg3_tilemap_d
  LDY #$815F
  JSR draw_window
  LDY #$795F
  JSR draw_window
  LDY #$7D5F
  JSR draw_window
  RTS
draw_blue_text_and_symbols
  JSR draw_lv_hp_mp_and_non_blue_symbols
  BRA draw_other_blue_text
draw_lv_hp_mp_and_non_blue_symbols
  LDA #$20
  STA $29
  LDX #$5564
  LDY #$0800
  JSR draw_multiple_strings
  LDA #$24
  STA $29
  LDX #$4B64
  LDY #$0A00
  JSR draw_multiple_strings
  RTS
draw_other_blue_text
  LDA #$2C
  STA $29
  LDX #$3764
  LDY #$1400
  JSR draw_multiple_strings
  RTS

upload_tilemap=C3/5D77

# jump_to_replace_portrait=C3/5D89
#   JSR replace_portrait

draw_gogo_commands=C3/5DC1

draw_command_name=C3/5EE1

window_layout=C3/5F79
  $B758 | $0601
  $2F5A | $0906
  $8B58 | $1C18
  $C758 | $0012
  $8760 | $0712
draw_actor_info

draw_actor_values=C3/5FC2
  JSL reset_function
  LDY $67
  JSR define_bat_pwr_mode
  LDA #$20
  STA $29
  LDA $A611
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$5D7C
  JSR draw_3_digits_8_bits
  LDA $A411
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$DD7C
  JSR draw_3_digits_8_bits
  LDA $A211
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$5D7D
  JSR draw_3_digits_8_bits
  LDA $A011
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$DD7D
  JSR draw_3_digits_8_bits
  JSR define_current_or_projected_bat_pwr
  LDA $AC11
  CLC
  ADC $AD11
  STA $F3
  TDC
  ADC #$00
  STA $F4
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDX #$5D7E
  JSR draw_3_digits
  LDA $BA11
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$DD7E
  JSR draw_3_digits_8_bits
  LDA $A811
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$5D7F
  JSR draw_3_digits_8_bits
  LDA $BB11
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$DD7F
  JSR draw_3_digits_8_bits
  LDA $AA11
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$5D88
  JSR draw_3_digits_8_bits
  LDY #$CD38
  JSR draw_actor_name
  LDY #$9D39
  JSR draw_actor_class
  JSR draw_esper_and_equipment
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
  LDX #$B539
  JSR draw_8_digits
  JSR calculate_xp_needed_for_level_up
  JSR convert_24_bit_number_into_text_blank_leading_zeros
  LDX #$A339
  JSR draw_8_digits
  STZ $47
  JSR process_animation_queue
  JMP draw_status_effects
lv_hp_mp_quantity_position=C3/6096
  $E738
  $2339
  $2D39
  $6339
  $6D39
calculate_xp_needed_for_level_up

draw_actor_commands=C3/6102
  LDY #$F57A
  JSR draw_string
  JSR draw_command_name
  LDY #$757B
  JSR draw_string
  INY
  JSR draw_command_name
  LDY #$F57B
  JSR draw_string
  INY
  INY
  JSR draw_command_name
  LDY #$757C
  JSR draw_string
  INY
  INY
  INY
  JMP draw_command_name

create_portrait_a=C3/61DA

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

draw_status_effects=C3/625B
  LDY #$1D3A
  LDX #$5030

text_pointers=C3/6437
  ptr text_status
  ptr text_vigor
  ptr text_speed
  ptr text_stamina
  ptr text_mag_pwr
  ptr text_bat_pwr
  ptr text_defense
  ptr text_evade
  ptr text_mag_def
  ptr text_mblock

  ptr text_lv
  ptr text_hp
  ptr text_mp
  ptr text_your_exp
  ptr text_for_level_up
  ptr text_hp_slash
  ptr text_mp_slash
  ptr text_evade_percentage
  ptr text_mblock_percentage
text_status
  $F978 | "Status",$00
text_hp_slash
  $2B39 | "/",$00
text_mp_slash
  $6B39 | "/",$00
text_evade_percentage
  $637F | "%",$00
text_mblock_percentage
  $6388 | "%",$00
text_lv
  $DD38 | "LV",$00
text_hp
  $1D39 | "HP",$00
text_mp
  $5D39 | "MP",$00
text_your_exp
  $9D39 | "XP",$00
text_for_level_up
  $B339 | "→",$00
text_vigor
  $4D7C | "Vigor  ¨",$00
text_speed
  $CD7C | "Speed  ¨",$00
text_stamina
  $4D7D | "Stamina¨",$00
text_mag_pwr
  $CD7D | "Mag.Pwr¨",$00
text_bat_pwr
  $4D7E | "Bat.Pwr¨",$00
text_defense
  $CD7E | "Defense¨",$00
text_evade
  $4D7F | "Evade %¨",$00
text_mag_def
  $CD7F | "Mag.Def¨",$00
text_mblock
  $4D88 | "MBlock%¨",$00

draw_multiple_strings=C3/69BA

clear_bg1_tilemap_a=C3/6A15

clear_bg1_tilemap_d=C3/6A23

clear_bg3_tilemap_a=C3/6A3C

clear_bg3_tilemap_b=C3/6A41

clear_bg3_tilemap_c=C3/6A46

clear_bg3_tilemap_d=C3/6A4B

draw_memorized_string=C3/7FD9

define_current_or_projected_bat_pwr=C3/9371

define_bat_pwr_mode=C3/99E8

create_portrait=C3/F0A0
  JSR create_portrait_a
  PHB
  LDA #$7E
  PHA
  PLB
  TDC
  LDA $28
  TAY
  JSR set_portrait_x_position_based_on_row
  TDC
  LDA $28
  TAY
  JSR init_vars_for_portrait
  PLB
  RTS
init_vars_for_portrait
  JSR load_pointer_to_animation_table_for_portrait
  REP #$20
  LDA #$1800 # Y position of actor portrait
  STA $4A34,X
  SEP #$20
  JMP init_m7
replace_portrait
  TDC
  LDA $60
  TAX
  LDA #$FF
  STA $C9357E,X
  JSR create_portrait_a
  JMP create_portrait

draw_equipped_weapon
  CMP #$FF
  BEQ blank_equipped_weapon
  STA $0242
  LDA #$0D
  STA $0342
  NOP
  NOP
  NOP
  LDX $1642
  LDY #$0D00
draw_equipped_weapon_loop_start
  LDA $00B3D2,X
  STA $8021
  INX
  DEY
  BNE draw_equipped_weapon_loop_start
  STZ $8021
  JMP draw_memorized_string
blank_equipped_weapon
  LDY #$0D00
  LDA #$FF
blank_equipped_weapon_loop_start
  STA $8021
  DEY
  BNE blank_equipped_weapon_loop_start
  STZ $8021
  JMP draw_memorized_string

draw_esper_and_equipment
  LDY #$6D7D
  JSR draw_equipped_esper

  LDY #$EB7D
  JSR prepare_name_drawing
  LDA $1F00,Y
  JSR draw_equipped_weapon

  LDY #$6B7E
  JSR prepare_name_drawing
  LDA $2000,Y
  JSR draw_equipped_weapon

  LDY #$EB7E
  JSR prepare_name_drawing
  LDA $2100,Y
  JSR draw_equipped_weapon

  LDY #$6B7F
  JSR prepare_name_drawing
  LDA $2200,Y
  JSR draw_equipped_weapon

  LDY #$EB7F
  JSR prepare_name_drawing
  LDA $2300,Y
  JSR draw_equipped_weapon

  LDY #$6B88
  JSR prepare_name_drawing
  LDA $2400,Y
  JSR draw_equipped_weapon

  JMP draw_actor_commands