import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const { Presentation, PresentationFile } = await import(pathToFileURL('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);

const root = process.cwd();
const build = path.join(root, 'docs/.presentation-build');
const outDir = path.join(root, 'docs/presentation-output');
const renderDir = path.join(build, 'rendered');
await fs.mkdir(renderDir, {recursive:true}); await fs.mkdir(outDir,{recursive:true});
const P = {navy:'#123047',teal:'#168C8A', mint:'#E7F4EF', gold:'#D9A441', coral:'#D86658', ink:'#193247', muted:'#587080', paper:'#F6F8F7', white:'#FFFFFF', line:'#D9E3E1', pale:'#EEF5F3'};
const pres = Presentation.create({slideSize:{width:1280,height:720}});
pres.theme.defaultFont='Arial';
const logoSvg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#168C8A"/><path d="M32 48S12 37 12 24c0-7 9-11 15-4l5 6 5-6c6-7 15-3 15 4 0 13-20 24-20 24Z" fill="#fff"/><path d="M17 40c5 2 10 1 14-2m16 2c-5 2-10 1-14-2" fill="none" stroke="#D9A441" stroke-width="3" stroke-linecap="round"/></svg>';
function shape(slide,geo,x,y,w,h,fill='none',stroke='none',sw=0,name=''){return slide.shapes.add({geometry:geo,name,position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:sw},borderRadius:geo==='roundRect'?18:undefined});}
function txt(slide,text,x,y,w,h,size=20,color=P.ink,bold=false,opts={}){const s=shape(slide,'textbox',x,y,w,h,'none','none',0);s.text=text;s.text.style={fontSize:size,typeface:'Arial',color,bold,alignment:opts.align||'left',verticalAlignment:opts.valign||'middle',autoFit:'shrinkText',insets:{left:0,right:0,top:0,bottom:0},wrap:true};return s;}
function addLogo(slide,x=58,y=34,size=34){slide.images.add({svg:logoSvg,alt:'Goodwill Foundation heart logo',position:{left:x,top:y,width:size,height:size}});txt(slide,'goodwill.',x+size+10,y-1,150,size+4,24,P.navy,true);}
function base(title,sub='',section='GOODWILL FOUNDATION'){const s=pres.slides.add();s.background.fill=P.paper;addLogo(s);txt(s,section.toUpperCase(),1040,38,180,24,12,P.teal,true,{align:'right'});txt(s,title,60,112,1120,62,38,P.navy,true);if(sub)txt(s,sub,62,176,1110,34,17,P.muted,false);shape(s,'rect',60,674,1160,2,P.line);txt(s,'DONATION MANAGEMENT SYSTEM',60,681,400,20,11,P.muted,true);txt(s,String(pres.slides.items.length).padStart(2,'0'),1170,679,45,20,12,P.teal,true,{align:'right'});return s;}
function card(slide,x,y,w,h,title,body,accent=P.teal){shape(slide,'roundRect',x,y,w,h,P.white,P.line,1);shape(slide,'rect',x,y,6,h,accent);txt(slide,title,x+24,y+18,w-46,31,20,P.navy,true);txt(slide,body,x+24,y+56,w-46,h-70,16,P.muted,false,{valign:'top'});}
async function image(slide,file,x,y,w,h,alt){shape(slide,'roundRect',x-5,y-5,w+10,h+10,P.white,P.line,1);const bytes=await fs.readFile(path.join(root,file));slide.images.add({blob:new Uint8Array(bytes),contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
function notes(slide,refs){slide.speakerNotes.text=`Sources: ${refs.join('; ')}. Project content is adapted for Goodwill Foundation; reference deck contributes section-heading structure only.`;}
// 1 Cover
{
 const s=pres.slides.add();s.background.fill=P.navy;shape(s,'ellipse',800,0,460,460,'#1D5264');shape(s,'ellipse',940,420,300,300,'#174456');
 slideLogo(s,78,58,52);
 function slideLogo(sl,x,y,size){sl.images.add({svg:logoSvg,alt:'Goodwill Foundation heart logo',position:{left:x,top:y,width:size,height:size}});txt(sl,'goodwill.',x+size+12,y-2,190,size+8,32,P.white,true);}
 txt(s,'DONATION MANAGEMENT SYSTEM',80,175,700,25,15,'#91D8C6',true);txt(s,'Giving that\nfeels good.',78,225,675,170,62,P.white,true);txt(s,'A transparent, accessible platform for discovering causes,\nmaking donations, and managing community impact.',82,418,660,78,23,'#D7E7E7');shape(s,'roundRect',82,533,435,76,'#FFFFFF/10','#FFFFFF/25',1);txt(s,'VVIT University  •  CSE – 6  •  Academic Year 2026–2027',102,546,390,50,15,P.white,true);
 txt(s,'Presented by Project Team',82,631,450,26,14,'#B9D2D7');txt(s,'PROJECT PRESENTATION',920,650,270,25,12,'#9EC9C8',true,{align:'right'});
 notes(s,['Donation_Management_System.pptx cover details','docs/Goodwill_Donation_Management_System_Final_Report.pdf']);
}
// 2 Project Overview
{
 const s=base('Project Overview','A role-based web application that connects donors with active community campaigns.');
 card(s,62,245,350,210,'Purpose','Make it easier to discover causes, give securely through a simulated checkout, and keep a clear record of each successful gift.');
 card(s,465,245,350,210,'People','Guests explore campaigns. Donors manage gifts and receipts. Administrators manage campaigns and review platform activity.',P.gold);
 card(s,868,245,350,210,'Platform','React and Vite client, Express API, and a Prisma-backed PostgreSQL mode, with a JSON demo mode for local showcase.',P.coral);
 txt(s,'One experience from campaign discovery to verified receipt.',62,508,1140,52,26,P.teal,true,{align:'center'});
 notes(s,['docs/Goodwill_Donation_Management_System_Final_Report.pdf','docs/SYSTEM_DESIGN_DOCUMENTATION.md']);
}
// 3 Problem Statement
{
 const s=base('Problem Statement','Donation processes can feel fragmented when discovery, payment records, and follow-up live in separate places.');
 const items=[['Hard to find a fit','Donors need clear campaign details and categories before choosing a cause.'],['Unclear gift history','Without organized records, donors may struggle to confirm what happened to a donation.'],['Manual administration','Campaign updates, receipt handling, and reporting can take time when managed by hand.'],['Trust and access','Sensitive donor information needs controlled access and a reliable audit trail.']];
 items.forEach((a,i)=>card(s,62+(i%2)*584,240+Math.floor(i/2)*190,548,154,a[0],a[1],[P.teal,P.gold,P.coral,P.navy][i]));
 notes(s,['docs/Goodwill_Donation_Management_System_Final_Report.pdf']);
}
// 4 Solution
{
 const s=base('Solution','A single portal supports campaign discovery, giving, and ongoing administration.');
 const steps=[['01','Discover','Browse causes and campaign details.'],['02','Give','Complete a simulated donation checkout.'],['03','Confirm','Successful gifts create a receipt and history entry.'],['04','Manage','Donors and administrators use role-specific workspaces.']];
 steps.forEach((a,i)=>{const x=62+i*294;shape(s,'roundRect',x,270,255,220,P.white,P.line,1);txt(s,a[0],x+22,290,56,40,20,P.teal,true);txt(s,a[1],x+22,345,210,34,23,P.navy,true);txt(s,a[2],x+22,395,210,70,16,P.muted,false,{valign:'top'});if(i<3){shape(s,'rightArrow',x+259,359,34,28,P.gold,'none',0)}});
 txt(s,'The payment provider is a local simulator; live card processing is not configured.',62,545,1125,48,17,P.coral,true,{align:'center'});
 notes(s,['docs/SYSTEM_DESIGN_DOCUMENTATION.md','docs/Goodwill_Donation_Management_System_Final_Report.pdf']);
}
// 5 Main Features
{
 const s=base('Main Features','Core features are organized around donor confidence and efficient campaign operations.');
 const list=[['Campaign discovery','Category browsing, search, campaign detail pages'],['Donor workspace','Donation history, receipts, saved causes, preferences'],['Admin workspace','Campaign management, activity overview, donor support'],['Donation records','Payment attempts, success-only receipts, transaction references'],['Reports and exports','Dashboard summaries plus CSV and PDF outputs'],['Account safeguards','Role checks, validation, rate limits, audit and security history']];
 list.forEach((a,i)=>card(s,62+(i%3)*392,230+Math.floor(i/3)*190,360,154,a[0],a[1],[P.teal,P.gold,P.navy,P.coral,P.teal,P.gold][i]));
 notes(s,['docs/Goodwill_Donation_Management_System_Final_Report.pdf','docs/API_DOCUMENTATION.md']);
}
// 6 Reports Supported
{
 const s=base('Reports Supported','Donation reporting keeps the donor’s personal record separate from organization-wide oversight.');
 card(s,62,250,530,245,'Donor records','• Donation history and status\n• Printable receipt for successful gifts\n• Receipt and transaction references\n• Downloadable personal history',P.teal);
 card(s,652,250,566,245,'Administrator reports','• Campaign and donation summaries\n• CSV exports for operational review\n• PDF reports and printable views\n• Audit context for key actions',P.gold);
 txt(s,'A receipt is issued only after a successful simulated payment outcome.',62,542,1150,42,17,P.muted,false,{align:'center'});
 notes(s,['docs/API_DOCUMENTATION.md','docs/SYSTEM_DESIGN_DOCUMENTATION.md']);
}
// 7 Users and Responsibilities
{
 const s=base('Users and Responsibilities','Access is separated by role so each person sees the right tools and records.');
 card(s,62,255,350,240,'Guest','Explore campaigns and begin a donation without opening a donor account.',P.gold);
 card(s,465,255,350,240,'Donor','Manage profile and preferences; review own donation history, receipts, and support requests.',P.teal);
 card(s,868,255,350,240,'Administrator','Create and update campaigns; review platform activity, reports, and support operations.',P.navy);
 notes(s,['docs/Goodwill_Donation_Management_System_Final_Report.pdf','docs/SYSTEM_DESIGN_DOCUMENTATION.md']);
}
// 8 Main Workflow
{
 const s=base('Main Workflow','From choosing a cause to recording a confirmed gift.');
 const labels=[['1','Browse campaigns'],['2','Choose a cause'],['3','Enter gift details'],['4','Simulated payment'],['5','Record outcome'],['6','Issue receipt']];
 labels.forEach((a,i)=>{let x=62+i*194;shape(s,'ellipse',x+57,295,64,64,i===5?P.gold:P.teal);txt(s,a[0],x+57,295,64,64,23,P.white,true,{align:'center'});txt(s,a[1],x,385,178,60,17,P.navy,true,{align:'center'});if(i<5)shape(s,'rightArrow',x+142,313,48,28,P.line,'none',0)});
 shape(s,'roundRect',90,500,1100,80,P.mint,'none');txt(s,'Failure path: retain the failed payment attempt, show the outcome, and do not create a receipt.',115,516,1050,47,17,P.ink,true,{align:'center'});
 notes(s,['docs/diagrams/rendered/activity-diagram.png','docs/SYSTEM_DESIGN_DOCUMENTATION.md']);
}
// 9 Main Workflow – UML Activity Diagram (from reference “Design Overview” framing)
{
 const s=base('Main Workflow','UML activity diagram • donation checkout and outcome handling','DESIGN OVERVIEW');
 await image(s,'docs/diagrams/rendered/activity-diagram.png',132,220,1016,420,'Donation activity diagram showing successful and failed donation paths');
 notes(s,['docs/diagrams/rendered/activity-diagram.png','docs/diagrams/activity-diagram.mmd']);
}
// 10 Technical Overview – Architecture
{
 const s=base('Technical Overview','Three-tier request flow with role-aware API and persistent data options.','TECHNICAL OVERVIEW');
 await image(s,'docs/diagrams/rendered/system-architecture.png',80,220,1120,420,'System architecture diagram for the Goodwill donation application');
 notes(s,['docs/diagrams/rendered/system-architecture.png','docs/SYSTEM_DESIGN_DOCUMENTATION.md']);
}
// 11 Design Overview – Data
{
 const s=base('Design Overview','Core giving relationships connect donors, campaigns, donations, payment attempts, and receipts.','DESIGN OVERVIEW');
 await image(s,'docs/diagrams/rendered/er-diagram.png',85,215,1110,440,'Entity relationship diagram for the donation management system');
 notes(s,['docs/diagrams/rendered/er-diagram.png','server/prisma/schema.prisma']);
}
// 12 Design Overview – Use Case
{
 const s=base('Design Overview','UML use cases show the responsibilities available to each system actor.','DESIGN OVERVIEW');
 await image(s,'docs/diagrams/rendered/use-case-diagram.png',105,220,1070,420,'UML use case diagram for Goodwill Foundation donation management');
 notes(s,['docs/diagrams/rendered/use-case-diagram.png','docs/diagrams/use-case-diagram.mmd']);
}
// 13 Design Overview – Sequence
{
 const s=base('Design Overview','A successful gift coordinates the client, API, database, and payment simulator.','DESIGN OVERVIEW');
 await image(s,'docs/diagrams/rendered/sequence-diagram.png',85,220,1110,420,'Sequence diagram for donation processing and receipt creation');
 notes(s,['docs/diagrams/rendered/sequence-diagram.png','docs/diagrams/sequence-diagram.mmd','docs/SYSTEM_DESIGN_DOCUMENTATION.md']);
}
// 14 Data Flow
{
 const s=base('Design Overview','Data-flow diagrams describe the system boundary and the supporting process breakdown.','DESIGN OVERVIEW');
 await image(s,'docs/diagrams/rendered/dfd-level-0.png',65,245,550,330,'Level 0 data flow diagram');await image(s,'docs/diagrams/rendered/dfd-level-1.png',660,245,550,330,'Level 1 data flow diagram');
 notes(s,['docs/diagrams/rendered/dfd-level-0.png','docs/diagrams/rendered/dfd-level-1.png']);
}
// 15 Feasibility and Testing
{
 const s=base('Feasibility and Testing','A practical showcase build with automated API and client utility coverage.');
 shape(s,'roundRect',62,238,330,300,P.navy,'none');txt(s,'26',90,285,270,90,66,P.white,true,{align:'center'});txt(s,'automated checks passed',90,375,270,48,21,'#BDE5D9',true,{align:'center'});txt(s,'23 API integration + 3 client utility tests',90,435,270,50,15,P.white,false,{align:'center'});
 card(s,440,238,360,300,'Verified behaviors','Authentication and role protection\nCampaign and donation paths\nReceipt and reporting responses\nClient formatting utilities',P.teal);
 card(s,842,238,376,300,'Current boundaries','The recorded test run used demo mode. PostgreSQL production integration and live deployment health are not certified by that run.',P.coral);
 txt(s,'Payment processing is simulated; no live card or bank transfer is performed.',62,567,1150,44,16,P.coral,true,{align:'center'});
 notes(s,['docs/TESTING_DOCUMENTATION.md','docs/PROJECT_DOCUMENTATION_AUDIT.md','docs/SYSTEM_DESIGN_DOCUMENTATION.md']);
}
// 16–19 Application Screenshots
{
 const pages=[
  ['Application Screenshots – Campaign Discovery','Public pages introduce the foundation and help donors find causes.',[['home.png','Home page'],['campaigns.png','Campaign discovery']],['docs/screenshots/home.png','docs/screenshots/campaigns.png']],
  ['Application Screenshots – Donor Access','Registration and sign-in are the entry points for account features.',[['login.png','Donor sign in'],['register.png','Account registration']],['docs/screenshots/login.png','docs/screenshots/register.png']],
  ['Application Screenshots – Donor Portal','Donors can review their giving activity and account information.',[['donor-dashboard.png','Donor dashboard'],['donor-history.png','Donation history']],['docs/screenshots/donor-dashboard.png','docs/screenshots/donor-history.png']],
  ['Application Screenshots – Admin Portal','Administrators manage campaigns and review platform activity.',[['admin-dashboard.png','Admin dashboard'],['admin-campaigns.png','Campaign administration']],['docs/screenshots/admin-dashboard.png','docs/screenshots/admin-campaigns.png']]
 ];
 for(const [title,subtitle,files,refs] of pages){const s=base(title,subtitle,'APPLICATION SCREENSHOTS');for(const [i,a] of files.entries()){const x=62+i*588;await image(s,'docs/screenshots/'+a[0],x,238,550,354,a[1]);txt(s,a[1],x,599,550,28,15,P.muted,true,{align:'center'});}notes(s,refs);}
}// 20 Wrap-up / Future Work
{
 const s=base('Wrap-Up','Goodwill brings discovery, donation records, receipts, and campaign administration into one application.');
 card(s,62,245,530,262,'Delivered','Responsive public campaign experience\nDonor and administrator workspaces\nDonation status and receipt flow\nReports, exports, and system diagrams',P.teal);
 card(s,652,245,566,262,'Next steps','Connect a production payment provider\nConfigure email and SMS delivery\nAdd recurring gifts and stronger account verification\nAutomate privacy-safe account deletion',P.gold);
 txt(s,'Designed to make giving easier to follow and simpler to manage.',62,555,1156,44,21,P.navy,true,{align:'center'});
 notes(s,['docs/Goodwill_Donation_Management_System_Final_Report.pdf','docs/PROJECT_DOCUMENTATION_AUDIT.md','docs/SYSTEM_DESIGN_DOCUMENTATION.md']);
}
// 21 closing slide
{
 const s=pres.slides.add();s.background.fill=P.teal;shape(s,'ellipse',920,0,350,350,'#2A9E96');shape(s,'ellipse',0,500,215,215,'#127A7B');
 s.images.add({svg:logoSvg,alt:'Goodwill Foundation heart logo',position:{left:565,top:145,width:150,height:150}});
 txt(s,'Thank you',250,330,780,92,58,P.white,true,{align:'center'});txt(s,'Goodwill Foundation • Donation Management System',260,438,760,42,22,'#E2F5EF',false,{align:'center'});txt(s,'Questions',500,554,280,42,20,P.white,true,{align:'center'});
 notes(s,['Goodwill Foundation project presentation']);
}
for (const [i,s] of pres.slides.items.entries()) {const png=await pres.export({slide:s,format:'png',scale:1});await fs.writeFile(path.join(renderDir,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));}
const candidate=path.join(build,'candidate.pptx');await (await PresentationFile.exportPptx(pres)).save(candidate);
const SKILL_DIR='C:/Users/mysel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')).href);
const finalPath=path.join(outDir,'Goodwill_Foundation_Donation_Management_System_Presentation_v2.pptx');
await finalizePresentation({explicitTotalSlideCount:21,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe',integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'Goodwill_Foundation_Donation_Management_System_Presentation.validation.json')});
console.log(`DONE ${finalPath} (${pres.slides.items.length} slides)`);






