Title: New Treasure Chest options
Author: TheNPCnextDoor
Version: 1.0.1
Applies to: FF6us v1.0, FF6us v1.1 (both unheadered)
Tested on: FF6us v1.0

Contents: asm/esper_name.asm
          asm/general_actions.asm
          asm/item_name.asm
          asm/treasure_chest.txt
          New Treasure Chest Options v1.0.1.ips
          README.txt

ROM addresses: C0/4C3A, C0/4C4F-C0/4CA1, C0/4CAC-C0/4CBF, C0/4CC1
               C0/8412-C0/8421
               C0/9926-C0/9927, C0/9962-C0/9963, C0/9966-C0/9967
               C0/D613-C0/D62B, C0/D62E-C0/D714
               CC/FD10, CC/FD12, CC/FD14, CC/FD16, CC/FD18, CC/FD1A, CC/FD1C,
                 CC/FD1E, CC/FD20
               CC/FE1A-CC/FE1B
               CE/DDD1-CE/DE58, CE/DE5A-CE/DE69, CE/DE6B-CE/DE8A,
                 CE/DE8C-CE/DECC
               CE/EFAF-CE/EFC7

--------------------------------------------------------------------------------

Description:

FF6 offers 4 types of Treasure Chests:

* Item
* Monster-In-A-Box!
* Gold
* Empty

--------------------------------------------------------------------------------

What this patch does:

It adds two new types to this list:

* Rare Item
* Esper

--------------------------------------------------------------------------------

How to use this patch:

Out of the box, this patch will seemingly have no effect. To use it, you must
modify the types and contents of treasure chests. The data is located at
ED/8634. Each treasure chest is composed of 5 bytes:

* Its X coordinate
* Its Y coordinate
* The location of its activation in the RAM
* Its type
* Its content

The accepted values for the types are:

* 0x80: Gold
* 0x40: Item
* 0x20: Monster-In-A-Box

Plus the newly added values:

* 0x10: Esper
* 0x08: Rare Item

Now, for the content byte, the accepted values are inclusively:

* 0x00 to 0x1A for Espers
* 0x00 to 0x13 for Rare Items

NB: If you choose to put Coral in a chest, it will also increase the internal
counter of your totals of Coral by one. Like in the original game, there is no
current way of knowing the current quantity.

However, please note that the address in the RAM dealing with the number of
Corals is shared with the value of Cid's Health. Both are located at $1FD0.
In vanilla, it doesn't matter since both events can never interfere with each
other. So, if you want to put Corals in chests for some kind of treasure hunt,
for example, you will have to modify the events that touch that value.

--------------------------------------------------------------------------------

Version history:

v1.0   - July 25, 2021
         Initial release.

v1.0.1 - July 26, 2021
         Fixed a bug that prevented the Coral quantity to be updated.
         Added info about Corals

--------------------------------------------------------------------------------

Credits:

Imzogelmo            - For writing the document about chest data and the
                       disassembly of the C0 bank.
Madsiur and Assassin - They answered by numerous questions in the FF6hacking
                       forum when I first tackled this hack in 2018.
Voragain             - This man heard me talked about this project and its
                       multiple iterations too many times for me to count. Yet,
                       he was always interested and convinced me to release the
                       MVP I was sitting on for months. Thanks, bro!
Serity               - Serity's eagerness to improve upon this patch made me
                       realize that there was a bug in the code.