m=false,x=false
start=C0/4C06

  REP #$20      
  LDA $ED8638,X 
  STA $1A       
  LDA $ED8636,X 
  STA $1E       
  AND #$0007    
  TAX           
  LDA $1E       
  AND #$01FF    
  LSR           
  LSR           
  LSR           
  TAY           
  TDC           
  SEP #$20
  LDA $1E40,Y
  AND $C0BAFC,X
  BNE $4BD3
  LDA $1E40,Y
  ORA $C0BAFC,X 
  STA $1E40,Y

is_gold
  LDA $1F       
  BPL is_item
  LDA $1A       
  STA $4202     
  LDA #$64      
  STA $4203     
  NOP           
  NOP           
  NOP           
  LDY $4216     
  STY $22       
  STZ $24
  JSR $D653
  JSR $02E5
  LDX #$0010
  BRA normal_event_bank

is_item
  BIT #$40
  BEQ is_monster
  LDA $1A
  STA $0583
  JSR $ACFC
  LDX #$0008
  BRA normal_event_bank

is_monster
  BIT #$20
  BEQ is_esper
  LDA $1A
  STA $0789
  LDX #$0040
  BRA normal_event_bank

is_esper
  BIT #$10
  BEQ is_rare_item
  LDA $1A
  STA $0584
  JSR $D68D
  LDX #$000C
  BRA normal_event_bank

is_rare_item
  BIT #$08
  BEQ is_empty
  LDA $1A
  STA $0584
  JSR $D621
  LDX #$D613
  BRA expanded_event_bank

is_empty
  LDX #$0014

expanded_event_bank
  LDA #$C0
  BRA second_part

normal_event_bank=C0/4CAC
  LDA #$CA

second_part
  STA $E7
  STX $E5
  STX $05F4
  LDX #$0000
  STX $0594
  LDA #$CA
  STA $0596
  STA $05F6
  LDA #$01      
  STA $05C7     
  LDX #$0003    
  STX $E8       
  LDY $0803     
  LDA $087C,Y   
  STA $087D,Y   
  LDA #$04      
  STA $087C,Y   
  JSR $2FED     
  LDX $2A       
  LDA $7F0000,X 
  CMP #$13      
  BNE end       
  STX $8F       
  LDX #$4D0C    
  STX $8C       
  LDA #$C0      
  STA $8E       
  LDX #$0000    
  STX $2A       
  LDA #$04      
  STA $055A     
  JSR $1EC4     
  LDA #$A6      
  JSR $02D3     
  RTS           

end=C0/4D06

