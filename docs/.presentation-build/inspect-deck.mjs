import { pathToFileURL } from 'node:url';
const {PresentationFile,FileBlob}=await import(pathToFileURL('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const p=await PresentationFile.importPptx(await FileBlob.load('docs/presentation-output/Goodwill_Foundation_Donation_Management_System_Presentation.pptx'));
console.log('slides',p.slides.items.length);
const info=await p.inspect({kind:'slide,textbox,shape,image',maxChars:20000});
console.log(info.ndjson.split('\n').filter(x=>x.includes('slideIndex":0')||x.includes('slideIndex":1')).join('\n'));
