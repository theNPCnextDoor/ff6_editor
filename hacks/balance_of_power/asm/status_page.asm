m=8,x=16

reset_function=C20006

init_status_menu_pointer=C301F1
  ptr init_status_menu

draw_window=C30341

draw_3_digits=C30486

draw_8_digits=C304A3

draw_2_digits=C304B6

draw_3_digits_8_bits=C304C0

convert_8_bit_number_into_text_blank_leading_zeros=C304E0

convert_16_bit_number_into_text_blank_leading_zeros=C3052E

convert_24_bit_number_into_text_blank_leading_zeros=C30582

load_pointer_to_animation_table_for_portrait=C30ACC

set_portrait_x_position_based_on_row=C30AF1

draw_lv_hp_and_mp=C30C6C
  STX $EF
  LDA #$C3
  STA $F1
  LDX $67
  LDA $0008,X
  JSR convert_8_bit_number_into_text_blank_leading_zeros
  REP #$20
  LDA [$EF]
  TAX
  SEP #$20
  JSR draw_2_digits
  LDX $67
  LDA $000B,X
  STA $F3
  LDA $000C,X
  STA $F4
  JSR determine_max_hp_or_mp_with_gear_bonus
  JSR enforce_hp_cap
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDY #$0004
  JSR draw_current_or_max_hp_or_mp
  LDY $67
  JSR prevent_hp_excess
  LDA $0009,Y
  STA $F3
  LDA $000A,Y
  STA $F4
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDY #$0002
  JSR draw_current_or_max_hp_or_mp
  JSR determine_if_actor_is_magic_user
  BCC hide_mp
  LDX $67
  LDA $000F,X
  STA $F3
  LDA $0010,X
  STA $F4
  JSR determine_max_hp_or_mp_with_gear_bonus
  JSR enforce_mp_cap
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDY #$0008
  JSR draw_current_or_max_hp_or_mp
  LDY $67
  JSR prevent_mp_excess
  LDA $000D,Y
  STA $F3
  LDA $000E,Y
  STA $F4
  JSR convert_16_bit_number_into_text_blank_leading_zeros
  LDY #$0006
  JMP draw_current_or_max_hp_or_mp

hide_mp=C30CEF

draw_current_or_max_hp_or_mp=C30D21

determine_if_actor_is_magic_user=C30D2B

determine_max_hp_or_mp_with_gear_bonus=C30D65

enforce_hp_cap=C30D92

enforce_mp_cap=C30D9F

process_animation_queue=C311B0

init_m7=C31206

init_status_menu=C31C46
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

prevent_hp_excess=C32B9A

prevent_mp_excess=C32BBC

draw_actor_name=C334CF
  JSR draw_string
  LDX #$0006
draw_actor_name_loop_start
  LDA $0002,Y
  STA $2180
  INY
  DEX
  BNE draw_actor_name_loop_start
  STZ $2180
  JMP draw_memorized_string

draw_actor_class=C334E5

draw_equipped_esper=C334E6
  JSR prepare_name_drawing
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
prepare_name_drawing=C33519


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

reset_oam_and_anim_queue=C3352F

prepare_fade_in=C33541

gogo_commands_cursor_positions=C33713
  $9E41
  $9E4D
  $9E59
  $9E65

draw_status_menu=C35D05
  JSR draw_windows
  JSR draw_gogo_commands
  JSR draw_blue_text_and_symbols
  JSR draw_actor_info
  JSR upload_tilemap
  JMP jump_to_put_portrait_in_top_left_corner
draw_windows
  JSR clear_bg1_tilemap_a
  JSR clear_bg1_tilemap_d
  JSR clear_bg3_tilemap_a
  JSR clear_bg3_tilemap_b
  JSR clear_bg3_tilemap_c
  JSR clear_bg3_tilemap_d
  LDY #$5F81
  JSR draw_window
  LDY #$5F79
  JSR draw_window
  LDY #$5F7D
  JSR draw_window
  RTS
draw_blue_text_and_symbols
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

upload_tilemap=C35D77

draw_gogo_commands=C35DC1

draw_command_name=C35EE1

gogo_portrait_position=C35F50
  LDX #$610A

window_layout=C35F79
  $B758 | $0601
  $2F5A | $0906
  $8B58 | $1C18
  $C758 | $0012
  $8760 | $0712
draw_actor_info

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
  LDY #$399D
  JSR draw_actor_class
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

jump_to_put_portrait_in_top_left_corner=C3F160
  JSR create_portrait_a
  ; JMP put_portrait_in_top_left_corner

create_portrait_a=C361DA

put_portrait_in_top_left_corner=C3F163
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
  JSR init_variables_for_portrait_in_top_left_corner
  PLB
  RTS
init_variables_for_portrait_in_top_left_corner
  JSR load_pointer_to_animation_table_for_portrait
  REP #$20
  LDA #$0018 ; Y-position of actor portrait
  STA $344A,X
  SEP #$20
  JMP init_m7

condense_bg3_text=C3620B
  LDA #$02
  STA $4350
  LDA #$12
  STA $4351
  LDY #$622A
  STY $4352
  LDA #$C3
  STA $4354
  LDA #$C3
  STA $4357
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

draw_status_effects=C3625B
  LDY #$3A1D
  LDX #$3050

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

clear_bg1_tilemap_a=C36A15

clear_bg1_tilemap_d=C36A23

clear_bg3_tilemap_a=C36A3C

clear_bg3_tilemap_b=C36A41

clear_bg3_tilemap_c=C36A46

clear_bg3_tilemap_d=C36A4B

draw_memorized_string=C37FD9

define_current_or_projected_bat_pwr=C39371

define_bat_pwr_mode=C399E8

create_portrait=C3F0A0
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
  LDA #$0018 ; Y position of actor portrait
  STA $344A,X
  SEP #$20
  JMP init_m7
replace_portrait
  TDC
  LDA $60
  TAX
  LDA #$FF
  STA $7E35C9,X
  JSR create_portrait_a
  JMP create_portrait

draw_equipped_weapon
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

draw_esper_and_equipment
  LDY #$7D6D
  JSR draw_equipped_esper

  LDY #$7DEB
  JSR prepare_name_drawing
  LDA $001F,Y
  JSR draw_equipped_weapon

  LDY #$7E6B
  JSR prepare_name_drawing
  LDA $0020,Y
  JSR draw_equipped_weapon

  LDY #$7EEB
  JSR prepare_name_drawing
  LDA $0021,Y
  JSR draw_equipped_weapon

  LDY #$7F6B
  JSR prepare_name_drawing
  LDA $0022,Y
  JSR draw_equipped_weapon

  LDY #$7FEB
  JSR prepare_name_drawing
  LDA $0023,Y
  JSR draw_equipped_weapon

  LDY #$886B
  JSR prepare_name_drawing
  LDA $0024,Y
  JSR draw_equipped_weapon

  JMP draw_actor_commands