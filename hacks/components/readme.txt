FF3us SRAM Expansion
by madsiur
version 1.1
released on 10/04/2018
------------------------------------------------------------------------------
Files included

sram_nh.ips:         patch for FF3us 1.0 headerless ROM.
sram_nh_reverse.ips: reverse patch.
sram.asm:            Assembly file to assemble with bass.
------------------------------------------------------------------------------
Offset changed, free space used (by patch)

$C0FFD8:         Internal header SRAM size (from $03 to $05)
Bank $C3:        A few offsets related to saving and loading (see asm file)
$EFFBC8-$EFFC16: Extra code (see asm file)
------------------------------------------------------------------------------
New SRAM map

Slot 1 expansion:  $306A00-$307FFF
                   $306000-$3069FF = $7E1600-$7E1FFF

Slot 2 expansion:  $316A00-$317FFF
                   $316000-$3169FF = $7E1600-$7E1FFF

Slot 3 expansion:  $326A00-$327FFF
                   $326000-$3269FF = $7E1600-$7E1FFF

Other SRAM values: $336000-$3375FF (game common SRAM)
                   $337600-$337EFF (unused)
                   $337F00 = last altered savefile
                   $337F01 = rng index
                   $337F08 = checksum value #$E41B (slot 1)
                   $337F0A = checksum value #$E41B (slot 2)
                   $337F0C = checksum value #$E41B (slot 3)
                   $337F0E = checksum value #$E41B (slot 4, useless..)
------------------------------------------------------------------------------
Description

This hack expand SRAM by $1600 bytes, allowing now $2000 bytes for each
save slot plus a third 8Kb for general purpose. In original game, only 8Kb of
SRAM is used ($306000-$307FFF), each slot occupying $0A00 bytes and $200 bytes
for general purpose at the end of the 8Kb block.

With this hack, $306000-$307FFF is used for slot 1, $316000-$317FFF for slot 2
and $326000-$327FFF for slot 3. $336000-$337FFF is used for game SRAM.
When you play the game, $7E1600-$7E1FFF is still used and copied to 
correct slot at saving. $336000-$3375FF is copied to correct slot as 
extra SRAM. At game loading, correct slot is loaded into $336000-$3375FF. 
So in order to save or load from extra SRAM in your hack, use as an example 
STA $336000,X or LDA $336000,X.

Since $337600-$337EFF is not used, it means it could be use as scratchpad SRAM 
for temporary things or have a general use common to the three slots. 
$337FF0-$337FFF has same function as the original $307FF0-$307FFF.

SRAM could be expanded more but I figured a whole $2000 bytes instead of $0A00
is enough expansion for any hack. In HiROM mapping banks $20-$3F can be used 
to map SRAM, using always the $6000-$7FFF range of the bank. $C0FFD8 tell the 
emulator the SRAM size of the ROM.

I have not tested this on sd2snes, everdrive or real hardware. snes9x 1.55 and 
bsnes+ were used for testing. If you plan to use this hack and make a cart of 
your hack after, I have no idea what kind of cartridge you will need or if
32Kb of SRAM is supported by any existing SNES game.
------------------------------------------------------------------------------
Version history
10/04/2018 1.1 released
   -removed $336000 init (see sram.asm for details)
   -renamed $337F08-$337F0E from "fixed value" to "checksum value"
   
05/25/2018 1.0 initial released
------------------------------------------------------------------------------
Contact

themadsiur@gmail.com
