m=8,x=16

reset_function=C20006

draw_3_digits=C30486

draw_8_digits=C304A3

draw_3_digits_8_bits=C304C0

convert_8_bit_number_into_text_blank_leading_zeros=C304E0

convert_16_bit_number_into_text_blank_leading_zeros=C3052E

convert_24_bit_number_into_text_blank_leading_zeros=C30582


draw_lv_hp_and_mp=C30C6C

process_animation_queue=C311B0

draw_actor_name=C334CF

draw_equipped_esper=C334E6
  JSR draw_string
  LDA $001E,Y
  CMP #$FF
  BEQ blank_esper_name
  ASL
  ASL
  ASL
  TAX
  LDY #$0008
draw_equipped_esper_loop_start
  LDA $E6F6E1,X
  STA $2180
  INX
  DEY
  BNE draw_equipped_esper_loop_start
  STZ $2180
  JMP draw_memorized_string
blank_esper_name
  LDY #$0008
  LDA #$FF
blank_esper_name_loop_start
  STA $2180
  DEY
  BNE blank_esper_name_loop_start
  STZ $2180
  JMP draw_memorized_string

draw_string=C33519
  LDX #$9E89
  STX $2181
  REP #$20
  TYA
  SEP #$20
  STA $2180
  XBA
  STA $2180
  TDC
  LDY $67
  RTS

gogo_commands_cursor_positions=C33713
  $9E41
  $9E4D
  $9E59
  $9E65

draw_blue_text_and_symbols=C35D3C
  JSR draw_lv_hp_mp_and_non_blue_symbols
  BRA draw_other_blue_text
draw_lv_hp_mp_and_non_blue_symbols
  LDA #$20
  STA $29
  LDX #$6455
  LDY #$0008
  JSR draw_multiple_strings
  LDA #$24
  STA $29
  LDX #$644B
  LDY #$000A
  JSR draw_multiple_strings
  RTS
draw_other_blue_text
  LDA #$2C
  STA $29
  LDX #$6437
  LDY #$0014
  JSR draw_multiple_strings
  RTS

draw_command_name=C35EE1

gogo_portrait_position=C35F50
  LDX #$610A

window_layout=C35F79
  $B758 | $0601
  $2F5A | $0906
  $8B58 | $1C18
  $C758 | $0012
  $8760 | $0712

draw_actor_values=C35FC2
  JSL reset_function
  LDY $67
  JSR define_bat_pwr_mode
  LDA #$20
  STA $29
  LDA $11A6
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7C5D
  JSR draw_3_digits_8_bits
  LDA $11A4
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7CDD
  JSR draw_3_digits_8_bits
  LDA $11A2
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7D5D
  JSR draw_3_digits_8_bits
  LDA $11A0
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7DDD
  JSR draw_3_digits_8_bits
  JSR define_current_or_projected_bat_pwr
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDX #$7E5D
  JSR draw_3_digits
  LDA $11BA
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7EDD
  JSR draw_3_digits_8_bits
  LDA $11A8
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7F5D
  JSR draw_3_digits_8_bits
  LDA $11BB
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$7FDD
  JSR draw_3_digits_8_bits
  LDA $11AA
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  LDX #$885D
  JSR draw_3_digits_8_bits
  LDY #$38CD
  JSR draw_actor_name
  JSR draw_esper_and_equipment
  LDA #$20
  STA $29
  LDX #$6096
  JSR draw_lv_hp_and_mp
  LDX $67
  LDA $0011,X
  STA $F1
  LDA $0012,X
  STA $F2
  LDA $0013,X
  STA $F3
  JSR convert_24_bit_number_into_text_blank_leading_zeros
  LDX #$39B5
  JSR draw_8_digits
  JSR calculate_xp_needed_for_level_up
  JSR convert_24_bit_number_into_text_blank_leading_zeros
  LDX #$39A3
  JSR draw_8_digits
  STZ $47
  JSR process_animation_queue
  JMP draw_status_effects
lv_hp_mp_quantity_position=C36096
  $E738
  $2339
  $2D39
  $6339
  $6D39
calculate_xp_needed_for_level_up

draw_actor_commands=C36102
  LDY #$7AF5
  JSR draw_string
  JSR draw_command_name
  LDY #$7B75
  JSR draw_string
  INY
  JSR draw_command_name
  LDY #$7BF5
  JSR draw_string
  INY
  INY
  JSR draw_command_name
  LDY #$7C75
  JSR draw_string
  INY
  INY
  INY
  JMP draw_command_name

draw_status_effects=C3625B
  LDY #$3A1D
  LDX #$2D50

text_pointers=C36437
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

draw_multiple_strings=C369BA

draw_memorized_string=C37FD9

define_current_or_projected_bat_pwr=C39371

define_bat_pwr_mode=C399E8

draw_equipped_weapon=C3F091
  CMP #$FF
  BEQ blank_equipped_weapon
  STA $4202
  LDA #$0D
  STA $4203
  NOP
  NOP
  NOP
  LDX $4216
  LDY #$000D
draw_equipped_weapon_loop_start
  LDA $D2B300,X
  STA $2180
  INX
  DEY
  BNE draw_equipped_weapon_loop_start
  STZ $2180
  JMP draw_memorized_string
blank_equipped_weapon
  LDY #$000D
  LDA #$FF
blank_equipped_weapon_loop_start
  STA $2180
  DEY
  BNE blank_equipped_weapon_loop_start
  STZ $2180
  JMP draw_memorized_string

draw_passive_abilities=C3F0E1
  JSR draw_string
  LDA $28
  TAX
  LDA $69,X
  STA $2C
  ASL
  ADC $2C
  ADC $2B
  STA $4202
  LDA #$10
  STA $4203
  NOP
  NOP
  NOP
  LDX $4216
  LDY #$0010
draw_passive_abilities_loop_start
  LDA $F00000,X
  STA $2180
  INX
  DEY
  BNE draw_passive_abilities_loop_start
  STZ $2180
  JMP draw_memorized_string

draw_esper_and_equipment
  LDY #$7D6D
  JSR draw_equipped_esper

  LDY #$7ACD
  STZ $2B
  JSR draw_passive_abilities
  LDY #$7B4D
  LDA #$01
  STA $2B
  JSR draw_passive_abilities
  LDY #$7BCD
  LDA #$02
  STA $2B
  JSR draw_passive_abilities

  LDY #$7DEB
  JSR draw_string
  LDA $001F,Y
  JSR draw_equipped_weapon

  LDY #$7E6B
  JSR draw_string
  LDA $0020,Y
  JSR draw_equipped_weapon

  LDY #$7EEB
  JSR draw_string
  LDA $0021,Y
  JSR draw_equipped_weapon

  LDY #$7F6B
  JSR draw_string
  LDA $0022,Y
  JSR draw_equipped_weapon

  LDY #$7FEB
  JSR draw_string
  LDA $0023,Y
  JSR draw_equipped_weapon

  LDY #$886B
  JSR draw_string
  LDA $0024,Y
  JSR draw_equipped_weapon

  JMP draw_actor_commands


passive_abilities=F00000
  "AP raises Morph " | "duration. Learns" | "spells on lvl up"
  "May unlock      " | "certain doors.  " | "---             "
  "Learns Swdtechs " | "on level up.    " | "---             "
  "Randomly        " | "protected by    " | "Interceptor.    "
  "Some shops may  " | "offer him a     " | "discount.       "
  "Learns Blitzes  " | "on level up.    " | "---             "
  "Learns spells   " | "on level up.    " | "---             "
  "Learns Lores by " | "getting hit.    " | "---             "
  "---             " | "---             " | "---             "
  "---             " | "---             " | "---             "
  "Learns Dances   " | "in new          " | "environments.   "
  "Learns Rages on " | "the Veldt when  " | "using Leap.     "
  "Has access to   " | "allies' spells. " | "---             "
  "Berserked. May  " | "gain new moves  " | "with relics.    "