
#include<iostream>
#include<cstring>
#include<cstdio>
using namespace std;
char a[200];
int len=0;
void reversef(int fro,int to){
    bool is_ok=false;
    for(int i=to;i>=fro;i--){
        if(is_ok==false){
            if(a[i]!='0'){ is_ok=true; cout<<a[i]; }
        }
        else cout<<a[i];
        if(is_ok==false&&i==fro) cout<<"0";
    }
}
void reverseb(int fro,int to){
    bool is_ok=false;
    for(int i=fro;i<=to;i++){
        if(a[i]!='0'){ fro=i; is_ok=true; break; }
    }
    if(is_ok==false){ cout<<"0"; return; }
    else { for(int i=to;i>=fro;i--) cout<<a[i]; }
}
int main(){
    cin>>a;
    len=strlen(a);
    for(int i=0;i<len;i++){
        if(a[i]=='.'){ reversef(0,i-1); cout<<a[i]; reverseb(i+1,len-1); return 0; }
        if(a[i]=='/'){ reversef(0,i-1); cout<<a[i]; reversef(i+1,len-1); return 0; }
        if(a[i]=='%'){ reversef(0,i-1); cout<<"%"; return 0; }
    }
    reversef(0,len-1);
    return 0;
}
