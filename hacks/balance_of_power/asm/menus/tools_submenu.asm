m=8,x=16

set_all_submenus_gray=C34D3D
  LDA #$24
  LDX $00
set_all_submenus_gray_loop_start
  STA $79,Y
  INX
  CPX #$0007
  BNE set_all_submenus_gray_loop_start
  JSR load_member_sram_address_in_skills_menu
  PHY
  LDX #$0004
set_all_submenus_gray_loop_end
  PHX
  LDX $00
assign_palette_to_submenus_loop_start
  LDA $0016,Y
  CMP $C34D78,X
  BNE goto_next_command ;  If doesn't have command, branch
  LDA #$20
  STA $79,Y
goto_next_command
  INX
  CPX #$0007
  BNE assign_palette_to_submenus_loop_start
  INY
  PLX
  DEX
  BNE set_all_submenus_gray_loop_end ; If there are still members, branch
  PLY
  LDA $0000,Y
  CMP #$0C
  BNE assign_palette_to_submenus_loop_end ; if not Gogo, branch
  LDA #$24
  STA $79
assign_palette_to_submenus_loop_end
  RTS

skills_submenu_dimensions=C34D9E
  $070C

load_member_sram_address_in_skills_menu=C34EDD

submenu_names=C3F212
  ptr espers_submenu_name
  ptr magic_submenu_name
  ptr swdtech_submenu_name
  ptr blitz_submenu_name
  ptr lore_submenu_name
  ptr rage_submenu_name
  ptr tools_submenu_name
espers_submenu_name
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
tools_submenu_name
  $8D7B | "Tools",$00

commands_to_check_in_submenu=C3F212
  $02       ; Magic (for Espers)
  $02       ; Magic (for Magic)
  $07       ; SwdTech
  $0A       ; Blitz
  $0C       ; Lore
  $10       ; Rage
  $13       ; Dance
  $09       ; Tools