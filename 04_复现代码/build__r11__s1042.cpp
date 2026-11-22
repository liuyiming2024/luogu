
#include<bits/stdc++.h>
using namespace std;
char s[250000];
char S;
int len=0;
int main(){
    int w=0,l=0;
    while(cin>>S){ if(S=='E') break; s[len++]=S; }
    for(int i=0;i<len;i++){
        if(s[i]=='W') w++; else l++;
        if(max(w,l)>=11&&abs(w-l)>=2) cout<<w<<":"<<l<<endl,w=0,l=0;
    }
    cout<<w<<":"<<l<<endl,w=0,l=0;
    puts("");
    for(int i=0;i<len;i++){
        if(s[i]=='W') w++; else l++;
        if(max(w,l)>=21&&abs(w-l)>=2) cout<<w<<":"<<l<<endl,w=0,l=0;
    }
    cout<<w<<":"<<l,w=0,l=0;
    return 0;
}
