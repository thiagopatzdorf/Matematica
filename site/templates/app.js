/* Filtro e ordenação da tabela de células. Sem JS a tabela continua completa. */
(function(){
  document.documentElement.classList.add('js');
  var t=document.getElementById('tabela');if(!t)return;
  var tb=t.tBodies[0],rows=Array.prototype.slice.call(tb.rows);
  var fq=document.getElementById('f-q'),fe=document.getElementById('f-estado'),
      fa=document.getElementById('f-abertas'),fs=document.getElementById('f-busca'),
      out=document.getElementById('contagem');
  var p=new URLSearchParams(location.search);
  if(p.get('q'))fq.value=p.get('q');if(p.get('estado'))fe.value=p.get('estado');
  function aplicar(){
    var q=fq.value,e=fe.value,a=fa.checked,s=fs.value.trim().toLowerCase(),n=0;
    rows.forEach(function(r){
      var ok=(!q||r.dataset.q===q)&&(!e||r.dataset.estado===e)&&(!a||r.dataset.aberta==='1')&&
             (!s||r.dataset.id.toLowerCase().indexOf(s)>=0);
      r.hidden=!ok;if(ok)n++;
    });
    out.textContent=n+' de '+rows.length+' células';
  }
  [fq,fe,fa].forEach(function(c){c.addEventListener('change',aplicar)});
  fs.addEventListener('input',aplicar);
  var ths=t.tHead.rows[0].cells;
  Array.prototype.forEach.call(ths,function(th,i){
    var b=th.querySelector('button');if(!b)return;
    b.addEventListener('click',function(){
      var asc=b.getAttribute('aria-sort')!=='ascending';
      Array.prototype.forEach.call(t.querySelectorAll('th button'),function(x){x.removeAttribute('aria-sort')});
      b.setAttribute('aria-sort',asc?'ascending':'descending');
      th.setAttribute('aria-sort',asc?'ascending':'descending');
      var num=th.dataset.tipo==='n';
      rows.sort(function(x,y){
        var a=x.cells[i].dataset.v,c=y.cells[i].dataset.v;
        var r=num?(parseFloat(a)-parseFloat(c)):a.localeCompare(c,'pt');
        return (asc?r:-r)||(x.dataset.ord-y.dataset.ord);
      });
      rows.forEach(function(r){tb.appendChild(r)});
    });
  });
  aplicar();
})();
