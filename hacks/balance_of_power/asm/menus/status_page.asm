m=8,x=16

@initialize_status_menu=C31C46
  JSR reset_stuff_for_status_menu

@jump_to_handle_y_and_b_in_status_menu=C32246
  JMP handle_y_and_b_in_status_menu
  NOP
  NOP
@handle_b_in_status_menu

@gogo_commands_cursor_positions=C33713
  $419E
  $4D9E
  $599E
  $659E

@draw_blue_text_and_symbols=C35D3C
  JSR draw_lv_hp_mp_and_non_blue_symbols
  BRA draw_other_blue_text
@draw_lv_hp_mp_and_non_blue_symbols
  LDA #$20
  STA $29
  LDX #$6453
  LDY #$0008
  JSR draw_multiple_strings
  LDA #$24
  STA $29
  LDX #$644B
  LDY #$0008
  JSR draw_multiple_strings
  RTS
@draw_other_blue_text
  LDA #$2C
  STA $29
  LDX #$6437
  LDY #$0014
  JMP draw_multiple_strings

@window_layout=C35F79
  $58B7 | $0106
  $5A2F | $0609
  $588B | $181C
  $58C7 | $1200
  $6087 | $1207

@status_menu_actor_jump_table=C35F92
  JMP set_actor_id_in_status_menu

@draw_actor_values=C35FC2
  JSL reset_function
  LDY $67
  JSR define_bat_pwr_mode
  LDA #$20
  STA $29
  LDA $11A6
  JSR prepare_right_aligned_8_bit_number
  LDX #$7C5D
  JSR draw_3_digits_8_bits
  LDA $11A4
  JSR prepare_right_aligned_8_bit_number
  LDX #$7CDD
  JSR draw_3_digits_8_bits
  LDA $11A2
  JSR prepare_right_aligned_8_bit_number
  LDX #$7D5D
  JSR draw_3_digits_8_bits
  LDA $11A0
  JSR prepare_right_aligned_8_bit_number
  LDX #$7DDD
  JSR draw_3_digits_8_bits
  JSR define_current_or_projected_bat_pwr
  JSR prepare_right_aligned_16_bit_number
  LDX #$7E5D
  JSR draw_3_digits
  LDA $11BA
  JSR prepare_right_aligned_8_bit_number
  LDX #$7EDD
  JSR draw_3_digits_8_bits
  LDA $11A8
  JSR prepare_right_aligned_8_bit_number
  LDX #$7F5D
  JSR draw_3_digits_8_bits
  LDA $11BB
  JSR prepare_right_aligned_8_bit_number
  LDX #$7FDD
  JSR draw_3_digits_8_bits
  LDA $11AA
  JSR prepare_right_aligned_8_bit_number
  LDX #$885D
  JSR draw_3_digits_8_bits
  LDY #$38CD
  JSR draw_actor_name
  JSR draw_esper_equipment_and_passive_abilities
  LDA #$20
  STA $29
  LDX #$6096
  JSR draw_lv_hp_and_mp
  JSR can_use_magic
  BCS draw_experience
  JSR hide_mp_in_status_menu
@draw_experience
  LDA $9E
  BNE jump_to_draw_total_exp
  JSR draw_needed_experience
  BRA resume_drawing_status_menu
@jump_to_draw_total_exp
  JSR draw_total_experience
@resume_drawing_status_menu
  STZ $47
  JSR process_animation_queue
  JMP draw_status_effects

@lv_hp_mp_quantity_position=C36096
  $38E7
  $3923
  $392D
  $3963
  $396D
@calculate_xp_needed_for_level_up

@draw_actor_commands=C36102
  LDY #$7AF5
  JSR prepare_string
  JSR draw_command_name
  LDY #$7B75
  JSR prepare_string
  INY
  JSR draw_command_name
  LDY #$7BF5
  JSR prepare_string
  INY
  INY
  JSR draw_command_name
  LDY #$7C75
  JSR prepare_string
  INY
  INY
  INY
  JMP draw_command_name

@draw_status_effects=C3625B
  LDY #$3A1D
  LDX #$2D50

@initialize_lineup=C3631D
  JSR reset_stuff_for_status_menu

@jump_to_draw_actor_value_in_lineup=C3635D
  JSR set_actor_id_in_lineup

@text_pointers=C36437
  ptr text_status               ;37
  ptr text_vigor                ;39
  ptr text_speed                ;3B
  ptr text_stamina              ;3D
  ptr text_mag_pwr              ;3F
  ptr text_bat_pwr              ;41
  ptr text_defense              ;43
  ptr text_evade                ;45
  ptr text_mag_def              ;47
  ptr text_mblock               ;49
  ptr text_lv                   ;4B
  ptr text_hp                   ;4D
  ptr text_mp                   ;4F
  ptr text_your_exp             ;51
  ptr text_hp_slash             ;53
  ptr text_mp_slash             ;55
  ptr text_evade_percentage     ;57
  ptr text_mblock_percentage    ;59
  ptr text_max_level            ;5B
  ptr text_hide_mp              ;5D
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

@draw_passive_abilities=C3F0AA
  JSR prepare_string
  LDA $2C           ; Load actor id
  ASL               ; Double it
  ADC $2C           ; Add actor id, therefore multiplying the original number by 3
  ADC $2B           ; Add offset (0 for first line, 1 for second line...)
  STA $4202         ; Store multiplicand
  LDA #$10          ; Set multiplier 16
  STA $4203         ; Store mutiplier
  NOP
  NOP
  NOP
  LDX $4216         ; Load product in X
  LDY #$0010        ; Set counter at 16
@draw_passive_abilities_loop_start
  LDA $F00000,X     ; Load character
  STA $2180
  INX               ; Next character
  DEY               ; Decrease counter
  BNE draw_passive_abilities_loop_start
  STZ $2180
  JMP draw_memorized_string

@draw_equipped_weapon
; There is another function to draw equipment, but it didn't work properly
; when using it in the lineup menu.
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
@draw_equipped_weapon_loop_start
  LDA $D2B300,X
  STA $2180
  INX
  DEY
  BNE draw_equipped_weapon_loop_start
  STZ $2180
  JMP draw_memorized_string
@blank_equipped_weapon
  LDY #$000D
  LDA #$FF
@blank_equipped_weapon_loop_start
  STA $2180
  DEY
  BNE blank_equipped_weapon_loop_start
  STZ $2180
  JMP draw_memorized_string

@draw_esper_equipment_and_passive_abilities
; Passive abilities
  LDY #$7ACD
  STZ $2B
  JSR draw_passive_abilities
  LDY #$7B4D
  LDA #$01                      ; Load offset to get second line of passive abilities
  STA $2B
  JSR draw_passive_abilities
  LDY #$7BCD
  LDA #$02                      ; Load offset to get THIRD line of passive abilities
  STA $2B
  JSR draw_passive_abilities

; Esper
  LDY #$7D6D
  JSR draw_equipped_esper

; Weapon
  LDY #$7DEB
  JSR prepare_string
  LDA $001F,Y
  JSR draw_equipped_weapon

; Shield
  LDY #$7E6B
  JSR prepare_string
  LDA $0020,Y
  JSR draw_equipped_weapon

; Helmet
  LDY #$7EEB
  JSR prepare_string
  LDA $0021,Y
  JSR draw_equipped_weapon

; Armor
  LDY #$7F6B
  JSR prepare_string
  LDA $0022,Y
  JSR draw_equipped_weapon

; Relic 1
  LDY #$7FEB
  JSR prepare_string
  LDA $0023,Y
  JSR draw_equipped_weapon

; Relic 2
  LDY #$886B
  JSR prepare_string
  LDA $0024,Y
  JSR draw_equipped_weapon

  JMP draw_actor_commands

@set_actor_id_in_status_menu
  PHX
  LDA $28
  TAX
  LDA $69,X
  STA $2C
  PLX
  JMP ($5F95,X)

@set_actor_id_in_lineup
  LDA $28
  STA $2C
  JMP draw_actor_values

@draw_9_digits
; A 24-bit character uses 8 characters maximum, which allows to put one non-decimal
; character in there, either at $F7 or $FF. In this script, it is used to insert
; the "↑" character after the needed experience.
  LDY #$0009
  STY $E0
  LDY $00
  JMP draw_text

@draw_total_experience
  LDX $67
  LDA $0011,X
  STA $F1
  LDA $0012,X
  STA $F2
  LDA $0013,X
  STA $F3
  JSR prepare_right_aligned_24_bit_number
  LDA #$FF              ; Loading "space" character
  STA $FF
  LDX #$39A5
  JMP draw_9_digits

@draw_needed_experience
  LDX $67               ; Loading actor address
  LDA $0008,X           ; Loading level
  CMP #$63
  BCS draw_max_level    ; If it is 99, branch
  JSR calculate_xp_needed_for_level_up
  JSR prepare_right_aligned_24_bit_number
  LDA #$D4              ; Loading "↑" character
  STA $FF
  LDX #$39A5            ; Next to XP quantity
  JMP draw_9_digits
@draw_max_level
  LDX #$645B
  LDY #$0002
  JMP draw_multiple_strings

@handle_y_and_b_in_status_menu
  LDA $09
  BIT #$80
  BEQ handle_y                              ; If "B" isn't pressed, then branch
  JMP handle_b_in_status_menu
@handle_y
  BIT #$40
  BEQ jump_to_handle_gogo_in_status_menu    ; If "Y" isn't pressed, then branch
  JSR sound_click
  LDA $9E
  EOR #$FF
  STA $9E
  ; There probably is a more efficient way to do this, but so far this is
  ; the only thing that worked.
  JMP handle_swapping_character
@jump_to_handle_gogo_in_status_menu
  JMP handle_gogo_in_status_menu

@reset_stuff_for_status_menu
; Clearing the bool used for switching between needed and total XP
; This is the same value used in the Magic menu to switch between %learned and MP cost.
  STZ $9E
  JMP reset_stuff_for_animations

@hide_mp_in_status_menu
; The following subroutine is not efficient, as we are first writing the line,
; then removing it completely (which is the behavior in vanilla) only to
; then write it again with the dashes.
  LDA #$24
  STA $29
  LDX #$644F
  LDY #$0002
  JSR draw_multiple_strings
  LDA #$20
  STA $29
  LDX #$645D
  LDY #$0002
  JMP draw_multiple_strings

