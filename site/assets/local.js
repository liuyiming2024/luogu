/* 本地轻量版 luogu · 前端逻辑
   硬约束：页面加载**零外网请求**、零 CDN、零外部依赖。
   所有 fetch 只在「用户主动点击」或「已显式配置 apiBase」时发生。
   登录态/评论/工单/设置全部 localStorage，隐私信息不出浏览器。 */
(function(){
"use strict";
var LL = {};
var K = {sess:"ll:sess", token:"ll:token", api:"ll:api", cmt:"ll:cmt:",
         std:"ll:std", imgs:"ll:imgs", pub:"ll:pub", push:"ll:push", pq:"ll:push_q",
         audit:"ll:audit", ideUrl:"ll:ide_url", subUrl:"ll:sub_url"};

/* ---------- 小工具 ---------- */
function $(s,r){return (r||document).querySelector(s);}
function $$(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
function get(k,d){try{var v=localStorage.getItem(k);return v?JSON.parse(v):d;}catch(e){return d;}}
function set(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(e){}}
function ts(){return new Date().toISOString().replace("T"," ").slice(0,19)+" UTC";}
function online(){return !!navigator.onLine;}
function apiBase(){return get(K.api,"");}
function tok(){return get(K.token,"");}
function authHeaders(){var t=tok();return t?{"Authorization":"Bearer "+t,"Content-Type":"application/json"}:{"Content-Type":"application/json"};}
/* 只在用户动作后调用；未配置 apiBase 直接返回 null，绝不发请求 */
function call(path,opt){
  var b=apiBase(); if(!b) return Promise.resolve(null);
  opt=opt||{}; opt.headers=Object.assign(authHeaders(),opt.headers||{});
  return fetch(b.replace(/\/$/,"")+path,opt).then(function(r){return r.json();})
    .catch(function(e){return {error:String(e)};});
}
function toast(m,cls){
  var d=document.createElement("div");
  d.className="ll-verdict "+(cls||"");
  d.style.cssText="position:fixed;right:16px;bottom:16px;z-index:99;max-width:340px;background:#fff;border:1px solid var(--ll-line);box-shadow:var(--ll-shadow)";
  d.textContent=m; document.body.appendChild(d);
  setTimeout(function(){d.remove();},3200);
}

/* ---------- 默认头像（看 luogu：洛谷风格默认头像，内联 SVG，零请求） ---------- */
var AVATAR = "data:image/svg+xml;utf8," + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="52" height="52" viewBox="0 0 52 52">'+
  '<rect width="52" height="52" rx="26" fill="#eaf4fb"/>'+
  '<circle cx="26" cy="20" r="9" fill="#9dc6e0"/>'+
  '<path d="M9 46c2-10 9-15 17-15s15 5 17 15" fill="#9dc6e0"/>'+
  '<circle cx="26" cy="26" r="25" fill="none" stroke="#cfe4f2" stroke-width="2"/></svg>');

/* ---------- 登录态 ---------- */
function session(){return get(K.sess,null);}
/* 三态：online(联网+已登录+配了api) / cached(有本地缓存) / invalid(无缓存且无网=灰色) */
function nameState(s){
  if(!s) return "invalid";
  if(online() && s.logged && apiBase()) return "online";
  if(s.name || s.uid || s.cookie) return "cached";
  return "invalid";
}
function chrome(){
  if($(".ll-top")) return;
  var s=session(), st=nameState(s);
  var bar=document.createElement("div"); bar.className="ll-top";
  var label = s ? (s.name || (s.mode==="cookie" ? "已登录（cookie）" : "已登录")) : "未登录";
  var extra = (s && s.mode!=="cookie" && s.uid) ? '<span class="ll-badge">uid '+esc(s.uid)+'</span>' : "";
  /* 气泡/牌子：有才渲染，没有不添加 */
  var bubble = (s && s.badge) ? '<span class="ll-bubble">'+esc(s.badge)+'</span>' : "";
  bar.innerHTML='<div class="in"><span class="ll-logo">本地 luogu</span>'+
    '<nav class="ll-nav">'+
      '<a href="index.html">首页</a><a href="problems.html">题目 / IDE</a>'+
      '<a href="submit.html">std 投稿</a><a href="self.html">本地操作</a>'+
      '<a href="reports/帮助手册.md.html">帮助手册</a>'+
      '<a href="reports/全量任务完成清单.md.html">完成清单</a>'+
      '<a href="reports/隐私声明与数据处理条款.md.html">隐私声明</a>'+
    '</nav><div class="ll-me">'+
      '<img class="ll-av" src="'+AVATAR+'" alt="默认头像">'+
      '<span class="ll-name '+st+'" title="'+st+'">'+esc(label)+'</span>'+extra+bubble+
      '<button class="ll-btn" id="ll-login">'+(s?"账户":"登录")+'</button>'+
      '<button class="ll-btn" id="ll-set" title="设置 API 与 token">设置</button>'+
    '</div></div>';
  document.body.insertBefore(bar,document.body.firstChild);
  $("#ll-login").onclick=loginDialog;
  $("#ll-set").onclick=settingsDialog;
}
function dialog(inner){
  var m=document.createElement("div"); m.className="ll-mask";
  m.innerHTML='<div class="ll-modal">'+inner+'</div>';
  document.body.appendChild(m);
  m.addEventListener("click",function(e){if(e.target===m) m.remove();});
  return m;
}
/* ---------- 用户自担确认门（第 11 条口径） ----------
   写操作 / 借账号操作前必须让用户自己看清后果、自己确认、自己承担。
   这是「明示同意 + 责任划分」，不是安全边界（纯前端可绕过；真鉴权仍靠 token）。
   默认每次确认；用户可主动勾选「本次会话不再重复」，责任仍归用户。 */
function sha256(t){
  /* 轻量非加密摘要，仅用于审计留痕标识；不是完整性签名 */
  var h=0,i,c; t=String(t||"");
  for(i=0;i<t.length;i++){c=t.charCodeAt(i);h=((h<<5)-h+c)|0;}
  return ("00000000"+(h>>>0).toString(16)).slice(-8);
}
function confirmAction(o, onOk){
  /* o: {kind, target, account, traces, detail} */
  if(sessionStorage.getItem("ll:confirm_once")==="1"){
    audit(o,"会话内已确认"); onOk(); return;
  }
  var acct=o.account||"你自己的洛谷账号（个人账号，非本人）";
  var traces=o.traces||"在洛谷留下公开可见的记录";
  var m=dialog('<h3>⚠ 请自己确认后果</h3>'+
    '<div class="ll-note" style="border-left-color:var(--ll-bad);background:#fdeeea;color:#7a3527">'+
      '即将执行 <b>'+esc(o.kind)+'</b>。此动作<b>使用'+esc(acct)+'</b>，'+
      esc(traces)+'。可能触发平台风控、限流乃至账号封禁；'+
      '内容的版权与合规责任亦由你承担。<b>后果全部由你自行承担。</b></div>'+
    '<table class="ll-tb"><tbody>'+
      '<tr><th>动作</th><td>'+esc(o.kind)+'</td></tr>'+
      '<tr><th>目标</th><td>'+esc(o.target||"—")+'</td></tr>'+
      '<tr><th>账号</th><td>'+esc(acct)+'</td></tr>'+
      '<tr><th>平台痕迹</th><td>'+esc(traces)+'</td></tr>'+
      '<tr><th>内容摘要</th><td><code>'+esc(sha256(o.detail))+'</code>（仅本地留痕）</td></tr>'+
    '</tbody></table>'+
    '<label style="display:flex;gap:7px;align-items:center;margin-top:10px;font-size:13px">'+
      '<input type="checkbox" id="ll-agree"> 我已阅读并<b>自行承担全部后果</b></label>'+
    '<label style="display:flex;gap:7px;align-items:center;margin-top:6px;font-size:13px">'+
      '<input type="checkbox" id="ll-once"> 本次会话内不再重复确认（责任仍由我承担）</label>'+
    '<label style="font-size:12px;color:var(--ll-mute);display:block;margin-top:9px">'+
      '输入 <code>我自担</code> 以确认</label>'+
    '<input id="ll-word" placeholder="我自担" autocomplete="off">'+
    '<div class="ll-msg" id="ll-conf-msg"></div>'+
    '<div class="row"><button class="ll-btn" id="ll-conf-no">取消</button>'+
    '<button class="ll-btn pri" id="ll-conf-yes">我已确认，执行</button></div>');
  $("#ll-conf-no",m).onclick=function(){m.remove();};
  $("#ll-conf-yes",m).onclick=function(){
    var ok=$("#ll-agree",m).checked, w=$("#ll-word",m).value.trim();
    if(!ok||w!=="我自担"){$("#ll-conf-msg",m).textContent="需勾选并输入「我自担」";return;}
    if($("#ll-once",m).checked) sessionStorage.setItem("ll:confirm_once","1");
    audit(o,"用户已确认自担"); m.remove(); onOk();
  };
}
function audit(o,result){
  var a=get(K.audit,[]);
  a.push({ts:ts(),kind:o.kind,target:o.target||"",hash:sha256(o.detail),
          account:o.account||"个人账号",result:result});
  set(K.audit,a.slice(-200));
  console.log("[本地 luogu] 自担审计留痕",a[a.length-1]);
}

function loginDialog(){
  var s=session()||{};
  var m=dialog('<h3>登录 · 本地优先</h3>'+
    '<div class="ll-note">账号等隐私信息<b>只存浏览器本地</b>，子页面不重复登录；'+
    '不写入仓库。用 cookie 时手机号 / uid 等标识不显示。</div>'+
    '<label>方式</label><select id="ll-mode">'+
      '<option value="cookie"'+(s.mode==="cookie"?" selected":"")+'>cookie</option>'+
      '<option value="password"'+(s.mode==="password"?" selected":"")+'>账密</option></select>'+
    '<label>用户名（联网时可从洛谷取，无网用缓存）</label><input id="ll-name" value="'+esc(s.name||"")+'" placeholder="留空则显示「已登录」">'+
    '<label>uid / 手机号（可选；cookie 方式不显示）</label><input id="ll-uid" value="'+esc(s.uid||"")+'">'+
    '<label>牌子 / 气泡（可选，有才渲染）</label><input id="ll-badge" value="'+esc(s.badge||"")+'">'+
    '<label>cookie 或 密码（仅本地）</label><input id="ll-secret" type="password" value="'+esc(s.secret||"")+'">'+
    '<div class="row"><button class="ll-btn" id="ll-out">退出</button>'+
    '<button class="ll-btn" id="ll-cancel">取消</button>'+
    '<button class="ll-btn pri" id="ll-save">保存到本地</button></div>');
  $("#ll-out",m).onclick=function(){localStorage.removeItem(K.sess);m.remove();location.reload();};
  $("#ll-cancel",m).onclick=function(){m.remove();};
  $("#ll-save",m).onclick=function(){
    var mode=$("#ll-mode",m).value, sec=$("#ll-secret",m).value;
    set(K.sess,{mode:mode,name:$("#ll-name",m).value.trim(),
      uid:$("#ll-uid",m).value.trim(),badge:$("#ll-badge",m).value.trim(),
      secret:sec,logged:true,ts:ts()});
    m.remove(); toast("已保存到本地（未联网、未回推）","ok"); location.reload();
  };
}
function settingsDialog(){
  var m=dialog('<h3>设置 · 只认 token 不认人</h3>'+
    '<div class="ll-note">留空 <b>apiBase</b> 时全站<b>零网络请求</b>：'+
    '评论、投稿、登录全部走本地。填了才按 <code>api/API契约.md</code> 调用。</div>'+
    '<label>apiBase（如 http://127.0.0.1:8765）</label><input id="ll-api" value="'+esc(apiBase())+'">'+
    '<label>token（Bearer；只存本地，不进仓库）</label><input id="ll-token" type="password" value="'+esc(tok())+'">'+
    '<label>回推 luogu.com.cn 适配器（发文）</label><select id="ll-pub">'+
      '<option value="0"'+(get(K.pub,false)?"":" selected")+'>关闭（默认）</option>'+
      '<option value="1"'+(get(K.pub,false)?" selected":"")+'>仅登录+联网+显式启用时</option></select>'+
    '<label>评论持久化 · 直接推洛谷</label><select id="ll-push">'+
      '<option value="0"'+(get(K.push,false)?"":" selected")+'>关闭（仅本地，默认）</option>'+
      '<option value="1"'+(get(K.push,false)?" selected":"")+'>本地先存 + 待推队列 → 个人账号低频推洛谷</option></select>'+
    '<label>洛谷 IDE 入口（用你的账号真编译）</label>'+
    '<input id="ll-ide-url" value="'+esc(get(K.ideUrl,"https://www.luogu.com/ide"))+'" placeholder="https://www.luogu.com/ide">'+
    '<label>洛谷题目提交页模板（{pid} 会被替换）</label>'+
    '<input id="ll-sub-url" value="'+esc(get(K.subUrl,"https://www.luogu.com/problem/{pid}"))+'">'+
    '<div class="ll-note"><b>静态站绝不直连洛谷</b>：跨源 + HttpOnly cookie + CSRF 使浏览器直推不可达。'+
    '评论/发文交给 <code>/api/comments/push-luogu</code> 等适配器；'+
    '<b>真编译则新窗口打开洛谷 IDE</b>（洛谷域下、你的登录态自然生效），代码走剪贴板粘贴。'+
    '入口按你所在网络自行确认，不编造内部 API。当前出口无法访问外部域名，默认关闭。</div>'+
    '<div class="ll-note"><b>运行态自己加 / 自己下载</b>：静态站只是壳，'+
    'GitHub Actions runner 就是现成运行态，也可本机跑 <code>tools/luogu_submit.py</code>。'+
    '评论 / 发文 / 洛谷 IDE 评测先本地入队 → 「导出待推队列」→ 放进 '+
    '<code>site/data/outbox/</code> → push → 手动跑「代提交 luogu」工作流并输入确认值。'+
    '凭据填在仓库 Settings → Secrets（<code>LUOGU_COOKIE / LUOGU_CSRF / LUOGU_UID / '+
    'LUOGU_SUBMIT_ENDPOINT</code>），<b>不进仓库</b>；端点按洛谷当前页面填写，不编造。</div>'+
    '<div class="ll-note" style="border-left-color:var(--ll-bad);background:#fdeeea;color:#7a3527">'+
    '<b>后果自担</b>：任何写操作 / 借账号动作都会先弹确认门，由你自己确认并承担全部后果；'+
    '默认每次确认，你也可主动选择会话内不再提示。</div>'+
    '<div class="row"><button class="ll-btn" id="ll-audit">查看本地审计</button>'+
    '<button class="ll-btn" id="ll-cancel">取消</button>'+
    '<button class="ll-btn pri" id="ll-save">保存</button></div>');
  $("#ll-cancel",m).onclick=function(){m.remove();};
  $("#ll-audit",m).onclick=function(){
    var a=get(K.audit,[]);
    toast(a.length?("本地审计 "+a.length+" 条，最近："+a[a.length-1].kind+" / "+a[a.length-1].result):"暂无审计记录");
  };
  $("#ll-save",m).onclick=function(){
    set(K.api,$("#ll-api",m).value.trim()); set(K.token,$("#ll-token",m).value.trim());
    set(K.pub,$("#ll-pub",m).value==="1"); set(K.push,$("#ll-push",m).value==="1");
    set(K.ideUrl,$("#ll-ide-url",m).value.trim()); set(K.subUrl,$("#ll-sub-url",m).value.trim());
    m.remove();
    toast("已保存；页面仍不主动发请求","ok"); location.reload();
  };
}

/* ---------- Markdown（自写，先转义再解析，防 XSS） ---------- */
function md(src){
  var t=esc(src||""), blocks=[];
  t=t.replace(/```([\s\S]*?)```/g,function(_,c){blocks.push(c);return "\u0000B"+(blocks.length-1)+"\u0000";});
  t=t.replace(/`([^`\n]+)`/g,function(_,c){return "<code>"+c+"</code>";});
  t=t.replace(/^### (.+)$/gm,"<h3>$1</h3>").replace(/^## (.+)$/gm,"<h2>$1</h2>")
     .replace(/^# (.+)$/gm,"<h1>$1</h1>");
  t=t.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/\*([^*\n]+)\*/g,"<em>$1</em>");
  /* 链接：仅 http(s) 与相对锚点，javascript: 会被转义后不匹配 */
  t=t.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|#[^\s)]*)\)/g,
    function(_,a,u){return '<a href="'+u+'" rel="noopener" referrerpolicy="no-referrer">'+a+"</a>";});
  t=t.replace(/^&gt; (.+)$/gm,"<blockquote>$1</blockquote>");
  t=t.split(/\n{2,}/).map(function(p){
    if(/^<(h\d|blockquote|pre)/.test(p)||/^\u0000B/.test(p)) return p;
    if(/^\s*[-*] /m.test(p)) return "<ul>"+p.replace(/^\s*[-*] (.+)$/gm,"<li>$1</li>")+"</ul>";
    if(/^\s*\d+\. /m.test(p)) return "<ol>"+p.replace(/^\s*\d+\. (.+)$/gm,"<li>$1</li>")+"</ol>";
    return p.trim()?"<p>"+p.replace(/\n/g,"<br>")+"</p>":"";
  }).join("\n");
  t=t.replace(/\u0000B(\d+)\u0000/g,function(_,i){
    return "<pre><code>"+blocks[+i]+"</code></pre>";});
  return t;
}

/* ---------- 验证码（纯前端算术，明示非安全边界） ---------- */
function captcha(host){
  var a=1+Math.floor(Math.random()*8), b=1+Math.floor(Math.random()*8);
  sessionStorage.setItem("ll:cap",String(a+b));
  var box=document.createElement("div"); box.className="ll-captcha";
  box.innerHTML='<span class="q">'+a+" + "+b+" = ?</span>"+
    '<input type="text" inputmode="numeric" placeholder="答案" maxlength="3">'+
    '<button class="ll-btn" id="ll-refresh">换一题</button>'+
    '<span class="hint">算术验证码仅防误触，真鉴权靠 token</span>';
  host.appendChild(box);
  $("#ll-refresh",box).onclick=function(){box.remove();captcha(host);};
  return function(){return $("input",box).value.trim()===sessionStorage.getItem("ll:cap");};
}

/* ---------- 待推队列 → outbox（喂给 GitHub Action） ----------
   运行态由使用者自行添加 / 下载：这里只导出，不碰洛谷、不持凭据。 */
function exportOutbox(lid){
  var q=get(K.pq,[]), list=get(K.cmt+lid,[]);
  var extra=list.filter(function(c){return c.state!=="已推洛谷";}).map(function(c){
    return {id:c.id||("c"+Date.now()+Math.floor(Math.random()*999)),kind:"comment",
            lid:lid,text:c.text,confirmed:true,state:"本地已存 · 待推",created_at:ts()};
  });
  var seen={}, out=[];
  q.concat(extra).forEach(function(x){
    if(!x || !x.id || seen[x.id]) return;
    seen[x.id]=1;
    out.push({id:x.id,kind:x.kind||"comment",lid:x.lid||lid,pid:x.pid||"",
              text:x.text||"",code:x.code||"",lang:x.lang||"",
              confirmed:true,state:"本地已存 · 待推",created_at:x.created_at||ts()});
  });
  if(!out.length){toast("待推队列为空","ok");return;}
  confirmAction({
    kind:"导出 "+out.length+" 条待推内容，交给 GitHub Action 代提交 luogu",
    target:"site/data/outbox/ · workflow: 代提交 luogu",
    traces:"导出本身只下载到本地文件，不发起任何请求；真正提交发生在你手动跑 Action 并输入确认值之后",
    detail:out.length+" 条 / "+lid
  },function(){
    var blob=new Blob([JSON.stringify(out,null,1)],{type:"application/json;charset=utf-8"});
    var u=URL.createObjectURL(blob), a=document.createElement("a");
    a.href=u; a.download="outbox-"+new Date().toISOString().slice(0,10).replace(/-/g,"")+".json";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function(){URL.revokeObjectURL(u);},1000);
    toast("已导出 "+out.length+" 条：放进 site/data/outbox/ 后 push，再手动跑 Action","ok");
  });
}

/* ---------- 评论 ---------- */
function comments(lid){
  var host=$("#ll-comments"); if(!host) return;
  var key=K.cmt+lid, list=get(key,[]);
  function render(){
    var nPushed=list.filter(function(c){return c.state==="已推洛谷";}).length;
    var nWait=list.length-nPushed;
    var h='<h2>评论 <span class="ll-pill">'+list.length+'</span></h2>'+
      '<div class="ll-note">支持 Markdown 在线渲染（内置解析器，无 CDN）。'+
      '<b>评论持久化 = 直接推洛谷</b>：本地先存离线副本（'+nWait+' 条待推 / '+nPushed+
      ' 条已推），待推项交给外部执行端用<b>个人账号</b>低频推送；'+
      '静态站不直连洛谷。未开启或未配置 apiBase 时纯本地、零请求。</div><div id="ll-cm-list"></div>';
    host.innerHTML=h;
    var exp=document.createElement("button"); exp.className="ll-btn";
    exp.textContent="导出待推队列（给 Action 用）"; exp.style.margin="0 0 10px 0";
    exp.onclick=function(){ exportOutbox(lid); };
    host.insertBefore(exp, host.querySelector("#ll-cm-list").nextSibling);
    var box=$("#ll-cm-list",host);
    if(!list.length){box.innerHTML='<p class="ll-empty">还没有评论。</p>';}
    list.forEach(function(c){
      var d=document.createElement("div"); d.className="ll-cm-item";
      var st=c.state||"本地已存";
      var pill=st==="已推洛谷"?'<span class="ll-pill" style="background:#eaf7ef;color:#2fa36b">已推洛谷</span>'
              :st==="失败待重试"?'<span class="ll-pill" style="background:#fdeeea;color:#d9634f">失败待重试</span>'
              :'<span class="ll-pill">本地已存 · 待推</span>';
      d.innerHTML='<div class="ll-cm-head"><b>'+esc(c.who)+"</b><span>"+esc(c.ts)+
        "</span>"+pill+'</div><div class="ll-md">'+md(c.text)+"</div>";
      box.appendChild(d);
    });
    var ta=document.createElement("textarea");
    ta.rows=4; ta.placeholder="写点什么… 支持 **粗体**、`代码`、```代码块```、> 引用、列表与链接";
    ta.style.cssText="width:100%;box-sizing:border-box;border:1px solid var(--ll-line);border-radius:8px;padding:9px;font:inherit";
    host.appendChild(ta);
    var msg=document.createElement("div"); msg.className="ll-msg"; host.appendChild(msg);
    var check=captcha(host);
    var btn=document.createElement("button"); btn.className="ll-btn pri"; btn.textContent="发表评论";
    btn.onclick=function(){
      if(!check()){msg.textContent="验证码不对，换一题再试";return;}
      var v=ta.value.trim(); if(!v){msg.textContent="内容为空";return;}
      var s=session(), who=(s&&(s.name||"已登录"))||"本地用户";
      var c={who:who,text:v,ts:ts(),lid:lid,state:"本地已存",id:"c"+Date.now(),
             kind:"comment",confirmed:false,created_at:ts()};
      list.push(c); set(key,list);
      /* 评论持久层 = 洛谷。静态站绝不 fetch luogu.com：
         跨源 + HttpOnly/SameSite cookie + CSRF 使浏览器直推不可达。
         只把「待推」交给能出网且持有用户个人账号登录态的一端。 */
      if(get(K.push,false) && apiBase() && online()){
        confirmAction({
          kind:"把评论推送到洛谷文章评论区",
          target:lid+" · www.luogu.com/article/"+lid,
          traces:"生成一条公开评论，任何人可见；可能触发洛谷风控 / 限流 / 封号",
          detail:v
        },function(){
          c.confirmed=true; set(key,list);
          var q=get(K.pq,[]); q.push(c); set(K.pq,q);
          call("/api/comments/push-luogu",{method:"POST",body:JSON.stringify({lid:lid,comment:c})})
            .then(function(r){
              if(r && (r.pushed===true || r.state==="已推洛谷")){
                c.state="已推洛谷"; set(key,list); render(); toast("已推洛谷","ok");
              }else if(r && r.error){ c.state="失败待重试"; set(key,list); render(); }
              /* r.queued 只表示已入队，状态仍为「待推」，不谎报已推送 */
            });
        });
      }
      ta.value=""; msg.textContent=""; render(); toast("已本地保存"+(get(K.push,false)?"，已入待推队列":""),"ok");
    };
    host.appendChild(btn);
  }
  render();
}

/* ---------- 按需图片：只登记引用，绝不自动抓取 ---------- */
function lazyImages(){
  var seen=get(K.imgs,{}), n=0;
  $$("img[data-ll-src]").forEach(function(im){
    var u=im.getAttribute("data-ll-src"); n++;
    if(!seen[u]) seen[u]={first_seen:ts(),owner:location.pathname};
    /* 不设置 src，不发请求；仅显示占位说明 */
    im.alt=im.alt||"图片（按需抓取，未缓存）";
  });
  if(n) set(K.imgs,seen);
  return n;
}

/* ---------- 主页区块 ---------- */
function home(){
  var host=$("#ll-home"); if(!host) return;
  var A=(window.LL_ARTICLES||[]);
  var recent=A.slice(0,6).map(function(a){
    return '<li><a href="'+esc(a.page)+'">'+esc(a.problem)+" · "+esc(a.lid)+"</a> "+
      '<span class="ll-pill">'+esc(a.class)+"</span></li>";}).join("");
  var probs={}; A.forEach(function(a){probs[a.problem]=1;});
  var plist=Object.keys(probs).slice(0,8).map(function(p){
    return '<a class="ll-pill" href="problems.html#pid='+esc(p)+'">'+esc(p)+"</a>";}).join(" ");
  var notices=get("ll:notices",[]);
  host.innerHTML=
    '<section class="ll-sec"><h2>最近文章</h2><div class="ll-card"><ul class="ll-list">'+
      (recent||'<li class="ll-empty">暂无</li>')+'</ul></div></section>'+
    '<div class="ll-cols">'+
      '<section class="ll-sec"><h2>题目</h2><div class="ll-card">'+
        (plist||'<span class="ll-empty">暂无</span>')+
        '<p class="ll-empty" style="margin-top:8px">进 <a href="problems.html">题目 / IDE</a> 看附件与本地评测</p>'+
      '</div></section>'+
      '<section class="ll-sec"><h2>公告（自己的）</h2><div class="ll-card">'+
        (notices.length?'<ul class="ll-list">'+notices.map(function(x){return "<li>"+esc(x)+"</li>";}).join("")+"</ul>"
          :'<span class="ll-empty">暂无公告 · 有则渲染，没有不添加</span>')+'</div></section>'+
      '<section class="ll-sec"><h2>比赛</h2><div class="ll-card">'+
        '<span class="ll-empty">暂无比赛数据 · 不硬造、不添加未获取的元素</span></div></section>'+
      '<section class="ll-sec"><h2>犇犇</h2><div class="ll-card">'+
        '<span class="ll-empty">暂无犇犇 · 次要元素有则渲染，没有不必添加</span></div></section>'+
    '</div>';
}

/* ---------- IDE / 本地评测 ---------- */
var TPL={
 "C++":'#include <bits/stdc++.h>\nusing namespace std;\nint main(){\n    \n    return 0;\n}\n',
 "Python":'import sys\n\ndef main():\n    pass\n\nif __name__ == "__main__":\n    main()\n',
 "C":'#include <stdio.h>\nint main(){\n    \n    return 0;\n}\n'
};
function ide(){
  var host=$("#ll-ide"); if(!host) return;
  var cases=window.LL_JUDGE_CASES||[];
  var pid=(location.hash.match(/pid=(P\d+)/)||[])[1]||"";
  host.innerHTML='<div class="ll-ide"><div class="ll-ide-bar">'+
    '<b>IDE 模式</b><select id="ll-lang"><option>C++</option><option>Python</option><option>C</option></select>'+
    '<input id="ll-pid" value="'+esc(pid)+'" placeholder="题号 如 P1001" style="width:110px">'+
    '<button class="ll-btn" id="ll-tpl">载入模板</button>'+
    '<button class="ll-btn" id="ll-copy">复制代码</button>'+
    '<button class="ll-btn pri" id="ll-submit">本地入队</button>'+
    '<button class="ll-btn" id="ll-luogu-ide" title="联网+已登录时，用你的账号在洛谷 IDE 真编译">洛谷 IDE 真编译</button>'+
    '<button class="ll-btn" id="ll-luogu-sub" title="用你的账号提交到洛谷评测">提交洛谷评测</button>'+
    '<span class="hint">仅 C++ / Python / C（最终要求：无额外语言）</span></div>'+
    '<div class="ll-editor"><div class="ll-ln" id="ll-ln">1</div>'+
    '<textarea id="ll-code" spellcheck="false"></textarea></div></div>'+
    '<div class="ll-judge"><h2>本地评测（无网 · 与库中 std 期望输出对照）</h2>'+
    '<div class="ll-note"><b>真编译 = 借洛谷 IDE，用你自己的账号</b>（第 10 条口径）：'+
    '要求你<b>联网且已登录洛谷</b>，点按钮后会<b>新窗口打开洛谷域下的 IDE</b>——'+
    '在洛谷域里你的会话自然生效，不受跨源限制；代码走剪贴板粘贴，静态站不碰你的账号、'+
    '不调洛谷内部 API。后果由你自己在确认门里承担。'+
    '<br>离线兜底：下面仍可用库中 <code>site/data/judge_cases.json</code> 的 std 期望输出做对照。</div>'+
    '<select id="ll-case" style="border:1px solid var(--ll-line);border-radius:8px;padding:6px 9px">'+
      '<option value="">选择测试点</option>'+
      cases.map(function(c,i){return '<option value="'+i+'">'+esc(c.label||("用例 "+(i+1)))+"</option>";}).join("")+
    '</select> <input id="ll-out" placeholder="粘贴你的程序输出" style="border:1px solid var(--ll-line);border-radius:8px;padding:6px 9px;width:240px">'+
    ' <button class="ll-btn" id="ll-check">对照</button><div id="ll-verdict"></div></div>';
  var code=$("#ll-code",host), ln=$("#ll-ln",host);
  function lines(){var n=code.value.split("\n").length,a=[];for(var i=1;i<=n;i++)a.push(i);ln.innerHTML=a.join("<br>");}
  code.addEventListener("input",lines); code.addEventListener("scroll",function(){ln.scrollTop=code.scrollTop;});
  $("#ll-lang",host).onchange=function(){code.value=TPL[this.value];lines();};
  $("#ll-tpl",host).onclick=function(){code.value=TPL[$("#ll-lang",host).value];lines();};
  code.value=TPL["C++"]; lines();
  $("#ll-submit",host).onclick=function(){
    var payload={pid:$("#ll-pid",host).value.trim(),lang:$("#ll-lang",host).value,code:code.value,ts:ts()};
    var q=get("ll:judge_q",[]); q.push(payload); set("ll:judge_q",q);
    /* 仅配置后外发 */
    if(apiBase()) call("/api/judge",{method:"POST",body:JSON.stringify(payload)});
    toast("已本地入队（未联网提交）","ok");
  };
  /* 复制代码（用户主动动作，零请求） */
  $("#ll-copy",host).onclick=function(){
    if(navigator.clipboard) navigator.clipboard.writeText(code.value)
      .then(function(){toast("代码已复制","ok");});
    else toast("浏览器不支持剪贴板，请手动选中复制");
  };
  /* 借洛谷 IDE 真编译：新窗口打开洛谷域 + 剪贴板；不跨域 fetch、不碰登录态 */
  function luoguRun(kind,urlTpl){
    var pid=$("#ll-pid",host).value.trim()||"P1001";
    var url=(urlTpl||"").replace("{pid}",encodeURIComponent(pid));
    if(!/^https?:\/\/(www\.)?luogu\.(com|com\.cn|org)\//i.test(url)){
      toast("请先在「设置」里填写洛谷域下的 IDE / 提交页入口","no"); return;
    }
    confirmAction({
      kind:kind, target:url,
      account:"你自己的洛谷账号（联网且已登录；非低频检索账号）",
      traces:"在洛谷 IDE 运行 / 产生一次提交记录，可能触发风控、限流或封号；代码内容责任由你承担",
      detail:code.value
    },function(){
      if(navigator.clipboard) navigator.clipboard.writeText(code.value);
      var w=window.open(url,"_blank","noopener,noreferrer");
      if(!w) toast("浏览器拦截了新窗口；请允许后重试","no");
      else toast("已打开洛谷域页面；代码已复制，粘贴后运行","ok");
    });
  }
  $("#ll-luogu-ide",host).onclick=function(){
    luoguRun("用洛谷 IDE 真编译",get(K.ideUrl,"https://www.luogu.com/ide"));
  };
  $("#ll-luogu-sub",host).onclick=function(){
    luoguRun("提交到洛谷评测",get(K.subUrl,"https://www.luogu.com/problem/{pid}"));
  };

  $("#ll-check",host).onclick=function(){
    var i=$("#ll-case",host).value, out=$("#ll-out",host).value.trim(), v=$("#ll-verdict",host);
    if(i===""){v.innerHTML='<div class="ll-verdict no">请先选测试点</div>';return;}
    var c=cases[+i], exp=String(c.expect==null?c.output:c.expect).trim();
    var okc=(out===exp);
    v.innerHTML='<div class="ll-verdict '+(okc?"ok":"no")+'">'+(okc?"一致 ✓":"不一致 ✗")+
      '</div><div class="ll-note">期望：<code>'+esc(exp)+"</code>　你的输出：<code>"+esc(out||"(空)")+
      "</code>　来源："+esc(c.source||"库中 std 对照表")+"</div>";
  };
  /* 已知 hack 入口 */
  var hk=$("#ll-hacks");
  if(hk && cases.length){
    hk.innerHTML='<h2>已知 hack（讨论区 / 工单题解）</h2><table class="ll-tb"><thead><tr>'+
      '<th>题解</th><th>代表输入</th><th>期望 → 实际</th></tr></thead><tbody>'+
      cases.slice(0,8).map(function(c){return "<tr><td>"+esc(c.lid||"—")+"</td><td><code>"+
        esc(c.input||"—")+"</code></td><td>"+esc(c.hack||c.note||"—")+"</td></tr>";}).join("")+
      "</tbody></table>";
  }
}

/* ---------- 编译环境（内置下载功能，不甩裸链） ---------- */
function mirrors(){
  var host=$("#ll-mirrors"); if(!host) return;
  var ms=window.LL_MIRRORS||[];
  host.innerHTML='<h2>编译环境 · 内置下载</h2><div class="ll-note">'+
    '无网时提供国内易联、速度快的地址，<b>内置为功能</b>而非直接甩网址：'+
    '可选、一键复制、主动点击才探测。镜像清单由你按所在网络维护，'+
    '仓库只存结构与检测逻辑，<b>不写死可能失效的第三方地址</b>。</div>'+
    (ms.length?ms.map(function(m,i){return '<div class="ll-mirror">'+
      '<span class="ll-pill">'+esc(m.lang||"通用")+'</span>'+
      '<code>'+esc(m.url||"（未填写）")+'</code>'+
      '<span class="ll-empty">'+esc(m.note||"")+'</span>'+
      '<button class="ll-btn" data-copy="'+i+'">复制</button>'+
      '<button class="ll-btn" data-probe="'+i+'">探测可达性</button>'+
      '<span id="ll-probe-'+i+'"></span></div>';}).join("")
      :'<p class="ll-empty">清单为空：在 <code>site/data/mirrors.js</code> 里按结构补充你所在网络可达的地址。</p>');
  $$("[data-copy]",host).forEach(function(b){b.onclick=function(){
    var u=ms[+b.getAttribute("data-copy")].url||"";
    if(navigator.clipboard) navigator.clipboard.writeText(u).then(function(){toast("已复制","ok");});
    else toast("浏览器不支持剪贴板，请手动选中复制");
  };});
  $$("[data-probe]",host).forEach(function(b){b.onclick=function(){
    var i=+b.getAttribute("data-probe"), u=ms[i].url, out=$("#ll-probe-"+i,host);
    if(!u){out.textContent="未填写地址";return;}
    if(!apiBase()){out.textContent="未配置 apiBase：不发起任何请求（零外网约束）";return;}
    /* 唯一可能的网络动作，且必须用户主动点击 */
    out.textContent="探测中…";
    fetch(u,{method:"HEAD",mode:"no-cors"}).then(function(){out.textContent="可达（no-cors 仅供参考）";})
      .catch(function(){out.textContent="不可达或被跨域策略拦截";});
  };});
}

/* ---------- std 工单投稿 ---------- */
function submit(){
  var host=$("#ll-submit"); if(!host) return;
  var q=get(K.std,[]);
  host.innerHTML='<h2>std 工单（投稿）</h2>'+
    '<div class="ll-flow"><span>投稿</span><i>→</i><span>与原 std 对跑比较</span><i>→</i>'+
    '<span>去除 WA</span><i>→</i><span>去除不优</span><i>→</i><span>添入可选项</span><i>→</i>'+
    '<span>人工审核无错</span><i>→</i><span>迁入 std</span></div>'+
    '<div class="ll-note">取不到官方数据，正确性以 <b>std 对拍</b>为准。'+
    '真对跑在 <code>tools/</code> 本地执行；脚本<b>不自动迁入</b>。</div>'+
    '<label style="font-size:12px;color:var(--ll-mute)">题号</label>'+
    '<input id="ll-s-pid" placeholder="P1001" style="border:1px solid var(--ll-line);border-radius:8px;padding:7px 9px">'+
    '<label style="font-size:12px;color:var(--ll-mute);display:block;margin-top:8px">代码 / 说明</label>'+
    '<textarea id="ll-s-body" rows="7" style="width:100%;box-sizing:border-box;border:1px solid var(--ll-line);border-radius:8px;padding:9px;font:inherit"></textarea>'+
    '<div style="margin-top:9px"><button class="ll-btn pri" id="ll-s-go">提交工单（本地入队）</button></div>'+
    '<h3 style="margin-top:18px">队列</h3><div id="ll-s-list"></div>';
  function render(){
    var box=$("#ll-s-list",host);
    if(!q.length){box.innerHTML='<p class="ll-empty">队列为空</p>';return;}
    box.innerHTML='<table class="ll-tb"><thead><tr><th>题号</th><th>状态</th><th>时间</th></tr></thead><tbody>'+
      q.map(function(x){return "<tr><td>"+esc(x.pid)+"</td><td><span class=\"ll-state wait\">"+
        esc(x.state||"待对跑")+"</span></td><td>"+esc(x.ts)+"</td></tr>";}).join("")+"</tbody></table>";
  }
  render();
  $("#ll-s-go",host).onclick=function(){
    var pid=$("#ll-s-pid",host).value.trim(), body=$("#ll-s-body",host).value.trim();
    if(!pid||!body){toast("题号和内容都要填","no");return;}
    var item={pid:pid,body:body,state:"待对跑",ts:ts()};
    q.push(item); set(K.std,q);
    if(apiBase()){
      confirmAction({kind:"把 std 投稿同步到外部队列",target:"apiBase /api/std/submit",
        traces:"产生一条投稿记录，后续可能被审核并公开；后果由你承担",detail:body},
        function(){call("/api/std/submit",{method:"POST",body:JSON.stringify(item)});});
    }
    $("#ll-s-body",host).value=""; render(); toast("已本地入队","ok");
  };
}

/* ---------- 本人（只认 token 不认人） ---------- */
function selfPanel(){
  var host=$("#ll-self"); if(!host) return;
  var ops=window.LL_SELF||[], A=window.LL_ARTICLES||[];
  var rw=!!tok();
  host.innerHTML='<h2>本地操作面板</h2>'+
    '<div class="ll-note"><b>只认 token 不认人</b>：服务端只校验 '+
    '<code>Authorization: Bearer &lt;token&gt;</code>，不校验自然人。'+
    (rw?'当前已配置 token → <b>可写</b>':'未配置 token → <b>只读</b>，不会误删')+'。</div>'+
    '<div style="margin:10px 0"><input id="ll-q" placeholder="按 uid 或 用户名 search" '+
      'style="border:1px solid var(--ll-line);border-radius:8px;padding:7px 10px;width:260px">'+
    ' <button class="ll-btn" id="ll-search">搜索</button></div>'+
    '<div id="ll-self-list"></div>'+
    '<div class="ll-note" style="margin-top:14px">用户名搜不到时，可在洛谷评论里用 <code>@</code> 搜索'+
    '（低频、无风险、仅必需时使用 <code>本人低频检索账号</code>）。</div>'+
    '<h3 style="margin-top:18px">资源（删资源需 token）</h3><div id="ll-res"></div>';
  function renderAdm(f){
    var list=ops.filter(function(a){return !f||(a.id||"").indexOf(f)>=0||(a.role||"").indexOf(f)>=0;});
    $("#ll-self-list",host).innerHTML='<table class="ll-tb"><thead><tr><th>标识</th><th>用途</th><th>约束</th></tr></thead><tbody>'+
      (list.length?list.map(function(a){return "<tr><td><code>"+esc(a.id)+"</code></td><td>"+
        esc(a.role)+"</td><td>"+esc(a.constraint||"")+"</td></tr>";}).join("")
        :'<tr><td colspan="3" class="ll-empty">无匹配</td></tr>')+"</tbody></table>";
  }
  function renderRes(f){
    var list=A.filter(function(a){return !f||(a.lid||"").indexOf(f)>=0||(a.problem||"").indexOf(f)>=0;}).slice(0,12);
    $("#ll-res",host).innerHTML='<table class="ll-tb"><thead><tr><th>编号</th><th>题号</th><th>归类</th><th>操作</th></tr></thead><tbody>'+
      list.map(function(a){return "<tr><td>"+esc(a.lid)+"</td><td>"+esc(a.problem)+"</td><td>"+
        esc(a.class)+'</td><td><button class="ll-btn" data-del="'+esc(a.lid)+'" '+(rw?"":"disabled")+'>删除</button></td></tr>';}).join("")+
      "</tbody></table>";
    $$("[data-del]",host).forEach(function(b){b.onclick=function(){
      if(!tok()){toast("未配置 token，只读","no");return;}
      var id=b.getAttribute("data-del");
      confirmAction({kind:"删除归档资源",target:id,
        traces:"本地与线上数据源同步删除该条目，仅保留「已移除」审计；不可恢复，后果由你承担",
        detail:id},function(){
        if(apiBase()) call("/api/resources/"+encodeURIComponent(id),{method:"DELETE"});
        toast("已提交删除（本地不直接删归档）","ok");
      });
    };});
  }
  renderAdm(""); renderRes("");
  $("#ll-search",host).onclick=function(){
    var f=$("#ll-q",host).value.trim(); renderAdm(f); renderRes(f);
    if(f && apiBase()) call("/api/search?name="+encodeURIComponent(f));
  };
}

/* ---------- 页面路由 ---------- */
function page(){
  var p=document.body.getAttribute("data-page");
  if(!p){
    if(/articles\//.test(location.pathname)) p="article";
    else if($("#groups")) p="home";
    else if($("#ll-ide")) p="problems";
    else if($("#ll-submit")) p="submit";
    else if($("#ll-self")) p="self";
    else p="doc";
  }
  return p;
}
function boot(){
  document.body.classList.add("ll");
  chrome();
  var imgs=lazyImages();
  var p=page();
  if(p==="home") home();
  if(p==="article"){
    var lid=(location.pathname.match(/articles\/([a-z0-9]{8})\.html/)||[])[1]||"unknown";
    if(!$("#ll-comments")){
      var box=document.createElement("div"); box.id="ll-comments"; box.className="ll-cm wrap";
      var main=$("main.article")||$("main.doc")||document.body;
      (main.parentNode||document.body).insertBefore(box,main.nextSibling||null);
    }
    comments(lid);
  }
  if(p==="problems"||$("#ll-ide")) ide();
  if($("#ll-mirrors")) mirrors();
  if(p==="submit"||$("#ll-submit")) submit();
  if(p==="self"||$("#ll-self")) selfPanel();
  if(imgs) console.log("[本地 luogu] 按需图片登记 "+imgs+" 处，未发起抓取");
  console.log("[本地 luogu] page="+p+" | apiBase="+(apiBase()?"已配置":"空(零请求)")+
    " | 加载完成，未发起任何外网请求");
}
if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",boot);
else boot();
window.LL={md:md,call:call,session:session,apiBase:apiBase,token:tok};
})();
