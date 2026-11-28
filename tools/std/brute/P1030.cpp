// P1030 朴素：显式建指针二叉树 + 栈迭代先序遍历。
#include <bits/stdc++.h>
using namespace std;struct Node{char c;Node*l;Node*r;Node(char x):c(x),l(nullptr),r(nullptr){}};
Node* build(const string& in,const string& post){if(in.empty())return nullptr;char root=post.back();Node*u=new Node(root);
 int p=(int)in.find(root);u->l=build(in.substr(0,p),post.substr(0,p));u->r=build(in.substr(p+1),post.substr(p,post.size()-p-1));return u;}
int main(){string in,post;if(!(cin>>in>>post))return 0;Node*rt=build(in,post);string ans;stack<Node*>st;if(rt)st.push(rt);
 while(!st.empty()){Node*u=st.top();st.pop();ans+=u->c;if(u->r)st.push(u->r);if(u->l)st.push(u->l);}
 cout<<ans<<'\n';return 0;}
