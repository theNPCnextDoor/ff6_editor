m=8,x=16

@jump_to_create_portrait_in_magic_menu=C34D92
  JSR set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_lore_menu=C35209
  JSR set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_swdtech_menu=C352EE
  JSR set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_rage_menu=C353A1
  JSR set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_espers_menu=C35466
  JSR set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_blitz_menu=C355E4
  JSR set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_dance_menu=C35784
  JSR set_y_value_to_middle_right_corner

@jump_to_create_portrait_in_status_menu=C35D14
  JMP set_y_value_to_top_right_corner

@gogo_portrait_position=C35F50
  LDX #$60CA

@init_vars_for_portrait_by_upper_left_corner=C361FB
  JSR load_anim_ptr ; Load anim ptr
  LDA $2A         ; Y: 56
  STA $344A,X     ; Set sprite's
  JMP init_m7      ; Set pose timer

@jump_to_create_portrait_in_lineup_menu=C36374
  JSR set_y_value_to_top_right_corner_then_jump_to_init_vars

@set_y_value_to_top_right_corner=C3F091
  LDA #$15
  STA $2A
  JMP jump_to_put_portrait_in_status_menus

@set_y_value_to_middle_right_corner
  LDA #$38
  STA $2A
  JMP jump_to_put_portrait_in_status_menus

@set_y_value_to_top_right_corner_then_jump_to_init_vars
  JSR load_anim_ptr      ; Load anim ptr
  LDA #$17     ; Y: 56
  STA $344A,X     ; Set sprite's
  JMP init_m7      ; Set pose timer

