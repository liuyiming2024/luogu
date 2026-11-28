// P1030 std：后序末为根，中序定位后递归，直接拼先序串。
#include <bits/stdc++.h>
using namespace std;string ans;
void solve(const string& in,const string& post){if(in.empty())return;char root=post.back();ans+=root;
 int p=(int)in.find(root);solve(in.substr(0,p),post.substr(0,p));solve(in.substr(p+1),post.substr(p,post.size()-p-1));}
int main(){string in,post;if(!(cin>>in>>post))return 0;solve(in,post);cout<<ans<<'\n';return 0;}
