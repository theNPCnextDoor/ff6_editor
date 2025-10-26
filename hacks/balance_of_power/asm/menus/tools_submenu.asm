m=8,x=16

draw_string=C302F9
upload_bg3_a_plus_b=C30E6E
sound_click=C30EB2
play_buzzer=C3209E
initialize_esper_submenu=C320B3
initialize_swdtech_submenu=C320EE
draw_string=C302F9
initialize_blitz_submenu=C32105
initialize_magic_submenu=C3211C
initialize_lore_submenu=C3216E
initialize_rage_submenu=C321A6
initialize_dance_submenu=C321DE
load_member_sram_address_in_skills_menu=C34EDD
set_source_as_dance_name=C357C1
draw_menu_title_dance=C35781

jump_to_invoke_submenu=C32019
  JMP initialize_selected_skill_submenu

load_cursor_positions=C34B59
  LDY #$F21C

number_of_rows_in_skills_menu=C34B73
  $08

powers_of_two=C34B74
  $01
  $02
  $04
  $08
  $10
  $20
  $40
  $80

draw_submenu_names=C34CDE
  JMP prepare_draw_submenu_names

assign_palette_to_submenus=C34D3D
  STZ $79
  JSR load_member_sram_address_in_skills_menu
  STY $7A
  REP #$20
  TYA
  ADC #$0004
  STA $7C
  SEP #$20
  LDX #$0008
next_menu_command
  DEX
  ASL $79
check_if_member_command_equals_menu_command2
  LDA $0016,Y
  CMP $C34D0D,X
  BNE goto_next_member_command
  INC $79
  BRA goto_next_menu_command
goto_next_member_command
  INY
  CPY $7C
  BNE check_if_member_command_equals_menu_command2
goto_next_menu_command
  LDY $7A
  CPX #$0000
  BNE next_menu_command
is_gogo_the_member
  LDA $0000,Y
  CMP #$0C
  BNE assign_palette_to_submenus_end
  LSR $79
  ASL $79
assign_palette_to_submenus_end
  RTS

skills_submenu_dimensions=C34D9E
  $070C

submenu_names=C34CFD
  ptr espers_submenu_name
  ptr magic_submenu_name
  ptr swdtech_submenu_name
  ptr blitz_submenu_name
  ptr lore_submenu_name
  ptr rage_submenu_name
  ptr dance_submenu_name
  ptr tools_submenu_name

commands_to_check_in_submenu
  $02       ; Magic (for Espers)
  $02       ; Magic (for Magic)
  $07       ; SwdTech
  $0A       ; Blitz
  $0C       ; Lore
  $10       ; Rage
  $13       ; Dance
  $09       ; Tools

is_palette_white_or_gray
  LSR $79
  BCC is_palette_gray
  LDA #$20
  BRA set_palette
is_palette_gray
  LDA #$24
set_palette
  STA $29
  RTS

build_dance_or_tools_list=C35620
  JSR load_either_dance_or_tools_list

jump_to_draw_dance_or_tools=C3577E
  JSR draw_dance_or_tools

draw_a_row_of_two_skills_first_skill=C357AA
  JSR set_source_for_skill_name

draw_a_row_of_two_skills_second_skill=C357B5
  JSR set_source_for_skill_name



espers_submenu_name=C35C48
  $0D79 | "Espers",$00
magic_submenu_name
  $8D79 | "Magic",$00
swdtech_submenu_name
  $8D7A | "SwdTech",$00
blitz_submenu_name
  $0D7B | "Blitz",$00
lore_submenu_name
  $8D7B | "Lore",$00
rage_submenu_name
  $0D7C | "Rage",$00
dance_submenu_name
  $8D7C | "Dance",$00
; Tools/Arsenal is separated from the rest. It currently is located at C3F212.

load_last_two_bytes_of_rare_item_for_list=C383B0
  STZ $F1
  LDA $1EBD
  AND #$0F
  STA $F2
  NOP
  NOP
  NOP

number_of_iterations_to_draw_the_rare_item_list=C383E3
  LDY #$000E

set_rare_item_name_source=C38436
  LDY #$CF50      ; D2/B300
  STY $EF         ; Set src LBs
set_rare_item_name_length_and_bank
  LDY #$000D      ; Letters: 13
  STY $EB         ; Set src size
  LDA #$CF        ; Bank: D2
  STA $F1         ; Set src HB
  RTS

; This is separated from the rest. Eventually, would be nice to find a place where it all fits together.
tools_submenu_name=C3F212
  $0D7D | "Tools  ",$00

cursor_positions_for_skills_menu
  $0014
  $0024
  $0044
  $0054
  $0064
  $0074
  $0084
  $0094

jump_table_for_initializing_submenus
  ptr initialize_esper_submenu
  ptr initialize_magic_submenu
  ptr initialize_swdtech_submenu
  ptr initialize_blitz_submenu
  ptr initialize_lore_submenu
  ptr initialize_rage_submenu
  ptr initialize_dance_submenu
  ptr initialize_dance_submenu

initialize_selected_skill_submenu
  TDC
  LDA $4B
  TAX
  LDA $C34B74,X
  AND $7E
  BNE is_correct_menu
  JMP play_buzzer
is_correct_menu
  JSR sound_click
  LDA $4E
  STA $7F
  ASL
  TAX
  JMP ($F22C,X)

prepare_draw_submenu_names
  LDX $00
  LDA $79
  STA $7E
draw_submenu_names_loop_start
  REP #$20
  LDA $C34CFD,X
  TAY
  SEP #$20
  LDA $79
  JSR is_palette_white_or_gray
  PHX
  JSR draw_string
  PLX
  INX
  INX
  CPX #$0010
  BNE draw_submenu_names_loop_start
  LDA #$20
  STA $29
  JMP upload_bg3_a_plus_b

load_either_dance_or_tools_list
  LDA $7F
  CMP #$06
  BNE load_tools_list
  LDA $1D4C
  RTS
load_tools_list
  LDX $02
  STX $1EBA
  STX $1EBC
  LDA #$FF
  RTS

set_source_for_skill_name
  LDA $7F
  CMP #$06
  BNE set_source_as_tool_name
  JMP set_source_as_dance_name
set_source_as_tool_name
  LDY #$D020      ; D2/B300
  STY $EF         ; Set src LBs
  JMP set_rare_item_name_length_and_bank

draw_dance_or_tools
  LDA $7F
  CMP #$06
  BNE draw_tools
  LDY #$5C9F
  RTS
draw_tools
  LDY #$F2B2
jump_to_draw_string
  RTS

menu_title_tools
  $B781 | "Tools  ",$00

rare_item_names=CFCF50
  "Cider        "
  "Old<0xFE>Clock-Key"
  "Yummy<0xFE>Fish   "
  "Fresh<0xFE>Fish   "
  "Stale<0xFE>Fish   "
  "Rotten<0xFE>Fish  "
  "Lump<0xFE>of<0xFE>Metal"
  "Lola's<0xFE>Letter"
  "Coral        "
  "Books        "
  "Royal<0xFE>Letter "
  "Rust-Rid     "
  "Autograph    "
  "Manicure     "
  "Opera<0xFE>Record "
  "Magn.Glass   "
  "<TOOL>NoiseBlaster"
  "<TOOL>Bio<0xFE>Blaster "
  "<TOOL>Flash       "
  "<TOOL>Chain<0xFE>Saw   "
  "<TOOL>Debilitator "
  "<TOOL>Drill       "
  "<TOOL>Air<0xFE>Anchor  "
  "<TOOL>AutoCrossbow"
  "Eerie<0xFE>Stone  "
  "Odd<0xFE>Picture  "
  "Dull<0xFE>Picture "
  "Pendant      "
