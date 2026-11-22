
#include<bits/stdc++.h>
using namespace std;
struct my_priority {
    vector<int>heap;
    void init() { heap.push_back(-1e9); }
    void gao(int pos) {
        int flag;
        if(pos*2>heap.size()-1)return;
        else if(pos*2==heap.size()-1)flag=0;
        else flag=heap[pos*2]>heap[pos*2+1];
        if(heap[pos]>heap[pos*2+flag]) { swap(heap[pos],heap[pos*2+flag]); gao(pos*2+flag); }
        return;
    }
    void doit(int i) {
        while(heap[i]<heap[i/2]) { swap(heap[i],heap[i/2]); i>>=1; }
        return;
    }
    void push(int w) { heap.push_back(w); doit(heap.size()-1); }
    int top() { return heap[1]; }
    void pop() { heap[1]=heap(heap.size()-1); heap.pop_back(); gao(1); }
    int size() { return heap.size()-1; }
} q;
int main() {
    int i,ans=0;
    int n,tmp;
    q.init();
    scanf("%d",&n);
    for(i=1; i<=n; i++) { scanf("%d",&tmp); q.push(tmp); }
    while(q.size()>1) {
        tmp=q.top(); q.pop();
        tmp+=q.top(); q.pop();
        ans+=tmp;
        q.push(tmp);
    }
    printf("%d\n",ans);
    return 0;
}
