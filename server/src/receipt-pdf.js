const C={mint:[.91,.97,.93],teal:[.086,.55,.54],navy:[.06,.16,.26],green:[.88,.95,.89],pale:[.965,.98,.97],line:[.84,.90,.87],text:[.19,.30,.34],muted:[.43,.53,.55]};
const rgb=c=>c.map(x=>x.toFixed(3)).join(' ');
const slash=String.fromCharCode(92);
const esc=v=>String(v??'').normalize('NFKD').replace(/[‘’]/g,"'").replace(/[“”]/g,'"').replace(/[–—]/g,'-').replace(/[^\x20-\x7e]/g,' ').replaceAll(slash,slash+slash).replaceAll('(',slash+'(').replaceAll(')',slash+')');
const wrap=(v,n=76)=>{let out=[],line='';for(let w of String(v??'Not provided').replace(/\s+/g,' ').trim().split(' ')){while(w.length>n){if(line)out.push(line),line='';out.push(w.slice(0,n));w=w.slice(n)}if(line&&line.length+w.length+1>n)out.push(line),line=w;else line+=(line?' ':'')+w}if(line)out.push(line);return out.length?out:['Not provided']};
const rect=(p,x,y,w,h,c)=>p.push(rgb(c)+' rg '+x+' '+(842-y-h)+' '+w+' '+h+' re f');
const txt=(p,s,x,y,size=9,font='F1',c=C.text)=>p.push(rgb(c)+' rg BT /'+font+' '+size+' Tf 1 0 0 1 '+x+' '+(842-y)+' Tm ('+esc(s)+') Tj ET');
const rule=(p,x,y,w,c=C.line)=>p.push(rgb(c)+' RG .8 w '+x+' '+(842-y)+' m '+(x+w)+' '+(842-y)+' l S');
const rupee=(p,x,y)=>{const b=842-y;p.push(rgb(C.navy)+' RG 1.35 w '+x+' '+(b+16)+' m '+(x+15)+' '+(b+16)+' l '+x+' '+(b+9)+' m '+(x+13)+' '+(b+9)+' l '+(x+11)+' '+(b+9)+' m '+(x+10)+' '+(b+3)+' '+(x+8)+' '+(b+1)+' '+(x+4)+' '+b+' c '+(x+3)+' '+b+' l '+(x+17)+' '+(b-1)+' l S')};
function createDonationReceiptPdf({donation,campaign,donor,receipt}){
 const pages=[[]];let p=pages[0],y=0;
 rect(p,0,0,595,258,C.mint);rect(p,42,246,511,1.5,C.teal);rect(p,260,22,75,75,C.teal);
 p.push('q 1.1 0 0 1.1 273 758 cm '+rgb(C.mint)+' rg 24 26 m 12.9 15.9 l 8.2 11.7 10.6 4.5 16.2 4.5 c 19.8 4.5 22.6 7 24 9.8 c 25.4 7 28.2 4.5 31.8 4.5 c 37.4 4.5 39.8 11.7 35.1 15.9 c 24 26 l h f Q');
 p.push('q 1.1 0 0 1.1 273 758 cm '+rgb(C.navy)+' RG 1.8 w 6 29.5 m 10.4 28.1 13.6 25.8 16.5 24.5 c 18.3 23.7 20.3 24.3 21.5 25.8 c 24 28.9 l 26.5 25.8 l 27.7 24.3 29.7 23.7 31.5 24.5 c 34.4 25.8 37.9 28.1 42 29.5 c 37.6 38.1 31.8 42.5 24 42.5 c 16.2 42.5 10.4 38.1 6 29.5 c S Q');
 txt(p,'GOODWILL FOUNDATION',198,119,17,'F2',C.navy);txt(p,'EVERY CONTRIBUTION MAKES A DIFFERENCE',202,135,7.5,'F1',C.muted);rule(p,105,151,385);rect(p,221,164,153,23,C.green);txt(p,'DONATION SUCCESSFUL',242,180,8,'F2',C.teal);txt(p,'Donation Receipt',206,210,25,'F2',C.navy);txt(p,'Thank you for making a positive impact.',180,229,10,'F1',C.muted);
 y=282;rect(p,42,y,511,68,[.95,.98,.96]);rect(p,42,y,4,68,C.teal);txt(p,'YOUR CONTRIBUTION',59,y+22,8,'F2',C.muted);
 const currency=donation.currency||'INR',amount=Number(donation.amount).toLocaleString(currency==='INR'?'en-IN':'en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
 if(currency==='INR'){rupee(p,59,y+49);txt(p,amount,82,y+49,22,'F2',C.navy)}else{txt(p,(currency==='USD'?'$':currency+' ')+amount,59,y+49,22,'F2',C.navy)}
 txt(p,'STATUS  '+donation.status,382,y+25,8,'F2',C.teal);txt(p,'SIMULATED DEMO PAYMENT',382,y+45,7,'F2',C.muted);y+=87;
 const section=t=>{rect(p,42,y-13,511,25,C.pale);txt(p,t.toUpperCase(),54,y+3,8,'F2',C.teal);y+=25};
 const row=(label,value,x,w)=>{txt(p,label.toUpperCase(),x,y,7,'F2',C.muted);let yy=y+14;for(const l of wrap(value,Math.floor(w/5.4))){txt(p,l,x,yy,9,'F1',C.navy);yy+=12}return Math.max(y+28,yy+3)};
 section('Receipt information');y=Math.max(row('Receipt ID',receipt.receiptNumber,54,235),row('Donation date',new Date(donation.createdAt).toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Kolkata'})+' IST',307,235));y=Math.max(row('Transaction reference',donation.transactionRef||'Not available',54,235),row('Payment method',donation.attempts?.at(-1)?.method?.replace(/^DEMO_/,'Demo ')||'Not available',307,235));y=Math.max(row('Currency',currency==='INR'?'INR - Indian Rupee':currency,54,235),row('Payment status',donation.status,307,235))+3;
 section('Donor information');y=Math.max(row('Donor name',donation.anonymous?'Anonymous supporter':donor?.name||donation.donorName||'Supporter',54,235),row('Email address',donation.anonymous?'Not shown for anonymous gift':donor?.email||donation.email||'Not available',307,235))+3;
 section('Campaign information');y=Math.max(row('Campaign',campaign?.title||donation.campaignTitle||'Campaign',54,235),row('Category',campaign?.category||'Not available',307,235))+2;txt(p,'PURPOSE',54,y,7,'F2',C.muted);y+=14;
 for(const l of wrap(campaign?.description||'Your contribution supports this campaign and its community impact.',94)){if(y>735){p=pages[pages.push([])-1];txt(p,'DONATION RECEIPT - CONTINUED',42,48,9,'F2',C.teal);txt(p,receipt.receiptNumber,420,48,8,'F1',C.muted);y=76}txt(p,l,54,y,8.5,'F1',C.text);y+=12}
 if(y>680){p=pages[pages.push([])-1];txt(p,'DONATION RECEIPT - CONTINUED',42,48,9,'F2',C.teal);txt(p,receipt.receiptNumber,420,48,8,'F1',C.muted);y=76}
 rect(p,42,y+8,511,82,C.mint);rect(p,42,y+8,4,82,C.teal);txt(p,'Your kindness creates change.',59,y+33,13,'F2',C.navy);txt(p,'Thank you for supporting Goodwill Foundation.',59,y+54,9,'F1',C.text);txt(p,'Your generosity helps us make a positive difference.',59,y+70,9,'F1',C.text);
 pages.forEach((pg,i)=>{rule(pg,42,795,511);txt(pg,'GOODWILL FOUNDATION - goodwillcares.vercel.app',42,812,7,'F2',C.teal);txt(pg,'Simulated demo donation - No actual payment was collected - Not a tax receipt',42,826,6.3,'F1',C.muted);txt(pg,(i+1)+' / '+pages.length,520,812,7,'F1',C.muted)});
 const objs=[],add=o=>(objs.push(o),objs.length),catalog=add(''),kids=add(''),f1=add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>'),f2=add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>'),pageIds=[];
 for(const pg of pages){const body=pg.join('\n'),stream=add('<< /Length '+Buffer.byteLength(body,'binary')+' >>\nstream\n'+body+'\nendstream');pageIds.push(add('<< /Type /Page /Parent '+kids+' 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 '+f1+' 0 R /F2 '+f2+' 0 R >> >> /Contents '+stream+' 0 R >>'))}
 objs[catalog-1]='<< /Type /Catalog /Pages 2 0 R >>';objs[kids-1]='<< /Type /Pages /Kids ['+pageIds.map(x=>x+' 0 R').join(' ')+'] /Count '+pageIds.length+' >>';
 let out='%PDF-1.4\n',offs=[0];objs.forEach((o,i)=>{offs.push(Buffer.byteLength(out,'binary'));out+=(i+1)+' 0 obj\n'+o+'\nendobj\n'});let x=Buffer.byteLength(out,'binary');out+='xref\n0 '+(objs.length+1)+'\n0000000000 65535 f \n';offs.slice(1).forEach(v=>out+=String(v).padStart(10,'0')+' 00000 n \n');out+='trailer\n<< /Size '+(objs.length+1)+' /Root 1 0 R >>\nstartxref\n'+x+'\n%%EOF';return Buffer.from(out,'binary');
}
export { createDonationReceiptPdf };