m=true,x=false
start=C0/83D3
  CMP #$1A      
  BNE label_840F
  LDA $0583     
  STA $4202     
  LDA #$0D      
  STA $4203     
  NOP           
  NOP           
  NOP           
  LDX $4216     
  LDY $00       
  LDA #$7E      
  PHA           
  PLB           

label_83EE
  LDA $D2B301,X 
  SEC           
  SBC #$60      
  STA $9183,Y   
  CMP #$9F      
  BEQ label_8403
  INX           
  INY           
  CPY #$000C    
  BNE label_83EE

label_8403
  TDC           
  STA $9183,Y   
  TDC           
  PHA           
  PLB           
  STZ $CF       
  JMP $8263     

end=C0/840D

label_840F=C0/840F
