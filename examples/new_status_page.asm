; This changes the Status menu to include equipment info as well as
; specific characters' passive abilities, such as Terra's Morph gaining
; in duration as AP are gained or Umaro being uncontrollable.
; Also, pressing Y will alternate between total XP and XP needed for level up,
; which is represented by the "↑" character.

map: HiROM

m = 8, x = 16

db palette_addr = $29
db xp_switch_addr = $9E

dw xp_low_byte = $0011
dw xp_medium_byte = $0012
dw xp_high_byte = $0013
dw weapon_addr = $001F
dw shield_addr = $0020
dw helmet_addr = $0021
dw armor_addr = $0022
dw relic1_addr = $0023
dw relic2_addr = $0024

dw multiplicand_addr = $4202
dw multiplier_addr = $4203
dw product_addr = $4216

@reset_function = $C20006

@draw_3_digits = $C30486
@draw_3_digits_8_bits = $C304C0
@draw_text = $C304C7
@prepare_right_aligned_8_bit_number = $C304E0
@prepare_right_aligned_16_bit_number = $C3052E
@prepare_right_aligned_24_bit_number = $C30582
@load_anim_ptr = $C30ACC
@draw_lv_hp_and_mp = $C30C6C
@can_use_magic = $C30D2B
@sound_click = $C30EB2
@process_animation_queue = $C311B0
@init_m7 = $C31206

@initialize_status_menu = $C31C46
  JSR !reset_stuff_for_status_menu

@jump_to_handle_y_and_b_in_status_menu = $C32246
  JMP !handle_y_and_b_in_status_menu
  NOP
  NOP
@handle_b_in_status_menu

@handle_gogo_in_status_menu = $C32254

@draw_actor_name = $C334CF
@draw_equipped_esper = $C334E6
@prepare_string = $C33519
@reset_stuff_for_animations = $C3352F

@gogo_commands_cursor_positions = $C33713
  $419E
  $4D9E
  $599E
  $659E

@jump_to_create_portrait_in_magic_menu = $C34D92
  JSR !set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_lore_menu = $C35209
  JSR !set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_swdtech_menu = $C352EE
  JSR !set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_rage_menu = $C353A1
  JSR !set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_espers_menu = $C35466
  JSR !set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_blitz_menu = $C355E4
  JSR !set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_dance_menu = $C35784
  JSR !set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_status_menu = $C35D14
  JMP !set_y_value_to_top_right_corner

@draw_blue_text_and_symbols = $C35D3C
  JSR !draw_lv_hp_mp_and_non_blue_symbols
  BRA draw_other_blue_text
@draw_lv_hp_mp_and_non_blue_symbols
  LDA #$20
  STA palette_addr
  LDX #$6453
  LDY #$0008
  JSR !draw_multiple_strings
  LDA #$24
  STA palette_addr
  LDX #$644B
  LDY #$0008
  JSR !draw_multiple_strings
  RTS
@draw_other_blue_text
  LDA #$2C
  STA palette_addr
  LDX #$6437
  LDY #$0014
  JMP !draw_multiple_strings

@handle_swapping_character = $C35D83
@draw_command_name = $C35EE1

@gogo_portrait_position = $C35F50
  LDX #$60CA

@window_layout = $C35F79
  $58B7 | $0106
  $5A2F | $0609
  $588B | $181C
  $58C7 | $1200
  $6087 | $1207

@jump_to_set_actor_id = $C35F92
  JMP !set_actor_id_in_status_menu
@jump_table_for_actor_info

@draw_actor_values = $C35FC2
  JSL reset_function
  LDY $67
  JSR !define_bat_pwr_mode
  LDA #$20
  STA palette_addr
  LDA $11A6
  JSR !prepare_right_aligned_8_bit_number
  LDX #$7C5D
  JSR !draw_3_digits_8_bits
  LDA $11A4
  JSR !prepare_right_aligned_8_bit_number
  LDX #$7CDD
  JSR !draw_3_digits_8_bits
  LDA $11A2
  JSR !prepare_right_aligned_8_bit_number
  LDX #$7D5D
  JSR !draw_3_digits_8_bits
  LDA $11A0
  JSR !prepare_right_aligned_8_bit_number
  LDX #$7DDD
  JSR !draw_3_digits_8_bits
  JSR !define_current_or_projected_bat_pwr
  JSR !prepare_right_aligned_16_bit_number
  LDX #$7E5D
  JSR !draw_3_digits
  LDA $11BA
  JSR !prepare_right_aligned_8_bit_number
  LDX #$7EDD
  JSR !draw_3_digits_8_bits
  LDA $11A8
  JSR !prepare_right_aligned_8_bit_number
  LDX #$7F5D
  JSR !draw_3_digits_8_bits
  LDA $11BB
  JSR !prepare_right_aligned_8_bit_number
  LDX #$7FDD
  JSR !draw_3_digits_8_bits
  LDA $11AA
  JSR !prepare_right_aligned_8_bit_number
  LDX #$885D
  JSR !draw_3_digits_8_bits
  LDY #$38CD
  JSR !draw_actor_name
  JSR !draw_esper_equipment_and_passive_abilities
  LDA #$20
  STA palette_addr
  LDX #$6096
  JSR !draw_lv_hp_and_mp
  JSR !can_use_magic
  BCS draw_experience
  JSR !hide_mp_in_status_menu
@draw_experience
  LDA xp_switch_addr
  BNE jump_to_draw_total_exp
  JSR !draw_needed_experience
  BRA resume_drawing_status_menu
@jump_to_draw_total_exp
  JSR !draw_total_experience
@resume_drawing_status_menu
  STZ $47
  JSR !process_animation_queue
  JMP !draw_status_effects

@lv_hp_mp_quantity_position = $C36096
  $38E7
  $3923
  $392D
  $3963
  $396D
@calculate_xp_needed_for_level_up

@draw_actor_commands = $C36102
  LDY #$7AF5
  JSR !prepare_string
  JSR !draw_command_name
  LDY #$7B75
  JSR !prepare_string
  INY
  JSR !draw_command_name
  LDY #$7BF5
  JSR !prepare_string
  INY
  INY
  JSR !draw_command_name
  LDY #$7C75
  JSR !prepare_string
  INY
  INY
  INY
  JMP !draw_command_name

@jump_to_put_portrait_in_status_menus = $C361AC

@init_vars_for_portrait_by_upper_left_corner = $C361FB
  JSR !load_anim_ptr ; Load anim ptr
  LDA $2A         ; Y: 56
  STA $344A,X     ; Set sprite's
  JMP !init_m7      ; Set pose timer

@draw_status_effects = $C3625B
  LDY #$3A1D
  LDX #$2D50

@initialize_lineup = $C3631D
  JSR !reset_stuff_for_status_menu

@jump_to_draw_actor_value_in_lineup = $C3635D
  JSR !set_actor_id_in_lineup

@jump_to_create_portrait_in_lineup_menu = $C36374
  JSR !set_y_value_to_top_right_corner_then_jump_to_init_vars

@text_pointers = $C36437
  ptr !text_status               ;37
  ptr !text_vigor                ;39
  ptr !text_speed                ;3B
  ptr !text_stamina              ;3D
  ptr !text_mag_pwr              ;3F
  ptr !text_bat_pwr              ;41
  ptr !text_defense              ;43
  ptr !text_evade                ;45
  ptr !text_mag_def              ;47
  ptr !text_mblock               ;49
  ptr !text_lv                   ;4B
  ptr !text_hp                   ;4D
  ptr !text_mp                   ;4F
  ptr !text_your_exp             ;51
  ptr !text_hp_slash             ;53
  ptr !text_mp_slash             ;55
  ptr !text_evade_percentage     ;57
  ptr !text_mblock_percentage    ;59
  ptr !text_max_level            ;5B
  ptr !text_hide_mp              ;5D
@text_status
  $78F9 | "Status",$00
@text_hp_slash
  $392B | "/",$00
@text_mp_slash
  $396B | "/",$00
@text_evade_percentage
  $7F63 | "%",$00
@text_mblock_percentage
  $8863 | "%",$00
@text_lv
  $38DD | "LV",$00
@text_hp
  $391D | "HP",$00
@text_mp
  $395D | "MP",$00
@text_your_exp
  $399D | "XP  ",$00
@text_vigor
  $7C4D | "Vigor  ¨",$00
@text_speed
  $7CCD | "Speed  ¨",$00
@text_stamina
  $7D4D | "Stamina¨",$00
@text_mag_pwr
  $7DCD | "Mag.Pwr¨",$00
@text_bat_pwr
  $7E4D | "Bat.Pwr¨",$00
@text_defense
  $7ECD | "Defense¨",$00
@text_evade
  $7F4D | "Evade %¨",$00
@text_mag_def
  $7FCD | "Mag.Def¨",$00
@text_mblock
  $884D | "MBlock%¨",$00
@text_max_level
  $39A3 | "Max level!",$00
@text_hide_mp
  $3965 | " --/  --",$00

@draw_multiple_strings = $C369BA
@draw_memorized_string = $C37FD9
@define_current_or_projected_bat_pwr = $C39371
@define_bat_pwr_mode = $C399E8

@set_y_value_to_top_right_corner = $C3F091
  LDA #$15
  STA $2A
  JMP !jump_to_put_portrait_in_status_menus

@set_y_value_to_middle_right_corner
  LDA #$38
  STA $2A
  JMP !jump_to_put_portrait_in_status_menus

@set_y_value_to_top_right_corner_then_jump_to_init_vars
  JSR !load_anim_ptr      ; Load anim ptr
  LDA #$17     ; Y: 56
  STA $344A,X     ; Set sprite's
  JMP !init_m7      ; Set pose timer

@draw_passive_abilities
  JSR !prepare_string
  LDA $2C           ; Load actor id
  ASL               ; Double it
  ADC $2C           ; Add actor id, therefore multiplying the original number by 3
  ADC $2B           ; Add offset (0 for first line, 1 for second line...)
  STA multiplicand_addr  ; Store multiplicand_addr
  LDA #$10          ; Set multiplier_addr 16
  STA multiplier_addr    ; Store mutiplier
  NOP
  NOP
  NOP
  LDX product_addr       ; Load product_addr in X
  LDY #$0010        ; Set counter at 16
@draw_passive_abilities_loop_start
  LDA passive_abilities,X     ; Load character
  STA $2180
  INX               ; Next character
  DEY               ; Decrease counter
  BNE draw_passive_abilities_loop_start
  STZ $2180
  JMP !draw_memorized_string

@draw_equipped_weapon
; There is another function to draw equipment, but it didn't work properly
; when using it in the lineup menu.
  CMP #$FF
  BEQ blank_equipped_weapon
  STA multiplicand_addr
  LDA #$0D
  STA multiplier_addr
  NOP
  NOP
  NOP
  LDX product_addr
  LDY #$000D
@draw_equipped_weapon_loop_start
  LDA item_names,X
  STA $2180
  INX
  DEY
  BNE draw_equipped_weapon_loop_start
  STZ $2180
  JMP !draw_memorized_string
@blank_equipped_weapon
  LDY #$000D
  LDA #$FF
@blank_equipped_weapon_loop_start
  STA $2180
  DEY
  BNE blank_equipped_weapon_loop_start
  STZ $2180
  JMP !draw_memorized_string

@draw_esper_equipment_and_passive_abilities
; Passive abilities
  LDY #$7ACD
  STZ $2B
  JSR !draw_passive_abilities
  LDY #$7B4D
  LDA #$01                      ; Load offset to get second line of passive abilities
  STA $2B
  JSR !draw_passive_abilities
  LDY #$7BCD
  LDA #$02                      ; Load offset to get THIRD line of passive abilities
  STA $2B
  JSR !draw_passive_abilities

; Esper
  LDY #$7D6D
  JSR !draw_equipped_esper

; Weapon
  LDY #$7DEB
  JSR !prepare_string
  LDA weapon_addr,Y
  JSR !draw_equipped_weapon

; Shield
  LDY #$7E6B
  JSR !prepare_string
  LDA shield_addr,Y
  JSR !draw_equipped_weapon

; Helmet
  LDY #$7EEB
  JSR !prepare_string
  LDA helmet_addr,Y
  JSR !draw_equipped_weapon

; Armor
  LDY #$7F6B
  JSR !prepare_string
  LDA armor_addr,Y
  JSR !draw_equipped_weapon

; Relic 1
  LDY #$7FEB
  JSR !prepare_string
  LDA relic1_addr,Y
  JSR !draw_equipped_weapon

; Relic 2
  LDY #$886B
  JSR !prepare_string
  LDA relic2_addr,Y
  JSR !draw_equipped_weapon

  JMP !draw_actor_commands

@set_actor_id_in_status_menu
  PHX
  LDA $28
  TAX
  LDA $69,X
  STA $2C
  PLX
  JMP (!jump_table_for_actor_info,X)

@set_actor_id_in_lineup
  LDA $28
  STA $2C
  JMP !draw_actor_values

@draw_9_digits
; A 24-bit character uses 8 characters maximum, which allows to put one non-decimal
; character in there, either at $F7 or $FF. In this script, it is used to insert
; the "↑" character after the needed experience.
  LDY #$0009
  STY $E0
  LDY $00
  JMP !draw_text

@draw_total_experience
  LDX $67
  LDA xp_low_byte,X
  STA $F1
  LDA xp_medium_byte,X
  STA $F2
  LDA xp_high_byte,X
  STA $F3
  JSR !prepare_right_aligned_24_bit_number
  LDA #$FF              ; Loading "space" character
  STA $FF
  LDX #$39A5
  JMP !draw_9_digits

@draw_needed_experience
  LDX $67               ; Loading actor address
  LDA $0008,X           ; Loading level
  CMP #$63
  BCS draw_max_level    ; If it is 99, branch
  JSR !calculate_xp_needed_for_level_up
  JSR !prepare_right_aligned_24_bit_number
  LDA #$D4              ; Loading "↑" character
  STA $FF
  LDX #$39A5            ; Next to XP quantity
  JMP !draw_9_digits
@draw_max_level
  LDX #$645B
  LDY #$0002
  JMP !draw_multiple_strings

@handle_y_and_b_in_status_menu
  LDA $09
  BIT #$80
  BEQ handle_y                              ; If "B" isn't pressed, then branch
  JMP !handle_b_in_status_menu
@handle_y
  BIT #$40
  BEQ jump_to_handle_gogo_in_status_menu    ; If "Y" isn't pressed, then branch
  JSR !sound_click
  LDA xp_switch_addr
  EOR #$FF
  STA xp_switch_addr
  ; There probably is a more efficient way to do this, but so far this is
  ; the only thing that worked.
  JMP !handle_swapping_character
@jump_to_handle_gogo_in_status_menu
  JMP !handle_gogo_in_status_menu

@reset_stuff_for_status_menu
; Clearing the bool used for switching between needed and total XP
; This is the same value used in the Magic menu to switch between %learned and MP cost.
  STZ xp_switch_addr
  JMP !reset_stuff_for_animations

@hide_mp_in_status_menu
; The following subroutine is not efficient, as we are first writing the line,
; then removing it completely (which is the behavior in vanilla) only to
; then write it again with the dashes.
  LDA #$24
  STA palette_addr
  LDX #$644F
  LDY #$0002
  JSR !draw_multiple_strings
  LDA #$2C
  STA palette_addr
  LDX #$645D
  LDY #$0002
  JSR !draw_multiple_strings
  LDA #$20
  STA palette_addr
  RTS

@passive_abilities
  ; There is definitely place for improvement here. First, it should be
  ; menu descriptions instead of menu strings. Also, this should make use
  ; of pointers.

  "AP raises Morph " | "duration. Learns" | "spells on LV up."
  "Can unlock      " | "certain locked  " | "doors.          "
  "Learns Swdtechs " | "on level up.    " | "                "
  "Randomly        " | "protected by    " | "Interceptor.    "
  "Some shops may  " | "offer him a     " | "discount.       "
  "Learns Blitzes  " | "on level up.    " | "                "
  "Learns spells   " | "on level up.    " | "                "
  "Learns Lores by " | "getting hit.    " | "                "
  "                " | "                " | "                "
  "                " | "                " | "                "
  "Learns Dances   " | "in new          " | "environments.   "
  "Learns Rages on " | "the Veldt when  " | "using Leap.     "
  "Has access to   " | "allies' spells. " | "                "
  "Uncontrollable. " | "Gains new moves " | "with relics.    "
  "                " | "                " | "                "
  "                " | "                " | "                "

@item_names = $D2B300