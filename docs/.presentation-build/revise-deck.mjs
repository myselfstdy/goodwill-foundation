import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const runtime='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const {PresentationFile,FileBlob}=await import(pathToFileURL(runtime).href);
const root=process.cwd(), build=path.join(root,'docs/.presentation-build'), out=path.join(root,'docs/presentation-output');
const source=path.join(out,'Goodwill_Foundation_Donation_Management_System_Presentation.pptx');
const p=await PresentationFile.importPptx(await FileBlob.load(source));
// Delete requested original slide numbers: 9, 10, 11, 13, 14, and 15 (zero-based indexes).
p.slides.delete([8,9,10,12,13,14]);
if(p.slides.items.length!==15) throw new Error(`Expected 15 remaining slides, got ${p.slides.items.length}`);
const metadataBox=p.resolve('sh/fu94fe98');
const metadataText=p.resolve('sh/utg3698n');
metadataBox.position={left:82,top:520,width:720,height:112};
metadataText.position={left:101,top:527,width:680,height:98};
metadataText.text='Presented by: Project Team\nRegister Numbers: 2025DCSBT10466, 2025DCSBT10467, 2025DCSBT10468\n2025DCSBT10469, 2025DCSBT10470\nBranch: CSE – 6  |  Institution: VVIT University\nAcademic Year: 2026–2027';
metadataText.text.style={fontSize:14,typeface:'Arial',color:'#FFFFFF',bold:true,alignment:'left',verticalAlignment:'middle',autoFit:'shrinkText',insets:{left:0,right:0,top:0,bottom:0}};
p.resolve('sh/wn6dc7eh').delete();// Refresh visible folios so the retained slides are numbered in sequence.
for(const [i,slide] of p.slides.items.entries()){
 if(i===0) continue;
 for(const sh of slide.shapes.items){const pos=sh.position||{};const current=String(sh.text??'').trim();if(pos.left>=1160&&pos.top>=675&&/^\d{2}$/.test(current))sh.text=String(i+1).padStart(2,'0');}
}
const renderDir=path.join(build,'rendered-revised');await fs.mkdir(renderDir,{recursive:true});
for(const [i,slide] of p.slides.items.entries()) {const png=await p.export({slide,format:'png',scale:1});await fs.writeFile(path.join(renderDir,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));}
const candidate=path.join(build,'candidate-revised.pptx');await (await PresentationFile.exportPptx(p)).save(candidate);
const SKILL='C:/Users/mysel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const finalPath=path.join(out,'Goodwill_Foundation_Donation_Management_System_Presentation_Final.pptx');
await finalizePresentation({explicitTotalSlideCount:15,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe',integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'Goodwill_Foundation_Donation_Management_System_Presentation_Final.validation.json')});
console.log(`DONE ${finalPath} (${p.slides.items.length} slides)`);


