m=true,x=false
start=C0/D700

  LDA $EB
  STA $1A
  SEC
  SBC #$36
  JSR $D70F
  LDA #$02
  JMP $9B5C
  STA $1A
  AND #$07      
  TAX           
  LDA $1A
  LSR           
  LSR           
  LSR           
  TAY           
  LDA $1A69,Y   
  ORA $C0BAFC,X 
  STA $1A69,Y
  RTS