// P1054 等价表达式 · std（递归下降解析 + 多 a 值 mod 2^61-1 指纹）：
// 题面逐字：括号 > ^ > * > + -；+ - 同优先级且**包含 ^ 在内**同级从左到右；
// 幂指数只可能是 1..10 的正整数；多余空格任意位置；非法选项忽略。
// 对每个表达式在 a=1..30 下用快速幂求值，指纹相同即等价。
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long ull;
const ull MOD = 2305843009213693951ULL;          // 2^61 - 1（梅森素数）
ull mul_mod(ull a, ull b){ return (ull)((__uint128_t)a*b % MOD); }
ull pow_mod(ull b, ull e){
    ull r=1; b%=MOD;
    while(e){ if(e&1) r=mul_mod(r,b); b=mul_mod(b,b); e>>=1; }
    return r;
}
struct Parser {
    string s; size_t p=0; ull aval=0; bool valid=true;
    void ws(){ while(p<s.size() && isspace((unsigned char)s[p])) p++; }
    ull primary(){
        ws();
        if(p>=s.size()){ valid=false; return 0; }
        if(s[p]=='('){
            p++; ull v=expr(); ws();
            if(p>=s.size()||s[p]!=')'){ valid=false; return v; }
            p++; return v;
        }
        if(s[p]=='a'){ p++; return aval; }
        if(isdigit((unsigned char)s[p])){
            ull v=0;
            while(p<s.size() && isdigit((unsigned char)s[p])){
                v=v*10+(ull)(s[p]-'0'); p++;
            }
            return v%MOD;
        }
        valid=false; return 0;
    }
    ull power(){                                  // ^ 左结合
        ull v=primary(); ws();
        while(valid && p<s.size() && s[p]=='^'){
            p++; ull e=primary(); v=pow_mod(v,e);
        }
        return v;
    }
    ull term(){
        ull v=power(); ws();
        while(valid && p<s.size() && s[p]=='*'){
            p++; ull r=power(); v=mul_mod(v,r);
        }
        return v;
    }
    ull expr(){
        ull v=term(); ws();
        while(valid && p<s.size() && (s[p]=='+'||s[p]=='-')){
            char op=s[p++]; ull r=term();
            v = op=='+' ? (v+r)%MOD : (v+MOD-r%MOD)%MOD;
        }
        return v;
    }
    ull run(ull a){
        p=0; valid=true; aval=a;
        ull v=expr(); ws();
        if(p!=s.size()) valid=false;
        return v;
    }
};
vector<ull> fingerprint(const string& s){
    Parser P; P.s=s; vector<ull> r;
    for(ull a=1;a<=30;a++){
        ull v=P.run(a);
        if(!P.valid) return {};
        r.push_back(v);
    }
    return r;
}
int main(){
    string line;
    if(!getline(cin,line)) return 0;
    int n; if(!(cin>>n)) return 0;
    string eol; getline(cin,eol);
    vector<ull> target=fingerprint(line);
    string ans;
    for(int i=0;i<n;i++){
        if(!getline(cin,line)) break;
        vector<ull> f=fingerprint(line);
        if(!f.empty() && !target.empty() && f==target) ans+=char('A'+i);
    }
    cout<<ans<<"\n"; return 0;
}
