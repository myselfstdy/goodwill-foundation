"""Generate the editable Goodwill project presentation using native PowerPoint shapes."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData

OUT = Path(__file__).with_name('Donation-Management-System-Presentation.pptx')
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
NAVY = RGBColor(16,42,67); INK = RGBColor(28,58,75); TEAL = RGBColor(22,140,138)
MINT = RGBColor(220,242,233); PALE = RGBColor(245,249,246); WHITE = RGBColor(255,255,255)
MUTED = RGBColor(119,140,147); LINE = RGBColor(226,235,231); GOLD = RGBColor(215,173,104)
GREEN = RGBColor(71,161,131); BLUE = RGBColor(111,143,191); PEACH = RGBColor(212,151,103)

def textbox(slide, x,y,w,h,text,size=16,color=INK,bold=False,font='Aptos',align=None,margin=0.02):
    shape=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=shape.text_frame
    tf.clear(); tf.word_wrap=True; tf.margin_left=Inches(margin);tf.margin_right=Inches(margin);tf.margin_top=Inches(margin);tf.margin_bottom=Inches(margin)
    p=tf.paragraphs[0];p.text=text;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color
    if align is not None:p.alignment=align
    return shape

def rect(slide,x,y,w,h,fill=WHITE,line=LINE,radius=True):
    shp=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid();shp.fill.fore_color.rgb=fill;shp.line.color.rgb=line;shp.line.width=Pt(.8)
    if radius:
        try: shp.adjustments[0]=.12
        except Exception: pass
    return shp

def circle(slide,x,y,d,fill):
    s=slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d));s.fill.solid();s.fill.fore_color.rgb=fill;s.line.fill.background();return s

def line(slide,x1,y1,x2,y2,color=TEAL,width=1.7,arrow=False):
    s=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2));s.line.color.rgb=color;s.line.width=Pt(width)
    return s

def base(title,kicker='GOODWILL · DONATION MANAGEMENT',num=None):
    s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=PALE
    textbox(s,.55,.27,7,.24,kicker,9,TEAL,True)
    textbox(s,.55,.62,11.9,.58,title,27,NAVY,True,'Aptos Display')
    line(s,.55,1.32,12.78,1.32,LINE,.7)
    textbox(s,.55,7.13,6,.2,'A little good goes a long way.',8,MUTED)
    if num: textbox(s,12.25,7.1,.5,.22,f'{num:02}',8,MUTED,align=PP_ALIGN.RIGHT)
    return s

def bullet(slide,x,y,w,text,accent=TEAL,size=14):
    circle(slide,x,y+.09,.11,accent);textbox(slide,x+.23,y,w-.23,.43,text,size,INK)

# 1 cover
s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=NAVY
circle(s,9.15,-.6,5.6,RGBColor(24,70,82));circle(s,10.25,.72,3.35,TEAL);circle(s,10.93,1.39,2.0,MINT)
textbox(s,.88,.78,6,.3,'NONPROFIT GIVING · PROJECT SHOWCASE',10,RGBColor(148,219,200),True)
textbox(s,.88,1.68,7.0,1.55,'Goodwill',60,WHITE,True,'Aptos Display')
textbox(s,.91,3.04,6.3,.65,'Donation Management System',28,RGBColor(203,228,220),False,'Aptos Display')
textbox(s,.92,4.22,5.55,.8,'A clearer, kinder way to connect generous people with causes that matter.',18,RGBColor(198,216,218))
rect(s,.91,5.74,2.3,.52,TEAL,TEAL);textbox(s,1.13,5.86,1.9,.18,'PROJECT PRESENTATION',9,WHITE,True)
textbox(s,.92,6.75,5,.2,'React · Express · Prisma · PostgreSQL',10,RGBColor(164,191,194))

# 2 intro
s=base('Giving should feel simple, honest, and human.',num=2)
textbox(s,.65,1.75,6.1,.55,'One connected place for the whole giving journey.',23,NAVY,True,'Aptos Display')
textbox(s,.67,2.52,5.8,1.0,'Goodwill brings public campaigns, donor accounts, administrative tools, simulated checkout, receipts and transparent reporting into one responsive web application.',15,MUTED)
for i,(big,label,col) in enumerate([('$125k','Successful gifts',TEAL),('1,248','Donors',BLUE),('5','Active causes',GREEN)]):
    x=7+i*1.82;rect(s,x,2.02,1.62,1.54,WHITE);textbox(s,x+.14,2.31,1.35,.42,big,23,col,True,'Aptos Display');textbox(s,x+.14,2.89,1.35,.35,label,10,MUTED)
rect(s,.67,4.44,11.95,1.55,MINT,MINT);textbox(s,.95,4.77,2,.3,'THE PROMISE',10,TEAL,True);textbox(s,2.8,4.69,9.2,.65,'Every gift is traceable. Every successful donation has a receipt. Every payment in this showcase is simulated.',18,NAVY,True,'Aptos Display')

# 3 problem
s=base('The problem: good intentions meet fragmented tools.',num=3)
cards=[('01','Scattered records','Campaigns, donors and gifts live in separate spreadsheets and inboxes.'),('02','Limited visibility','Teams struggle to see what is working and where support is flowing.'),('03','Low confidence','Donors need clear confirmation, reliable receipts and transparent outcomes.')]
for i,(n,h,b) in enumerate(cards):
    x=.7+i*4.13;rect(s,x,1.92,3.77,3.54,WHITE);textbox(s,x+.22,2.18,.6,.35,n,14,TEAL,True);line(s,x+.22,2.68,x+3.48,2.68,LINE,1);textbox(s,x+.22,2.99,3.3,.6,h,20,NAVY,True,'Aptos Display');textbox(s,x+.22,3.83,3.2,1.0,b,13,MUTED)
textbox(s,.77,6.04,11.5,.34,'A consistent experience can help teams spend less time reconciling and more time serving.',14,TEAL,True)

# 4 objectives
s=base('Objectives',num=4)
items=[('Connect the journey','Bring campaigns, giving, donor records, receipts and reporting together.'),('Protect private records','Use secure sign-in, role checks, input validation and scoped donor access.'),('Make outcomes visible','Summarize successful gifts, campaign progress, trends and activity.'),('Keep checkout safe','Demonstrate success and failure without collecting real payment information.')]
for i,(h,b) in enumerate(items):
    col=i%2;row=i//2;x=.75+col*6.03;y=1.8+row*2.0;rect(s,x,y,5.65,1.62,WHITE);circle(s,x+.22,y+.26,.42,MINT);textbox(s,x+.22,y+.32,.42,.18,str(i+1),11,TEAL,True,align=PP_ALIGN.CENTER);textbox(s,x+.85,y+.22,4.45,.35,h,16,NAVY,True);textbox(s,x+.85,y+.7,4.45,.63,b,11,MUTED)

# 5 existing
s=base('Existing approach: useful pieces, little connection.',num=5)
textbox(s,.8,1.78,4.9,.42,'TYPICAL TOOLCHAIN',10,MUTED,True)
for i,(label,col) in enumerate([('Web form',BLUE),('Spreadsheet',GOLD),('Email receipts',PEACH),('Manual reports',TEAL)]):
    x=.8+i*2.88;rect(s,x,2.32,2.45,1.02,WHITE);circle(s,x+.16,2.58,.3,col);textbox(s,x+.56,2.58,1.7,.26,label,12,NAVY,True)
    if i<3:line(s,x+2.5,2.83,x+2.82,2.83,MUTED,1.5,True)
rect(s,.82,4.12,11.7,1.44,RGBColor(250,239,229),RGBColor(250,239,229));textbox(s,1.05,4.43,2.0,.25,'THE FRICTION',10,PEACH,True);textbox(s,3.0,4.38,8.9,.55,'Duplicate entry · Delayed updates · Hard-to-audit changes · Manual follow-up',16,NAVY,True,'Aptos Display')

# 6 proposed
s=base('Proposed system: one simple flow, shared records.',num=6)
parts=[('Discover','Campaigns'),('Give','Demo checkout'),('Confirm','Receipt'),('Understand','Reports')]
for i,(h,b) in enumerate(parts):
    x=.75+i*3.12;rect(s,x,2.14,2.57,2.12,WHITE);circle(s,x+.18,2.34,.5,[MINT,RGBColor(230,238,248),RGBColor(250,239,226),RGBColor(233,242,228)][i]);textbox(s,x+.18,2.5,.5,.18,str(i+1),12,TEAL,True,align=PP_ALIGN.CENTER);textbox(s,x+.2,3.05,2.2,.34,h,18,NAVY,True,'Aptos Display');textbox(s,x+.2,3.52,2.2,.3,b,11,MUTED)
    if i<3:line(s,x+2.6,3.22,x+3.06,3.22,TEAL,2,True)
textbox(s,.82,5.13,11.2,.5,'Role-aware workspaces keep the public experience welcoming and the admin experience operational.',15,TEAL,True)

# 7 tech stack
s=base('Technology stack',num=7)
stack=[('FRONT END','React 18','Vite · Router · Axios · Recharts · Lucide',TEAL),('API','Node.js + Express','REST · JWT · bcrypt · Zod · Helmet',BLUE),('DATA','PostgreSQL + Prisma','UUIDs · Decimal money · migrations · seed data',GREEN),('QUALITY','Vitest + Supertest','API behavior checks · documentation · diagrams',PEACH)]
for i,(tag,h,b,col) in enumerate(stack):
    y=1.72+i*1.18;rect(s,.85,y,11.65,.9,WHITE);rect(s,1.05,y+.17,1.5,.54,col,col);textbox(s,1.15,y+.34,1.3,.16,tag,9,WHITE,True,align=PP_ALIGN.CENTER);textbox(s,2.86,y+.21,2.85,.3,h,17,NAVY,True);textbox(s,6.2,y+.25,5.5,.27,b,12,MUTED)

# 8 architecture
s=base('System architecture',num=8)
nodes=[(.75,2.3,2.1,.92,'Browser UI','React + Vite',RGBColor(231,244,237)),(3.65,2.3,2.25,.92,'REST API','Express + Zod',RGBColor(230,239,248)),(7.0,1.8,2.45,.92,'Demo repository','JSON local store',RGBColor(248,239,226)),(7.0,3.15,2.45,.92,'Prisma adapter','Planned runtime link',RGBColor(241,236,248)),(10.35,3.15,2.15,.92,'PostgreSQL','Local / Neon',RGBColor(231,242,228))]
for x,y,w,h,a,b,c in nodes:
    rect(s,x,y,w,h,WHITE);rect(s,x,y,w,.09,c,c,False);textbox(s,x+.16,y+.19,w-.3,.25,a,14,NAVY,True);textbox(s,x+.16,y+.54,w-.3,.2,b,9,MUTED)
line(s,2.9,2.76,3.57,2.76,TEAL,2,True);line(s,5.93,2.63,6.91,2.25,TEAL,1.8,True);line(s,5.93,2.9,6.91,3.55,BLUE,1.8,True);line(s,9.53,3.61,10.25,3.61,BLUE,1.8,True)
rect(s,.92,4.75,11.35,.77,NAVY,NAVY);textbox(s,1.17,5.02,10.9,.25,'Cross-cutting controls: JWT authorization · password hashing · rate limiting · audit events · demo-only payments',12,WHITE,True,align=PP_ALIGN.CENTER)

# 9 ER model
s=base('Relational model: eight connected records.',num=9)
boxes=[(.72,1.72,2.15,.8,'USER','role · email · hash'),(3.55,1.72,2.15,.8,'DONOR','contact profile'),(6.35,1.72,2.15,.8,'DONATION','amount · status'),(9.22,1.72,2.15,.8,'CAMPAIGN','goal · dates'),(3.0,4.05,2.25,.8,'REFRESH TOKEN','hash · expiry'),(6.0,4.05,2.15,.8,'PAYMENT ATTEMPT','sequence · result'),(9.0,4.05,1.8,.8,'RECEIPT','unique number'),(11.2,4.05,1.35,.8,'AUDIT LOG','actor · action')]
for x,y,w,h,a,b in boxes:
    rect(s,x,y,w,h,WHITE);textbox(s,x+.1,y+.12,w-.2,.2,a,9,TEAL,True,align=PP_ALIGN.CENTER);textbox(s,x+.08,y+.42,w-.16,.18,b,8,MUTED,align=PP_ALIGN.CENTER)
line(s,2.92,2.12,3.48,2.12,TEAL,1.5);line(s,5.72,2.12,6.27,2.12,TEAL,1.5);line(s,8.52,2.12,9.14,2.12,TEAL,1.5);line(s,7.42,2.56,7.18,3.96,TEAL,1.4);line(s,8.35,2.56,9.73,3.96,TEAL,1.4);line(s,4.53,2.56,4.1,3.96,BLUE,1.4);line(s,8.82,2.56,11.84,3.96,GOLD,1.3)
textbox(s,.85,5.38,11.2,.48,'UUID keys · Foreign keys · Unique receipt / transaction references · DECIMAL(12,2) monetary values',13,NAVY,True)

# 10 modules
s=base('Application modules',num=10)
mods=[('01','Authentication','Sign-in · registration · roles'),('02','Campaigns','Goals · status · progress'),('03','Donations','Anonymous · identified · history'),('04','Demo payments','Success · failure · retry'),('05','Receipts','Unique number · printable'),('06','Analytics','Dashboard · CSV · campaign view'),('07','Donor records','Search · contribution history'),('08','Audit & profile','Activity trail · account settings')]
for i,(n,h,b) in enumerate(mods):
    c=i%4;r=i//4;x=.67+c*3.13;y=1.72+r*2.15;rect(s,x,y,2.82,1.76,WHITE);textbox(s,x+.18,y+.16,.5,.25,n,10,TEAL,True);textbox(s,x+.18,y+.58,2.45,.34,h,15,NAVY,True,'Aptos Display');textbox(s,x+.18,y+1.08,2.42,.48,b,10,MUTED)

# 11 workflow
s=base('Donation workflow',num=11)
steps=[('01','Choose a cause'),('02','Enter gift details'),('03','Create pending gift'),('04','Simulate outcome'),('05','Record attempt'),('06','Issue receipt only on success')]
for i,(n,t) in enumerate(steps):
    x=.66+i*2.12;rect(s,x,2.26,1.79,1.55,WHITE);circle(s,x+.62,2.02,.5,MINT);textbox(s,x+.62,2.19,.5,.18,n,10,TEAL,True,align=PP_ALIGN.CENTER);textbox(s,x+.16,2.82,1.48,.65,t,12,NAVY,True,align=PP_ALIGN.CENTER)
    if i<5:line(s,x+1.8,3.02,x+2.06,3.02,TEAL,1.8,True)
rect(s,.88,4.65,5.55,1.03,RGBColor(232,245,238),RGBColor(232,245,238));textbox(s,1.1,4.92,1.55,.22,'SUCCESS',10,GREEN,True);textbox(s,2.55,4.86,3.55,.3,'Donation status + receipt number',12,NAVY,True)
rect(s,6.83,4.65,5.55,1.03,RGBColor(250,239,232),RGBColor(250,239,232));textbox(s,7.05,4.92,1.45,.22,'FAILURE',10,PEACH,True);textbox(s,8.47,4.86,3.58,.3,'Donation status + retry path; no receipt',12,NAVY,True)

# 12 screenshots UI mockups
s=base('Product preview: public giving and admin workspace',num=12)
# Public window
rect(s,.55,1.68,5.95,4.78,WHITE);rect(s,.55,1.68,5.95,.34,NAVY,NAVY,False);circle(s,.75,1.79,.08,PEACH);circle(s,.91,1.79,.08,GOLD);circle(s,1.07,1.79,.08,GREEN);textbox(s,1.45,1.76,3,.15,'goodwill · public campaign view',8,WHITE)
textbox(s,.91,2.24,2.1,.18,'A LITTLE GOOD GOES A LONG WAY',7,TEAL,True);textbox(s,.91,2.64,2.6,1.1,'Make kindness\ngo further.',22,NAVY,True,'Aptos Display');textbox(s,.92,3.83,2.45,.6,'Choose a cause close to your heart and be part of what is possible.',8,MUTED);rect(s,.91,4.58,1.55,.36,TEAL,TEAL);textbox(s,1.05,4.69,1.28,.12,'Explore our causes →',7,WHITE,True)
rect(s,3.75,2.14,2.36,3.85,MINT,MINT);circle(s,4.34,2.64,1.15,RGBColor(183,214,196));textbox(s,4.12,3.05,1.62,.36,'💧',26,TEAL,True,align=PP_ALIGN.CENTER);textbox(s,4.04,4.04,1.8,.22,'Clean Water for All',10,NAVY,True);textbox(s,4.04,4.45,1.8,.18,'$34,750 raised · 69%',8,MUTED);rect(s,4.04,4.82,1.8,.08,RGBColor(193,218,205),RGBColor(193,218,205),False);rect(s,4.04,4.82,1.24,.08,TEAL,TEAL,False)
# Admin window
rect(s,6.82,1.68,5.95,4.78,WHITE);rect(s,6.82,1.68,5.95,.34,NAVY,NAVY,False);circle(s,7.02,1.79,.08,PEACH);circle(s,7.18,1.79,.08,GOLD);circle(s,7.34,1.79,.08,GREEN);textbox(s,7.72,1.76,3,.15,'goodwill · admin dashboard',8,WHITE)
rect(s,6.82,2.02,.86,4.43,RGBColor(248,250,248),RGBColor(248,250,248),False);textbox(s,6.98,2.23,.55,.17,'Overview',7,TEAL,True);textbox(s,6.98,2.65,.55,.16,'Donors',7,MUTED);textbox(s,6.98,3.03,.55,.16,'Campaigns',7,MUTED);textbox(s,6.98,3.41,.55,.16,'Reports',7,MUTED)
for i,(a,b) in enumerate([('$125k','Giving'),('1,248','Donors'),('5','Causes')]):
    x=7.89+i*1.47;rect(s,x,2.26,1.31,.85,PALE,PALE);textbox(s,x+.1,2.4,1.1,.26,a,14,NAVY,True);textbox(s,x+.1,2.78,1.1,.14,b,7,MUTED)
rect(s,7.89,3.35,4.42,2.55,PALE,PALE);textbox(s,8.08,3.51,3,.18,'Giving over time',8,NAVY,True)
for i,h in enumerate([.55,.85,.72,1.2,1.38,1.7,1.52]):line(s,8.25+i*.53,5.45,8.25+i*.53,5.45-h,TEAL,4)
textbox(s,.8,6.61,11.7,.2,'Editable interface illustrations built from PowerPoint shapes. Browser screenshots were unavailable in the build environment.',8,MUTED)

# 13 testing
s=base('Testing approach',num=13)
rect(s,.72,1.78,5.68,3.98,WHITE);textbox(s,1.02,2.05,4.9,.32,'API checks included',18,NAVY,True,'Aptos Display')
for i,t in enumerate(['Health endpoint responds','Admin sign-in returns role token','Public campaign catalogue loads','Success creates receipt and reference','Failure does not create receipt','Admin gate and CSV export','Invalid amount is rejected']):bullet(s,1.07,2.65+i*.39,4.8,t,TEAL,11)
rect(s,6.75,1.78,5.68,3.98,NAVY,NAVY);textbox(s,7.08,2.05,4.9,.32,'Verification status',18,WHITE,True,'Aptos Display')
textbox(s,7.1,2.78,4.75,.62,'Runtime dependencies could not be installed in this environment.',15,RGBColor(211,227,224),True)
textbox(s,7.1,3.65,4.75,1.13,'The project includes API tests and build scripts, but automated results must be confirmed after npm install succeeds. PostgreSQL migration execution also needs a reachable database.',11,RGBColor(172,195,198))

# 14 future
s=base('Future enhancements',num=14)
future=[('Complete Prisma runtime adapter','Use Prisma transactions for attempt completion, receipt issuance and reports.'),('Issue PDF files directly','Generate downloadable receipt PDFs with verified organization details.'),('Expand quality coverage','Add browser journey tests, donor privacy cases and concurrency tests.'),('Production operations','Add observability, backups, deployment configuration and secret management.')]
for i,(h,b) in enumerate(future):
    x=.78+(i%2)*6.0;y=1.82+(i//2)*2.08;rect(s,x,y,5.58,1.66,WHITE);circle(s,x+.22,y+.26,.42,MINT);textbox(s,x+.22,y+.38,.42,.16,'↗',14,TEAL,True,align=PP_ALIGN.CENTER);textbox(s,x+.82,y+.22,4.35,.33,h,15,NAVY,True);textbox(s,x+.82,y+.72,4.28,.64,b,11,MUTED)

# 15 conclusion
s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=NAVY
circle(s,9.4,1.35,3.2,RGBColor(22,80,87));circle(s,10.14,2.1,1.72,TEAL);circle(s,10.65,2.61,.7,MINT)
textbox(s,.88,.84,6,.3,'GOODWILL · DONATION MANAGEMENT SYSTEM',10,RGBColor(148,219,200),True)
textbox(s,.88,1.85,7.3,.88,'Good giving,\nmade visible.',39,WHITE,True,'Aptos Display')
textbox(s,.91,4.1,6.6,.78,'A connected foundation for transparent campaigns, thoughtful donor care, accountable reporting, and safe simulated checkout.',16,RGBColor(198,216,218))
line(s,.9,5.55,7.15,5.55,RGBColor(54,100,108),1)
textbox(s,.92,5.84,5.9,.3,'Thank you.',17,RGBColor(148,219,200),True)
textbox(s,.92,6.86,6,.2,'Project submission · 2026',9,RGBColor(164,191,194))

prs.save(OUT)
print(f'Created {OUT} ({len(prs.slides)} editable slides)')
