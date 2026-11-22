import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const runtime='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const {PresentationFile,FileBlob}=await import(pathToFileURL(runtime).href);
const root=process.cwd(),build=path.join(root,'docs/.presentation-build'),out=path.join(root,'docs/presentation-output');
const source=path.join(out,'Goodwill_Foundation_Donation_Management_System_Presentation.pptx');
const p=await PresentationFile.importPptx(await FileBlob.load(source));
if(p.slides.items.length!==21)throw new Error(`Expected 21 source slides, found ${p.slides.items.length}`);
p.slides.keep([0,1,2,3,4,5,6,7,11,15,16,17,18,19,20]);
if(p.slides.items.length!==15)throw new Error('Requested removals did not leave 15 slides');
const coverPanel=p.resolve('sh/fu94fe98'),coverText=p.resolve('sh/utg3698n');
coverPanel.position={left:82,top:520,width:720,height:112};coverText.position={left:101,top:527,width:680,height:98};
coverText.text='Presented by: Project Team\nRegister Numbers: 2025DCSBT10466, 2025DCSBT10467, 2025DCSBT10468\n2025DCSBT10469, 2025DCSBT10470\nBranch: CSE – 6  |  Institution: VVIT University\nAcademic Year: 2026–2027';
coverText.text.style={fontSize:14,typeface:'Arial',color:'#FFFFFF',bold:true,alignment:'left',verticalAlignment:'middle',autoFit:'shrinkText',insets:{left:0,right:0,top:0,bottom:0}};
p.resolve('sh/wn6dc7eh').delete();
const {slide}=p.slides.insert({after:p.slides.items[8]});
const C={navy:'#123047',teal:'#168C8A',mint:'#E7F4EF',gold:'#D9A441',coral:'#D86658',ink:'#193247',muted:'#587080',paper:'#F6F8F7',white:'#FFFFFF',line:'#D9E3E1'};
slide.background.fill=C.paper;
const logo='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#168C8A"/><path d="M32 48S12 37 12 24c0-7 9-11 15-4l5 6 5-6c6-7 15-3 15 4 0 13-20 24-20 24Z" fill="#fff"/><path d="M17 40c5 2 10 1 14-2m16 2c-5 2-10 1-14-2" fill="none" stroke="#D9A441" stroke-width="3" stroke-linecap="round"/></svg>';
function addShape(geo,x,y,w,h,fill='none',stroke='none',sw=0){return slide.shapes.add({geometry:geo,position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:sw},borderRadius:geo==='roundRect'?18:undefined});}
function text(value,x,y,w,h,size,color=C.ink,bold=false,align='left'){const s=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});s.text=value;s.text.style={fontSize:size,typeface:'Arial',color,bold,alignment:align,verticalAlignment:'middle',autoFit:'shrinkText',insets:{left:0,right:0,top:0,bottom:0},wrap:true};return s;}
slide.images.add({svg:logo,alt:'Goodwill Foundation heart logo',position:{left:58,top:34,width:34,height:34}});text('goodwill.',102,33,150,38,24,C.navy,true);text('TECHNOLOGY & AI',1040,38,180,24,12,C.teal,true,'right');
text('Technology Stack & AI Tools',60,112,1120,62,38,C.navy,true);text('The application platform and AI-assisted tools used to develop and present it.',62,176,1110,34,17,C.muted);
const cards=[
{x:62,color:C.teal,icon:'WEB',title:'Web application',tag:'FRONTEND',lines:['React interface with Vite tooling','Responsive layouts using authored CSS','React Router for page navigation','Lucide icons and Recharts visuals']},
{x:460,color:C.gold,icon:'API',title:'API & data',tag:'BACKEND',lines:['Node.js and Express REST API','Prisma ORM with PostgreSQL mode','JSON demo storage for local showcase','JWT authentication and Zod validation']},
{x:858,color:C.coral,icon:'AI',title:'AI tools used',tag:'DEVELOPMENT',lines:['GPT / ChatGPT — planning, explanations, writing, and review','OpenAI Codex — repository-aware coding, debugging, and implementation support','AI-assisted changes reviewed and integrated into the project']}
];
for(const c of cards){addShape('roundRect',c.x,242,360,328,C.white,C.line,1);addShape('rect',c.x,242,360,7,c.color);addShape('ellipse',c.x+25,270,56,56,c.color);text(c.icon,c.x+25,270,56,56,15,C.white,true,'center');text(c.tag,c.x+98,270,230,20,11,c.color,true);text(c.title,c.x+25,343,310,37,23,C.navy,true);c.lines.forEach((line,i)=>{addShape('ellipse',c.x+28,398+i*42,8,8,c.color);text(line,c.x+48,383+i*42,285,40,15,C.muted);});}
addShape('roundRect',62,598,1156,48,C.mint,'none',0);text('Frontend: React + Vite  •  API: Express  •  Data: Prisma + PostgreSQL (or JSON demo mode)',82,604,1116,36,15,C.ink,true,'center');
addShape('rect',60,674,1160,2,C.line);text('DONATION MANAGEMENT SYSTEM',60,681,400,20,11,C.muted,true);text('10',1170,679,45,20,12,C.teal,true,'right');
slide.speakerNotes.text='Technology summary based on client/package.json, server/package.json, and docs/SYSTEM_DESIGN_DOCUMENTATION.md. AI tools listed per project team request: GPT/ChatGPT and OpenAI Codex.';
for(const [i,s] of p.slides.items.entries())for(const sh of s.shapes.items){const pos=sh.position||{},value=String(sh.text??'').trim();if(pos.left>=1160&&pos.top>=675&&/^\d{2}$/.test(value))sh.text=String(i+1).padStart(2,'0');}
if(p.slides.items.length!==16)throw new Error(`Expected 16 total slides, found ${p.slides.items.length}`);
const renders=path.join(build,'rendered-ai-stack');await fs.mkdir(renders,{recursive:true});for(const [i,s] of p.slides.items.entries()){const png=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(path.join(renders,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));}
const candidate=path.join(build,'candidate-ai-stack.pptx');await(await PresentationFile.exportPptx(p)).save(candidate);
const SKILL='C:/Users/mysel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';const{finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const finalPath=path.join(out,'Goodwill_Foundation_Donation_Management_System_Presentation_AI_Stack_Final.pptx');
await finalizePresentation({explicitTotalSlideCount:16,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe',integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'Goodwill_Foundation_Donation_Management_System_Presentation_AI_Stack_Final.validation.json')});
console.log(`DONE ${finalPath} (${p.slides.items.length} slides)`);
