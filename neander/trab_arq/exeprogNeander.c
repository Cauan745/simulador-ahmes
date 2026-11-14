 #include <stdio.h>
 #include <stdlib.h>
 #include <math.h>
 #define Nbit 8 //númeor de bits que a máquina opera
 #define MAX  (int)(pow(2,Nbit)) // Número máximo permitido para endereçamento

 // início das definições dos comandos da linguagem do Neander
 #define NOP pc++;
 #define STA(m) {mem[m]=ac;pc=pc+2;}
 #define LDA(m) {ac=mem[m];pc=pc+2;}
 #define ADD(m) {ac=((ac+mem[m])&(MAX-1));pc=pc+2;}
 #define OR(m) {ac=mem[m]|ac;pc=pc+2;}
 #define AND(m) {ac=mem[m]&ac;pc=pc+2;}
 #define NOT {ac=((~ac)&(MAX-1));pc++;}
 #define JMP(end) {goto end;}
 #define HLT pc++;
 #define JN(end) {if(ac<0) goto end;}
 #define JZ(end) {if(ac==0) goto end;}
 // fim das definições dos comandos da linguagem do Neander

 #define PRINT(i) printf(" %u \n",i);
 int main (){
   int pc=0;
   unsigned ac=0;
   unsigned int mem[256];
   char ch;//, str[30] ,str2[33],/*num1,num2,num3*/num[3];
  // int linha =1, ctr=0;
   for(int i=0;i<256;i++) mem[i]=0; //zera memória
    FILE *fp;
   if ((fp=fopen("mem.txt", "rb"))==NULL) {
        printf("o aquivo nao pode ser aberto. \n");
        exit(1);
   }
   char s[3]; int cont=0,indice=0;
   printf("\n Memória antes do processamento:\n");
   while ((ch=getc(fp))!=EOF) {
    printf("%c",ch);
    if (ch!='\n') {s[cont]=ch; cont++;} //acomula em s os caracteres da posição de memória até encontrar \n
                else {cont=0;mem[indice]=atoi(s);indice++; //transforma o conteúdo de s em inteiro 
                s[0]=0;s[1]=0;s[2]=0; // zera o conteúdo do vetor s para utilizá-lo na próxima posição de memória
                }
   }
    fclose(fp);
  
//#include "ST.h"
l0:  LDA(129)
l2:  ADD(128)
l4:  STA(131)
l6:  HLT
printf("\n Memória após o processamento:\n");
  for(int i=0;i<32;i++) {printf("%d:",i); printf("%d",mem[i]);
                         printf(" %d:",i+32); printf("%d",mem[i+32]);
                         printf(" %d:",i+64); printf("%d",mem[i+64]);
                         printf(" %d:",i+96); printf("%d",mem[i+96]);
                         printf(" %d:",i+128); printf("%d",mem[i+128]);
                         printf(" %d:",i+160); printf("%d",mem[i+160]);
                         printf(" %d:",i+192); printf("%d",mem[i+192]);
                         printf(" %d:",i+224); printf("%d\n",mem[i+224]);
                         }   
    printf("\n\n");
    printf("pc = ");PRINT(pc)
    printf("ac = ");PRINT(ac)
    printf("Número de bits = ");PRINT(MAX);
    if (ac>127) printf("Negativo\n\n");
                else  printf("Positivo\n\n");

    if (ac==0)  printf("Zero\n");
                else  printf("Diferente de Zero\n"); 
    return 0;
 }



 /*
 *Este software é de propriedade intelectual do Prof Dr. Marcello Batista Ribeiro
 *Professor Da Universidade Federal de Rondônia desde 1998.
 *contatos: mribeiro@unir.br ; ribeiro.marcello@gmail.com ; +55 69 99357-5296
 */