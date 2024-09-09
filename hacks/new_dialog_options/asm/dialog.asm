m=true,x=true


start=C0/7FBF
  LDA #$CD      
  STA $CB       
  REP #$20      
  LDA $D0       
  ASL           
  TAX           
  LDA $CCE602,X 
  STA $C9       
  LDA $D0       
  CMP $CCE600   
  BCC label_7FDC
  TDC           
  SEP #$20      
  INC $CB       

label_7FDC
  TDC           
  SEP #$20      
  LDA #$01      
  STA $0568     
  RTS           
  STZ $0567     
  LDA $1EB9     
  AND #$40      
  BNE label_7FF4
  LDA $0745     
  BNE label_7FF8

label_7FF4
  STZ $0745     
  RTS           

label_7FF8
  LDA #$64      
  STA $0567     
  LDA #$CE      
  STA $CB       
  LDA $0520     
  ASL           
  TAX           
  REP #$21      
  LDA $E68400,X 
  ADC #$F100    
  STA $C9       
  TDC           
  SEP #$20      
  STZ $C0       
  LDY $00       

label_8018
  LDA [$C9],Y   
  BEQ label_8029
  TAX           
  LDA $C48FC0,X 
  CLC           
  ADC $C0       
  STA $C0       
  INY           
  BRA label_8018

label_8029
  LDA #$E0      
  SEC           
  SBC $C0       
  LSR           
  STA $BF       
  TAY           
  STY $4204     
  LDA #$10      
  STA $4206     
  NOP           
  NOP           
  NOP           
  NOP           
  NOP           
  NOP           
  NOP           
  LDA $4214     
  STA $4202     
  LDA #$20      
  STA $4203     
  NOP           
  NOP           
  NOP           
  LDY $4216     
  STY $C1       

label_8054
  JSR $824D     
  JSR $8609     
  LDA $0568     
  BPL label_8054
  STZ $D3       
  STZ $CC       
  JSR $2EA8     
  RTS           
  LDA $CF       
  PHA           
  LDA $CB       
  PHA           
  LDX $C9       
  PHX           
  STZ $C0       

label_8072
  LDY $00       
  LDA [$C9],Y   
  BPL label_80B0
  AND #$7F      
  ASL           
  TAX           
  LDA $CF       
  CMP #$80      
  BEQ label_8088
  LDA #$80      
  STA $CF       
  BRA label_809C

label_8088
  LDA $C0DFA0,X 
  CMP #$7F      
  BEQ label_80D2
  PHX           
  TAX           
  LDA $C48FC0,X 
  CLC           
  ADC $C0       
  STA $C0       
  PLX           

label_809C
  LDA $C0DFA1,X 
  CMP #$7F      
  BEQ label_80D2
  TAX           
  LDA $C48FC0,X 
  CLC           
  ADC $C0       
  STA $C0       
  BRA label_80C6

label_80B0
  LDY $00       
  LDA [$C9],Y   
  CMP #$20      
  BCC label_80DC
  CMP #$7F      
  BEQ label_80D2
  TAX           
  LDA $C48FC0,X 
  CLC           
  ADC $C0       
  STA $C0       

label_80C6
  INC $C9       
  BNE label_8072
  INC $CA       
  BNE label_8072
  INC $CB       
  BRA label_8072

label_80D2
  PLX           
  STX $C9       
  PLA           
  STA $CB       
  PLA           
  STA $CF       
  RTS           

label_80DC
  CMP #$1A      
  BEQ label_8118
  CMP #$02      
  BCC label_80D2
  CMP #$10      
  BCS label_80D2
  DEC           
  DEC           
  STA $4202     
  LDA #$25      
  STA $4203     
  LDA $CF       
  BPL label_80D2
  LDA #$06      
  STA $1A       
  LDY $4216     

label_80FD
  LDA $1602,Y   
  CMP #$FF      
  BEQ label_80D2
  SEC           
  SBC #$60      
  TAX           
  LDA $C48FC0,X 
  CLC           
  ADC $C0       
  STA $C0       
  INY           
  DEC $1A       
  BNE label_80FD
  BRA label_80D2

label_8118
  LDA $0583     
  STA $4202     
  LDA #$0D      
  STA $4203     
  LDA $CF       
  BPL label_80D2
  LDA #$0C      
  STA $1A       
  LDX $4216     

label_812E
  TXY           
  LDA $D2B301,X 
  CMP #$FF      
  BEQ label_80D2
  SEC           
  SBC #$60      
  TAX           
  LDA $C48FC0,X 
  CLC           
  ADC $C0       
  STA $C0       
  TYX           
  INX           
  DEC $1A       
  BNE label_812E
  BRA label_80D2
  REP #$20      
  LDA $00       
  STA $7E7204   
  STA $7E7404   
  LDA $1D55     
  STA $7E7202   
  STA $7E7402   
  STA $7E7206   
  STA $7E7406   
  TDC           
  SEP #$20      
  LDA $0567     
  BEQ label_817B
  DEC $0567     
  BNE label_817B
  JSR $2FED     

label_817B
  LDA $0568     
  BNE label_8181
  RTS           

label_8181
  LDX $0569     
  BEQ label_818B
  DEX           
  STX $0569     
  RTS           

label_818B
  LDX $056B     
  BEQ label_81AF
  REP #$20      
  TXA           
  AND #$7FFF    
  TAX           
  TDC           
  SEP #$20      
  CPX $00       
  BNE label_81A8
  STZ $056C     
  STZ $D3       
  STZ $056F     
  BRA label_81AF

label_81A8
  LDX $056B     
  DEX           
  STX $056B     

label_81AF
  LDA $D3       
  BNE label_81B6
  JMP $823B     

label_81B6
  LDA $056F     
  CMP #$02      
  BCC label_821F
  LDA $056E     
  ASL           
  TAX           
  REP #$20      
  LDA $0570,X   
  STA $C3       
  TDC           
  SEP #$20      
  LDA $07       
  AND #$0F      
  BNE label_81D7
  STZ $056D     
  BRA label_8209

label_81D7
  LDA $056D     
  BNE label_821F
  LDA $07       
  AND #$0A      
  BEQ label_81F2
  LDA $056E     
  DEC           
  BMI label_8209
  STA $056E     
  LDA #$01      
  STA $056D     
  BRA label_8209

label_81F2
  LDA $07       
  AND #$05      
  BEQ label_8209
  LDA $056E     
  INC           
  CMP $056F     
  BEQ label_8209
  STA $056E     
  LDA #$01      
  STA $056D     

label_8209
  JSR $879A     
  LDA $056E     
  ASL           
  TAX           
  REP #$20      
  LDA $0570,X   
  STA $0580     
  TDC           
  SEP #$20      
  INC $0582     

label_821F
  LDA $D3       
  CMP #$01      
  BEQ label_822D
  LDA $06       
  BMI label_8241
  DEC $D3       
  BRA label_8241

label_822D
  LDA $06       
  BPL label_8241
  DEC $D3       
  STZ $056F     
  STZ $056C     
  BRA label_8241
  LDA $CC       
  BEQ label_8242
  DEC $CC       

label_8241
  RTS           

label_8242
  LDA $0568     
  BPL label_824D
  STA $BA       
  STZ $0568     
  RTS           

label_824D
  JSR $8067     
  LDA $BF       
  CLC           
  ADC $C0       
  BCS label_825B
  CMP $C8       
  BCC label_825F

label_825B
  JSR $851A     
  RTS           

label_825F
  LDA $CF       
  BMI label_8284
  LDA $CF       
  TAX           
  LDA $7E9183,X 
  STA $CD       
  STZ $CE       
  LDA $7E9184,X 
  BEQ label_827A
  JSR $84D0     
  INC $CF       
  RTS           

label_827A
  LDA #$80      
  STA $CF       
  JSR $84D0     
  JMP $829D     

label_8284
  LDY $00       
  LDA [$C9],Y   
  STA $BD       
  INY           
  LDA [$C9],Y   
  STA $BE       
  LDA $BD       
  BMI label_829A
  CMP #$20      
  BCC label_82B5
  JMP $845A     

label_829A
  JMP $8466     
  LDA #$01      
  BRA label_82A3
  LDA #$02      

label_82A3
  CLC           
  ADC $C9       
  STA $C9       
  LDA $CA       
  ADC #$00      
  STA $CA       
  LDA $CB       
  ADC #$00      
  STA $CB       
  RTS           

label_82B5
  CMP #$00      
  BNE label_82C2
  JSR $8554     
  LDA #$80      
  STA $0568     
  RTS           

label_82C2
  CMP #$01      
  BNE label_82CC
  JSR $851A     
  JMP $829D     

label_82CC
  CMP #$10      
  BCS label_8302
  DEC           
  DEC           
  STA $4202     
  LDA #$25      
  STA $4203     
  NOP           
  NOP           
  NOP           
  NOP           
  LDY $4216     
  LDX $00       

label_82E3
  LDA $1602,Y   
  SEC           
  SBC #$60      
  STA $7E9183,X 
  CMP #$9F      
  BEQ label_82F8
  INY           
  INX           
  CPX #$0006    
  BNE label_82E3

label_82F8
  TDC           
  STA $7E9183,X 
  STZ $CF       
  JMP $8263     

label_8302
  CMP #$10      
  BNE label_830F
  LDX #$003C    
  STX $0569     
  JMP $829D     

label_830F
  CMP #$11      
  BNE label_832A
  LDA $BE       
  STA $4202     
  LDA #$0F      
  STA $4203     
  NOP           
  NOP           
  NOP           
  NOP           
  LDX $4216     
  STX $0569     
  JMP $82A1     

label_832A
  CMP #$12      
  BNE label_8337
  LDX #$8001    
  STX $056B     
  JMP $829D     

label_8337
  CMP #$13      
  BNE label_8341
  JSR $8554     
  JMP $829D     

label_8341
  CMP #$14      
  BNE label_8362
  LDA $BE       
  STA $1E       
  STZ $1F       
  LDX $00       
  LDA #$7F      

label_834F
  STA $7E9183,X 
  INX           
  CPX $1E       
  BNE label_834F
  TDC           
  STA $7E9183,X 
  STZ $CF       
  JMP $829D     

label_8362
  CMP #$15      
  BNE label_837F
  LDA $056F     
  ASL           
  TAY           
  REP #$20      
  LDA $C1       
  STA $0570,Y   
  TDC           
  SEP #$20      
  LDA #$FF      
  STA $BD       
  INC $056F     
  JMP $845A     

label_837F
  CMP #$16      
  BNE label_83A4
  LDA $BE       
  STA $4202     
  LDA #$0F      
  STA $4203     
  NOP           
  NOP           
  REP #$20      
  LDA $4216     
  ORA #$8000    
  STA $056B     
  TDC           
  SEP #$20      
  LDA #$01      
  STA $D3       
  JMP $82A1     

label_83A4
  CMP #$19      
  BNE label_83D3
  STZ $1A       
  LDX $00       
  TXY           

label_83AD
  LDA $1A       
  BNE label_83B8
  LDA $0755,Y   
  BEQ label_83C3
  INC $1A       

label_83B8
  LDA $0755,Y   
  CLC           
  ADC #$54      
  STA $7E9183,X 
  INX           

label_83C3
  INY           
  CPY #$0007    
  BNE label_83AD
  TDC           
  STA $7E9183,X 
  STZ $CF       
  JMP $8263     

label_83D3
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

label_840F
  CMP #$1B      
  BNE label_844B
  LDA $0584     
  STA $4202     
  LDA #$04      
  STA $4203     
  NOP           
  NOP           
  NOP           
  LDX $4216     
  LDY $00       
  LDA #$7E      
  PHA           
  PLB           

label_842A
  LDA $E6F568,X 
  SEC           
  SBC #$60      
  STA $9183,Y   
  CMP #$9F      
  BEQ label_843F
  INX           
  INY           
  CPY #$0004    
  BNE label_842A

label_843F
  TDC           
  STA $9183,Y   
  TDC           
  PHA           
  PLB           
  STZ $CF       
  JMP $8263     

label_844B
  SEC           
  SBC #$1B      
  STA $CE       
  LDA $BE       
  STA $CD       
  JSR $84D0     
  JMP $82A1     
  LDA $BD       
  STA $CD       
  STZ $CE       
  JSR $84D0     
  JMP $829D     
  AND #$7F      
  ASL           
  TAY           
  LDX #$DFA0    
  STX $2A       
  LDA #$C0      
  STA $2C       
  LDA [$2A],Y   
  STA $7E9183   
  INY           
  LDA [$2A],Y   
  STA $7E9184   
  TDC           
  STA $7E9185   
  STZ $CF       
  JMP $8263     
  LDA #$7E      
  STA $2183     
  LDX #$9E00    
  STX $2181     
  LDX $00       

label_8497
  LDA $C48FC0,X 
  STA $2180     
  INX           
  CPX #$0080    
  BNE label_8497
  LDX #$DFA0    
  STX $2A       
  LDA #$C0      
  STA $2C       
  LDX $00       
  TXY           

label_84B0
  STZ $1A       
  LDA [$2A],Y   
  TAX           
  LDA $C48FC0,X 
  STA $1A       
  INY           
  LDA [$2A],Y   
  TAX           
  LDA $C48FC0,X 
  CLC           
  ADC $1A       
  STA $2180     
  INY           
  CPY #$0100    
  BNE label_84B0
  RTS           
  LDX $CD       
  LDA $C48FC0,X 
  CLC           
  ADC $BF       
  CMP $C8       
  BCC end       
  JSR $851A     
  RTS           

end=C0/84E1

