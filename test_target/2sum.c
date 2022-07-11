#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(void){
    char *data;
    int num1,num2;
    printf("Content-type: text/html\n\n");

    data = getenv("QUERY_STRING");

    if(data == NULL)
        printf("<p>null QUERY_STRING</p>");
    else if(sscanf(data,"num1=%d&num2=%d",&num1,&num2)!=2)
        printf("<p>err input</p>");
    else{
        int sum=num1+num2;
        if(num1>0&&num2>0&&sum<0){
            printf("boom");
            char *x="boommmmmmmmmmmmm";
            char y[3];
    	    strcpy(y, x);
        }
        printf("<p>sum result:%d</p>",sum);
    }

    return 0;
} 
