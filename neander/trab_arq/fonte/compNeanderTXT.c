//compNeanderTXT.c
 #include <stdio.h>
 #include <string.h>
 #include <stdlib.h>
 #include <stdbool.h>
 #include <ctype.h>
 
 
 int main (int argc, char *argv[]){
 
   int linha=0,ctr=0;
   char ch, str[30] ,str2[33],num[4];
   bool linhabranca=true; // Variável usada para detectar e pular a linha em branco
   int mem[256]; // Cria memória de inteiro com 256 posições
   for(int i=0;i<256;i++) mem[i]=0; //zera memória
 
  
   FILE *fp; 
   if ((fp=fopen(argv[1], "rb"))==NULL) { //abre o arquivo texto gerado pelo Neander
        printf("o aquivo nao pode ser aberto. \n");
        exit(1);
   }
   while ((ch=getc(fp))!=EOF) {
    if (ch=='\n') {str[ctr-1]='\0';ctr=0;
                      
                       for (int i=0;i<32;i++) str2[i]=' ';
                      str2[32]='\0';
                       for (int n=0;n<30;n++){
                       if ((n>4)&&(n<8)) {
                                            num[n-5]=str[n];
                                            if ((n-5)==2) 
                                                mem[linha]=atoi(num); 
                                         }
                       if ((n>8)&&(n<12)) {
                                            
                                            num[n-9]=str[n];
                                            if (((n-9)==2)&& (str[n]!=' ')) {
                                                            linha++;
                                                             mem[linha]=atoi(num); 
                                                            }
                                         }    
                                            }
                      
                      if ((linha==126) && linhabranca) {linha--; linhabranca=false;}
                      linha++; 
                    }
                  
                  else {str[ctr]=ch; ctr++;}
  
 }
    
    fclose(fp); //fecha o arquivo texto gerado pelo Neander

    if ((fp=fopen("mem.txt", "wb"))==NULL) { //abre o arquivo texto para copiar a memória
        printf("o aquivo nao pode ser aberto. \n");
        exit(1);
        }
     for(int i=0;i<256;i++) fprintf(fp,"%d\n",mem[i]); // copia o conteúdo da memória para o
                                                       // arquivo texto mem.txt
     fclose(fp); // Fecha o arquivo mem.txt
    
   if ((fp=fopen("ST.h", "wb"))==NULL) { // abre o arquivo texto ST.h para escrever o programa
                                         // em Assembler do Neander
                    printf("o aquivo nao pode ser aberto. \n");
                    exit(1);
                  }
                  else printf("o aquivo novo aberto com sucesso. \n");

//Linguagem assembler do Neander e seu correspondente valor em decimal:

//NOP 00
//STA 16
//LDA 32
//ADD 48
//OR  64
//AND 80
//NOT 96
//JMP 128
//JN  144
//JZ  160
//HLT 240

//gerando o programa em assemble Neander
bool programa=true;
    for(int i=0;i<256;i++){
      if (mem[i]==240) {programa=false; fprintf(fp, "l%d:  HLT",i);}
      if (programa) {
        if (mem[i]==16) {fprintf(fp, "l%d:  STA(%d)\n",i,mem[i+1]); i++;}
          else
        if (mem[i]==32) {fprintf(fp, "l%d:  LDA(%d)\n",i,mem[i+1]); i++;}
          else
        if (mem[i]==48) {fprintf(fp, "l%d:  ADD(%d)\n",i,mem[i+1]); i++;}
          else
        if (mem[i]==64) {fprintf(fp, "l%d:  OR(%d)\n",i,mem[i+1]); i++;}
          else
        if (mem[i]==80) {fprintf(fp, "l%d:  AND(%d)\n",i,mem[i+1]); i++;}
          else 
        if (mem[i]==96) {fprintf(fp, "l%d:  NOT\n",i);} 
          else
        if (mem[i]==128) {fprintf(fp, "l%d:  JMP(l%d)\n",i,mem[i+1]); i++;}
          else
        if (mem[i]==144) {fprintf(fp, "l%d:  JN(l%d)\n",i,mem[i+1]); i++;}
          else
        if (mem[i]==160) {fprintf(fp, "l%d:  JZ(l%d)\n",i,mem[i+1]); i++;}  
          else 
        if (mem[i]==0) {fprintf(fp, "l%d:  NOP\n",i);} 
      } 
    }

    

   fclose(fp); //Fecha o arquivo texto ST.h
   return 0;

 }