from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DIAGRAMS = DOCS / "diagrams"
RENDERED = DIAGRAMS / "rendered"
SCHEMA = ROOT / "server/prisma/schema.prisma"

NAVY = "102A43"
TEAL = "168C8A"
PALE = "E7F5F0"
INK = "253B4A"
MUTED = "647887"
LINE = "CFDDE2"
BLUE = "EAF1F8"
GOLD = "F8F0DB"
WHITE = "FFFFFF"


def font(size: int, bold: bool = False):
    candidates = ["C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
                  "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"]
    for item in candidates:
        if Path(item).exists():
            return ImageFont.truetype(item, size)
    return ImageFont.load_default()


def esc(value):
    return html.escape(str(value))


def wrap(text, width, f):
    words = str(text).split()
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if line and ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(candidate, font=f) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def render_diagram(name, title, subtitle, nodes, edges, cols=3, node_w=360, node_h=136):
    pad, gap_x, gap_y = 60, 34, 54
    rows = (len(nodes) + cols - 1) // cols
    width = pad * 2 + cols * node_w + (cols - 1) * gap_x
    height = 154 + rows * node_h + (rows - 1) * gap_y + 70
    positions = {}
    for i, node in enumerate(nodes):
        row, col = divmod(i, cols)
        positions[node["id"]] = (pad + col * (node_w + gap_x), 138 + row * (node_h + gap_y))

    # SVG uses the same geometry as the PNG fallback embedded in the report.
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#168C8A"/></marker></defs>',
           f'<rect width="100%" height="100%" rx="24" fill="#{WHITE}"/>',
           f'<text x="{pad}" y="54" font-family="Arial" font-size="30" font-weight="700" fill="#{NAVY}">{esc(title)}</text>',
           f'<text x="{pad}" y="88" font-family="Arial" font-size="16" fill="#{MUTED}">{esc(subtitle)}</text>']
    img = Image.new("RGB", (width, height), "#" + WHITE)
    draw = ImageDraw.Draw(img)
    draw.text((pad, 27), title, font=font(30, True), fill="#" + NAVY)
    draw.text((pad, 70), subtitle, font=font(16), fill="#" + MUTED)

    # Draw edge lines first so connectors remain behind entity cards.
    for edge in edges:
        src, dst, label = edge
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        sx, sy = x1 + node_w // 2, y1 + node_h // 2
        ex, ey = x2 + node_w // 2, y2 + node_h // 2
        if abs(ex - sx) > abs(ey - sy):
            sx = x1 + node_w if ex > sx else x1
            ex = x2 if ex > sx else x2 + node_w
            sy, ey = y1 + node_h // 2, y2 + node_h // 2
        else:
            sy = y1 + node_h if ey > sy else y1
            ey = y2 if ey > sy else y2 + node_h
            sx, ex = x1 + node_w // 2, x2 + node_w // 2
        # Simple two-segment elbow routes keep arrows legible in the compact diagrams.
        if abs(ex - sx) > abs(ey - sy):
            mid = (sx + ex) // 2
            pts = [(sx, sy), (mid, sy), (mid, ey), (ex - (10 if ex > sx else -10), ey)]
        else:
            mid = (sy + ey) // 2
            pts = [(sx, sy), (sx, mid), (ex, mid), (ex, ey - (10 if ey > sy else -10))]
        path = "M " + " L ".join(f"{x} {y}" for x, y in pts)
        svg.append(f'<path d="{path}" fill="none" stroke="#{TEAL}" stroke-width="2.2" marker-end="url(#arr)"/>')
        draw.line(pts, fill="#" + TEAL, width=3, joint="curve")
        x, y = pts[1]
        if label:
            label_f = font(12, True)
            svg.append(f'<text x="{x + 5}" y="{y - 6}" font-family="Arial" font-size="12" fill="#{NAVY}">{esc(label)}</text>')
            draw.text((x + 5, y - 19), label, font=label_f, fill="#" + NAVY)
        # arrow head
        tipx, tipy = pts[-1]
        prevx, prevy = pts[-2]
        if abs(tipx - prevx) >= abs(tipy - prevy):
            sign = 1 if tipx > prevx else -1
            poly = [(tipx, tipy), (tipx - 12 * sign, tipy - 7), (tipx - 12 * sign, tipy + 7)]
        else:
            sign = 1 if tipy > prevy else -1
            poly = [(tipx, tipy), (tipx - 7, tipy - 12 * sign), (tipx + 7, tipy - 12 * sign)]
        draw.polygon(poly, fill="#" + TEAL)

    for node in nodes:
        x, y = positions[node["id"]]
        kind = node.get("kind", "process")
        bg = {"actor": "#" + GOLD, "data": "#" + BLUE, "entity": "#" + PALE, "process": "#" + WHITE}.get(kind, "#" + WHITE)
        border = "#" + NAVY if kind == "actor" else "#" + TEAL
        if kind == "data":
            draw.rounded_rectangle((x, y, x + node_w, y + node_h), radius=7, fill=bg, outline=border, width=3)
            draw.line((x + 9, y + 32, x + node_w - 9, y + 32), fill=border, width=2)
            svg.append(f'<rect x="{x}" y="{y}" width="{node_w}" height="{node_h}" rx="7" fill="{bg}" stroke="{border}" stroke-width="2"/>')
            svg.append(f'<path d="M{x+9} {y+34} H{x+node_w-9}" stroke="{border}" stroke-width="2"/>')
        else:
            draw.rounded_rectangle((x, y, x + node_w, y + node_h), radius=15, fill=bg, outline=border, width=3)
            svg.append(f'<rect x="{x}" y="{y}" width="{node_w}" height="{node_h}" rx="15" fill="{bg}" stroke="{border}" stroke-width="2"/>')
        head = font(18, True)
        svg.append(f'<text x="{x+18}" y="{y+29}" font-family="Arial" font-size="18" font-weight="700" fill="#{NAVY}">{esc(node["title"])}</text>')
        draw.text((x + 18, y + 12), node["title"], font=head, fill="#" + NAVY)
        lines = []
        for item in node.get("body", []):
            lines.extend(wrap(item, node_w - 34, font(13)))
        base_y = y + 42
        for j, line in enumerate(lines[:5]):
            svg.append(f'<text x="{x+18}" y="{base_y+17*j}" font-family="Arial" font-size="13" fill="#{INK}">{esc(line)}</text>')
            draw.text((x + 18, base_y + 16 * j), line, font=font(13), fill="#" + INK)
    (RENDERED / f"{name}.svg").write_text("\n".join(svg + ["</svg>"]), encoding="utf-8")
    img.save(RENDERED / f"{name}.png", dpi=(160, 160))


def render_architecture_diagram():
    """Render a UML deployment view with deployment nodes and contained artifacts."""
    width, height = 1740, 930
    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    def tnr(size, bold=False):
        path = "C:/Windows/Fonts/timesbd.ttf" if bold else "C:/Windows/Fonts/times.ttf"
        return ImageFont.truetype(path, size) if Path(path).exists() else font(size, bold)
    title_font, body_font, small_font = tnr(35, True), tnr(22), tnr(18)
    navy, teal, pale, blue, ink, muted = "#"+NAVY, "#"+TEAL, "#"+PALE, "#"+BLUE, "#"+INK, "#"+MUTED
    draw.text((70, 40), "Deployment Architecture", font=title_font, fill=navy)
    draw.text((70, 90), "UML deployment view · HTTPS request path and runtime components", font=body_font, fill=muted)

    # Each deployment node uses a folded corner and stereotype label, as in UML tools.
    boxes = {
      "browser": (55, 340, 320, 270, "<<device>>", "Donor / administrator", ["Web browser", "React client", "HTTPS request / response"]),
      "vercel": (405, 290, 320, 370, "<<cloud>>", "Vercel", ["Static web application", "SPA route handling", "/api rewrite"]),
      "render": (865, 180, 430, 590, "<<node>>", "Render application service", ["<<artifact>> Express REST API", "Authentication + validation", "Campaign / donation routes", "Receipt, reports, support", "<<component>> Demo payment simulator"]),
      "database": (1420, 340, 270, 270, "<<database>>", "Neon PostgreSQL", ["Prisma data access", "Relational records", "Migration-managed schema"]),
    }
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#168C8A"/></marker></defs>',
           f'<rect width="100%" height="100%" fill="#FFFFFF"/>',
           f'<text x="70" y="78" font-family="Times New Roman,serif" font-size="35" font-weight="700" fill="{navy}">Deployment Architecture</text>',
           f'<text x="70" y="120" font-family="Times New Roman,serif" font-size="22" fill="{muted}">UML deployment view · HTTPS request path and runtime components</text>']
    for key, (x,y,w,h,stereo,label,items) in boxes.items():
        fill = pale if key in {"browser","database"} else blue
        draw.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=fill,outline=navy,width=4)
        # Folded upper-right corner signals a UML deployment node.
        fold=34
        draw.line((x+w-fold,y,x+w-fold,y+fold,x+w,y+fold),fill=navy,width=3)
        draw.line((x+w-fold,y,x+w,y+fold),fill=navy,width=2)
        draw.text((x+18,y+18),stereo,font=small_font,fill=teal)
        draw.text((x+18,y+50),label,font=tnr(24,True),fill=navy)
        svg.extend([f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{navy}" stroke-width="4"/>',
                    f'<path d="M{x+w-fold} {y} V{y+fold} H{x+w} M{x+w-fold} {y} L{x+w} {y+fold}" fill="none" stroke="{navy}" stroke-width="3"/>',
                    f'<text x="{x+18}" y="{y+39}" font-family="Times New Roman,serif" font-size="18" fill="{teal}">{esc(stereo)}</text>',
                    f'<text x="{x+18}" y="{y+75}" font-family="Times New Roman,serif" font-weight="700" font-size="24" fill="{navy}">{esc(label)}</text>'])
        for j,item in enumerate(items):
            yy=y+97+j*57
            draw.rounded_rectangle((x+18,yy-5,x+w-18,yy+45),radius=6,fill="#FFFFFF",outline=teal,width=2)
            draw.text((x+30,yy+7),item,font=small_font,fill=ink)
            svg.append(f'<rect x="{x+18}" y="{yy-5}" width="{w-36}" height="50" rx="6" fill="#FFFFFF" stroke="{teal}" stroke-width="2"/>')
            svg.append(f'<text x="{x+30}" y="{yy+27}" font-family="Times New Roman,serif" font-size="18" fill="{ink}">{esc(item)}</text>')

    links = [((375,470),(405,470),"HTTPS"), ((725,470),(865,470),"/api rewrite"), ((1295,470),(1420,470),"Prisma / SQL")]
    for (x1,y1),(x2,y2),label in links:
        draw.line((x1,y1,x2,y2),fill=teal,width=5)
        if x2 > x1:
            draw.polygon([(x2,y2),(x2-15,y2-9),(x2-15,y2+9)],fill=teal)
        box=draw.textbbox((0,0),label,font=small_font); tw=box[2]-box[0]
        draw.rounded_rectangle(((x1+x2-tw)//2-9,y1-43,(x1+x2+tw)//2+9,y1-10),radius=8,fill="#FFFFFF")
        draw.text(((x1+x2-tw)//2,y1-42),label,font=small_font,fill=navy)
        svg.append(f'<path d="M{x1} {y1} H{x2-12}" stroke="{teal}" stroke-width="5" marker-end="url(#arrow)"/>')
        svg.append(f'<text x="{(x1+x2)//2}" y="{y1-18}" text-anchor="middle" font-family="Times New Roman,serif" font-size="18" fill="{navy}">{esc(label)}</text>')
    draw.text((70, 835), "Persistent mode uses PostgreSQL; JSON demo mode is a separate runtime option. Payment handling is simulated.", font=small_font, fill=muted)
    svg.append(f'<text x="70" y="870" font-family="Times New Roman,serif" font-size="18" fill="{muted}">Persistent mode uses PostgreSQL; JSON demo mode is a separate runtime option. Payment handling is simulated.</text>')
    svg.append("</svg>")
    img.save(RENDERED / "system-architecture.png", dpi=(160,160))
    (RENDERED / "system-architecture.svg").write_text("\n".join(svg),encoding="utf-8")


def render_use_case_diagram():
    """Create a clear UML use-case view with actors, boundary, and UML relations."""
    width, height = 1800, 1240
    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    def tnr(size, bold=False):
        path = "C:/Windows/Fonts/timesbd.ttf" if bold else "C:/Windows/Fonts/times.ttf"
        return ImageFont.truetype(path, size) if Path(path).exists() else font(size, bold)
    title_f, boundary_f, use_f, actor_f, rel_f = tnr(44, True), tnr(31, True), tnr(27), tnr(31, True), tnr(24)
    navy, teal, pale, ink, muted = "#"+NAVY, "#"+TEAL, "#"+BLUE, "#"+INK, "#"+MUTED
    draw.text((width//2, 35), "Goodwill Foundation — UML Use-Case Diagram", anchor="ma", font=title_f, fill=navy)
    # System boundary
    boundary=(250,165,1550,1095)
    draw.rounded_rectangle(boundary,radius=10,fill="#FFFFFF",outline=navy,width=4)
    draw.rectangle((252,167,1548,230),fill="#EAF1F8")
    draw.line((252,230,1548,230),fill=navy,width=3)
    draw.text((900,198),"Goodwill Donation Management System",anchor="mm",font=boundary_f,fill=navy)

    use_cases=[
      ("browse",300,275,"Browse and search campaigns"),
      ("auth",300,410,"Register or sign in"),
      ("donate",300,545,"Submit a donation"),
      ("history",300,680,"View own donations and receipts"),
      ("profile",300,815,"Manage profile and preferences"),
      ("saved",300,950,"Save / follow causes and request support"),
      ("campaign_admin",960,275,"Manage campaigns and donors"),
      ("reports",960,410,"Review donations and reports"),
      ("support_admin",960,545,"Respond to support / deletion requests"),
      ("validate",960,680,"Validate gift and campaign details"),
      ("payment",960,815,"Simulate payment outcome"),
      ("receipt",960,950,"Issue receipt after successful payment"),
    ]
    # Associations are drawn first so they sit behind the UML ovals.
    guest_anchor=(190,372)
    donor_anchor=(190,792)
    admin_anchor=(1610,612)
    actor_links={
      "guest":["browse","auth","donate"],
      "donor":["browse","donate","history","profile","saved"],
      "admin":["campaign_admin","reports","support_admin"],
    }
    coords={name:(x,y,540,96) for name,x,y,label in use_cases}
    for actor, names in actor_links.items():
        ax,ay=guest_anchor if actor=="guest" else donor_anchor if actor=="donor" else admin_anchor
        for idx,name in enumerate(names):
            x,y,w,h=coords[name]
            start=(ax,ay)
            end=(x,y+h/2) if actor!="admin" else (x+w,y+h/2)
            draw.line((start,end),fill=muted,width=3)

    # Draw three UML stick-figure actors outside the system boundary.
    def actor(cx,top,label):
        r=26; head_y=top+r
        draw.ellipse((cx-r,top,cx+r,top+2*r),outline=navy,width=4)
        draw.line((cx,top+2*r,cx,top+112),fill=navy,width=4)
        draw.line((cx-45,top+72,cx+45,top+72),fill=navy,width=4)
        draw.line((cx,top+112,cx-38,top+165),fill=navy,width=4)
        draw.line((cx,top+112,cx+38,top+165),fill=navy,width=4)
        draw.text((cx,top+180),label,anchor="ma",font=actor_f,fill=navy)
        return [f'<circle cx="{cx}" cy="{head_y}" r="{r}" fill="#FFFFFF" stroke="{navy}" stroke-width="4"/>',
                f'<path d="M{cx} {top+2*r} V{top+112} M{cx-45} {top+72} H{cx+45} M{cx} {top+112} L{cx-38} {top+165} M{cx} {top+112} L{cx+38} {top+165}" fill="none" stroke="{navy}" stroke-width="4"/>',
                f'<text x="{cx}" y="{top+220}" text-anchor="middle" font-family="Times New Roman,serif" font-size="31" font-weight="700" fill="{navy}">{esc(label)}</text>']
    actor_svg=[]
    actor_svg.extend(actor(145,300,"Guest"))
    actor_svg.extend(actor(145,720,"Donor"))
    actor_svg.extend(actor(1655,540,"Administrator"))

    # Use cases: ellipses inside the application boundary.
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<defs><marker id="use-arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#168C8A"/></marker></defs>',
         '<rect width="100%" height="100%" fill="#FFFFFF"/>',
         f'<text x="900" y="80" text-anchor="middle" font-family="Times New Roman,serif" font-size="44" font-weight="700" fill="{navy}">Goodwill Foundation — UML Use-Case Diagram</text>',
         f'<rect x="{boundary[0]}" y="{boundary[1]}" width="{boundary[2]-boundary[0]}" height="{boundary[3]-boundary[1]}" rx="10" fill="#FFFFFF" stroke="{navy}" stroke-width="4"/>',
         f'<rect x="252" y="167" width="1296" height="63" fill="#EAF1F8"/><path d="M252 230 H1548" stroke="{navy}" stroke-width="3"/>',
         f'<text x="900" y="210" text-anchor="middle" font-family="Times New Roman,serif" font-size="31" font-weight="700" fill="{navy}">Goodwill Donation Management System</text>']
    for actor,names in actor_links.items():
        ax,ay=guest_anchor if actor=="guest" else donor_anchor if actor=="donor" else admin_anchor
        for idx,name in enumerate(names):
            x,y,w,h=coords[name]
            sy=ay
            ex,ey=(x,y+h/2) if actor!="admin" else (x+w,y+h/2)
            svg.append(f'<path d="M{ax} {sy} L{ex} {ey}" fill="none" stroke="{muted}" stroke-width="3"/>')
    svg.extend(actor_svg)
    for _,x,y,label in use_cases:
        draw.ellipse((x,y,x+540,y+96),fill=pale,outline=teal,width=4)
        # Wrap long use-case titles into two centered lines when necessary.
        lines=wrap(label,495,use_f)
        base=y+47-(len(lines)-1)*17
        for i,line in enumerate(lines): draw.text((x+270,base+i*36),line,anchor="mm",font=use_f,fill=ink)
        svg.append(f'<ellipse cx="{x+270}" cy="{y+48}" rx="270" ry="48" fill="{pale}" stroke="{teal}" stroke-width="4"/>')
        lines=wrap(label,495,use_f)
        base=y+47-(len(lines)-1)*17
        for i,line in enumerate(lines):
            svg.append(f'<text x="{x+270}" y="{base+i*36+9}" text-anchor="middle" font-family="Times New Roman,serif" font-size="27" fill="{ink}">{esc(line)}</text>')
    draw.text((900,1145),"Donation is validated and simulated; a receipt is issued only after success.",anchor="mm",font=rel_f,fill=muted)
    svg.append(f'<text x="900" y="1153" text-anchor="middle" font-family="Times New Roman,serif" font-size="24" fill="{muted}">Donation is validated and simulated; a receipt is issued only after success.</text>')
    svg.append("</svg>")
    img.save(RENDERED / "use-case-diagram.png",dpi=(160,160))
    (RENDERED / "use-case-diagram.svg").write_text("\n".join(svg),encoding="utf-8")
    (DIAGRAMS / "use-case-diagram.puml").write_text("""@startuml
left to right direction
actor Guest
actor Donor
actor Administrator
rectangle "Goodwill Donation Management System" {
  usecase "Browse and search campaigns" as Browse
  usecase "Register or sign in" as Auth
  usecase "Submit a donation" as Donate
  usecase "View own donations and receipts" as History
  usecase "Manage profile and preferences" as Profile
  usecase "Save / follow causes and request support" as Saved
  usecase "Manage campaigns and donors" as CampaignAdmin
  usecase "Review donations and reports" as Reports
  usecase "Respond to support / deletion requests" as AdminSupport
  usecase "Validate gift and campaign details" as Validate
  usecase "Simulate payment outcome" as Payment
  usecase "Issue receipt after successful payment" as Receipt
  note bottom: Donation is validated and simulated; a receipt is issued only after success.
}
Guest -- Browse
Guest -- Auth
Guest -- Donate
Donor -- Browse
Donor -- Donate
Donor -- History
Donor -- Profile
Donor -- Saved
Administrator -- CampaignAdmin
Administrator -- Reports
Administrator -- AdminSupport
@enduml
""",encoding="utf-8")


def create_diagrams():
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    RENDERED.mkdir(parents=True, exist_ok=True)
    diagrams = {
      "system-architecture": ("System architecture", "Browser UI → Vercel → Render API → Prisma → PostgreSQL", [
        ("browser", "Browser client", ["React 18 + Vite", "React Router, Axios, Recharts"]),
        ("vercel", "Vercel", ["Static client assets", "/api requests rewritten to Render"]),
        ("api", "Express API on Render", ["REST endpoints", "Helmet, CORS, rate limiting"]),
        ("middleware", "Request controls", ["JWT authentication", "Role checks + Zod validation"]),
        ("logic", "Application workflows", ["Campaign, donor, donation", "Receipt, report, support"]),
        ("sim", "Payment simulator", ["Demo success/failure only", "No real payment network"]),
        ("prisma", "Prisma ORM", ["Schema + migrations", "Transactions and constraints"]),
        ("postgres", "Neon PostgreSQL", ["Persistent relational records", "DATABASE_URL at runtime"]),
      ], [("browser","vercel","HTTPS"),("vercel","api","/api proxy"),("api","middleware","request"),("middleware","logic","authorized request"),("logic","sim","demo attempt"),("logic","prisma","query/write"),("sim","logic","outcome"),("prisma","postgres","SQL")], 2),
      "application-workflow": ("Main application workflow", "Public browsing, giving, donor services, and administrator operations", [
        ("guest","Guest",["Browse active campaigns","May give without account"]),
        ("campaign","Campaign selection",["Choose a cause","Check active status and amount"]),
        ("auth","Account access",["Register or sign in","JWT + role scope"]),
        ("donation","Create donation",["Validate campaign and amount","Record demo payment attempt"]),
        ("decision","Outcome",["Success or failure","Retry available after failure"]),
        ("receipt","Receipt and history",["Receipt only on success","Donor sees own records"]),
        ("admin","Admin workspace",["Manage campaigns and donors","Reports, activity, support"]),
        ("store","PostgreSQL",["Prisma transaction","Audit and notification records"]),
      ], [("guest","campaign","public"),("campaign","auth","optional sign-in"),("auth","donation","authenticated or guest"),("donation","store","pending + attempt"),("donation","decision","simulated"),("decision","receipt","success only"),("decision","store","status + audit"),("admin","store","protected management")], 2),
      "activity-diagram": ("Donation activity", "A failed demo attempt is recorded without a receipt; retry can succeed later", [
        ("start","Start",["Open an active campaign"]),
        ("enter","Enter gift details",["Amount, name, email","Anonymous option if desired"]),
        ("validate","Validate",["Positive amount", "Active campaign + valid fields"]),
        ("invalid","Invalid",["Show validation error", "Return to form"]),
        ("create","Create donation",["Pending donation", "Create payment attempt"]),
        ("simulate","Simulate payment",["Demo card or bank", "Success or failure result"]),
        ("success","Successful",["Mark succeeded", "Record transaction reference"]),
        ("receipt","Issue receipt",["Unique receipt", "Update campaign totals"]),
        ("failed","Failed",["Mark failed", "No receipt; retry may be offered"]),
        ("end","Finish",["Show status and next step", "Guest or donor view"]),
      ], [("start","enter",""),("enter","validate","submit"),("validate","invalid","no"),("validate","create","yes"),("create","simulate",""),("simulate","success","success"),("success","receipt",""),("simulate","failed","failure"),("receipt","end",""),("failed","end","")], 2),
      "sequence-diagram": ("Donation sequence", "Transaction boundary protects the successful donation, attempt, campaign total, receipt, and audit", [
        ("donor","Donor",["Chooses active campaign"]),
        ("react","React client",["Submits gift payload"]),
        ("express","Express API",["Helmet / limiter", "JWT optional for guest"]),
        ("zod","Validation",["Zod request schema", "Campaign / owner checks"]),
        ("service","Donation workflow",["Creates pending record", "Invokes demo processor"]),
        ("payment","Demo payment",["Returns success/failure", "Reference for attempt"]),
        ("prisma","Prisma transaction",["Commits success atomically", "Failure records failed attempt"]),
        ("db","PostgreSQL",["Donation + attempts", "Receipt + audit/notification"]),
      ], [("donor","react","gift details"),("react","express","POST /api/donations"),("express","zod","parse and authorize"),("zod","service","valid payload"),("service","payment","simulate"),("payment","service","result"),("service","prisma","success/failure branch"),("prisma","db","transaction"),("db","react","response + receipt")], 2),
      "dfd-level-0": ("DFD Level 0 Context", "One Goodwill system exchanges campaign, gift, receipt, and management information with three actors", [
        ("guest","Guest",["Campaign search", "Optional gift details"]),
        ("donor","Donor",["Credentials + profile", "Own history / receipt"]),
        ("admin","Administrator",["Management commands", "Dashboard / reports"]),
        ("system","Goodwill DMS",["REST application", "Demo payment outcome"]),
        ("gateway","Demo payment simulator",["Success/failure outcome", "Transaction reference"]),
      ], [("guest","system","browse / give"),("system","guest","causes / outcome"),("donor","system","account / giving"),("system","donor","history / receipt"),("admin","system","manage / report"),("system","admin","dashboard / export"),("system","gateway","demo request"),("gateway","system","simulated result")], 2),
      "dfd-level-1": ("DFD Level 1 Data Flow", "Processes map to the application routes and PostgreSQL models", [
        ("actors","Actors",["Guest, donor, administrator"]),
        ("auth","1. Identity and access",["Register, login, refresh", "Role and ownership checks"]),
        ("campaigns","2. Campaign service",["Browse public causes", "Admin create/update/pause"]),
        ("donations","3. Donation service",["Validate amount and campaign", "Persist payment attempt"]),
        ("payment","4. Payment simulation",["Successful or failed demo", "No external processor"]),
        ("receipts","5. Receipts and impact",["Success-only receipt", "Donor history / statements"]),
        ("reports","6. Reports and support",["Admin exports / audit", "Donor tickets / notifications"]),
        ("db","PostgreSQL stores",["Users, donors, campaigns", "Donations, receipt, support, audit"]),
      ], [("actors","auth","credentials"),("actors","campaigns","search / updates"),("actors","donations","gift request"),("donations","payment","attempt"),("payment","donations","result"),("donations","db","persist"),("campaigns","db","read/write"),("auth","db","user/session"),("receipts","db","receipt/history"),("reports","db","report/support"),("actors","receipts","request"),("actors","reports","admin / donor actions")], 2),
      "use-case-diagram": ("Use cases and roles", "Solid associations show available actions; giving includes validation and demo processing", [
        ("guest","Guest",["Browse causes", "Register / sign in", "Make demo gift"]),
        ("donor","Donor",["Manage profile/preferences", "View own gifts and receipts", "Save/follow causes", "Support ticket + privacy tools"]),
        ("admin","Administrator",["Dashboard and reports", "Manage causes and donors", "Review gifts, receipts, activity", "Support and deletion review"]),
        ("browse","Browse causes",["Search / filter public campaigns"]),
        ("give","Make demo donation",["Guest or signed-in donor"]),
        ("validate","Validate gift",["Amount, campaign, contact"]),
        ("payment","Simulate payment",["Demo outcome + reference"]),
        ("receipt","Issue receipt",["Only when payment succeeds"]),
      ], [("guest","browse","association"),("guest","give","association"),("donor","browse","association"),("donor","give","association"),("donor","receipt","own receipt"),("admin","browse","manage"),("admin","receipt","review records"),("give","validate","include"),("give","payment","include"),("payment","receipt","success extends")], 2),
      "class-diagram": ("Domain class view", "Prisma models shown as domain classes; service methods remain in Express modules", [
        ("User","User",["id: UUID (PK)","email: String (unique)","passwordHash: String","role: Role; active: Boolean"]),
        ("Donor","Donor",["id: UUID (PK)","userId: UUID? (unique FK)","name, email, phone?","anonymous: Boolean"]),
        ("Campaign","Campaign",["id: UUID (PK)","slug: String (unique)","target: Decimal(12,2)","status, startsAt, endsAt"]),
        ("Donation","Donation",["id: UUID (PK)","campaignId: UUID (FK)","donorId: UUID? (FK)","amount, status, anonymous"]),
        ("PaymentAttempt","PaymentAttempt",["id: UUID (PK)","donationId: UUID (FK)","attemptNumber, status, method","reference: String (unique)"] ),
        ("Receipt","Receipt",["id: UUID (PK)","donationId: UUID (unique FK)","receiptNumber: String (unique)","issuedAt: DateTime"]),
        ("Notification","Notification",["userId FK; category; readAt?"]),
        ("AuditLog","AuditLog",["userId? FK; action; entity; metadata?"]),
        ("SupportTicket","SupportTicket",["userId FK; subject; category; status"]),
        ("SupportTicketReply","SupportTicketReply",["ticketId FK; userId? FK; body"]),
      ], [("User","Donor","1 — 0..1"),("Donor","Donation","1 — 0..*"),("Campaign","Donation","1 — 0..*"),("Donation","PaymentAttempt","1 — 0..*"),("Donation","Receipt","1 — 0..1"),("User","Notification","1 — 0..*"),("User","AuditLog","1 — 0..*"),("User","SupportTicket","1 — 0..*"),("SupportTicket","SupportTicketReply","1 — 0..*")], 2),
      "er-diagram": ("Entity relationship overview", "Core giving entities; 17 supporting entities are inventoried in the database chapter", [
        ("User","User",["PK id UUID","UQ email; role; passwordHash","active; tokenVersion; timestamps"]),
        ("Donor","Donor",["PK id UUID; FK userId? UQ","name; email; phone?; address?","anonymous; createdAt"]),
        ("Campaign","Campaign",["PK id UUID; UQ slug","title; category; target Decimal","status; startsAt; endsAt"]),
        ("Donation","Donation",["PK id UUID; FK campaignId","FK donorId?; amount; status","currency; anonymous; idempotencyKey?"]),
        ("PaymentAttempt","PaymentAttempt",["PK id UUID; FK donationId","attemptNumber; status; method","reference UQ; message?; createdAt"]),
        ("Receipt","Receipt",["PK id UUID; FK donationId UQ","receiptNumber UQ; issuedAt"]),
      ], [("User","Donor","1 : 0..1"),("Donor","Donation","1 : 0..*"),("Campaign","Donation","1 : 0..*"),("Donation","PaymentAttempt","1 : 0..*"),("Donation","Receipt","1 : 0..1")], 2),
    }
    mmd = {
      "system-architecture": "flowchart LR\n subgraph Client[\"<<device>> Donor or administrator\"]\n  Browser[Web browser]\n  React[React client]\n end\n subgraph Web[\"<<cloud>> Vercel\"]\n  Static[Static web application]\n  Rewrite[SPA routes and /api rewrite]\n end\n subgraph App[\"<<node>> Render application service\"]\n  API[<<artifact>> Express REST API]\n  Auth[Authentication and validation]\n  Routes[Campaign, donation, receipt, reports, support]\n  Pay[<<component>> Demo payment simulator]\n  API --> Auth --> Routes\n  Routes --> Pay\n end\n subgraph Data[\"<<database>> Neon PostgreSQL\"]\n  Prisma[Prisma data access]\n  DB[(Relational database)]\n  Prisma --> DB\n end\n Browser -->|HTTPS| Static\n Static --> Rewrite\n Rewrite -->|/api| API\n Routes --> Prisma\n Pay -->|Simulated result| Routes",
      "application-workflow": "flowchart LR\n Guest[Guest] --> Campaign[Browse active campaign]\n Donor[Donor] --> Campaign\n Campaign --> Auth[Optional registration or login]\n Auth --> Gift[Validate and create donation]\n Gift --> Payment{Demo payment result}\n Payment -->|Success| Receipt[Issue one receipt]\n Payment -->|Failure| Failed[Failed status; no receipt]\n Receipt --> History[Donor history and admin reports]\n Failed --> Retry[Retry may be offered]",
      "activity-diagram": "flowchart TD\n A([Start]) --> B[Select active campaign and enter amount]\n B --> C{Input valid?}\n C -->|No| D[Show validation error] --> B\n C -->|Yes| E[Create pending donation and attempt]\n E --> F{Demo result}\n F -->|Success| G[Mark successful and update campaign]\n G --> H[Create unique receipt and audit event] --> I([Show successful result])\n F -->|Failure| J[Mark failed; no receipt] --> K([Show failed result / retry])",
      "sequence-diagram": "sequenceDiagram\n actor Donor\n participant React\n participant API as Express API\n participant V as Validation and auth middleware\n participant S as Donation workflow\n participant P as Demo payment simulator\n participant ORM as Prisma\n participant DB as PostgreSQL\n Donor->>React: Submit campaign and gift\n React->>API: POST /api/donations\n API->>V: Apply security and Zod checks\n V->>S: Valid request\n S->>ORM: Create pending donation and attempt\n S->>P: Simulate payment\n P-->>S: Success or failure + reference\n alt Success\n S->>ORM: Transaction: success, totals, receipt, audit\n ORM->>DB: Commit\n else Failure\n S->>ORM: Record failed status; no receipt\n ORM->>DB: Commit failure attempt\n end\n API-->>React: Donation outcome and receipt if successful\n React-->>Donor: Display result",
      "dfd-level-0": "flowchart LR\n Guest[Guest] -->|Browse or gift| DMS((Goodwill Donation System))\n Donor[Donor] -->|Account and giving| DMS\n Admin[Administrator] -->|Manage and report| DMS\n DMS -->|Causes and outcome| Guest\n DMS -->|Own history and receipts| Donor\n DMS -->|Dashboard and exports| Admin\n DMS -->|Simulated request| Sim[Demo payment simulator]\n Sim -->|Outcome and reference| DMS",
      "dfd-level-1": "flowchart LR\n Actors[Guest / donor / admin] --> Auth((1 Identity and access))\n Auth <--> U[(User and session records)]\n Actors --> Camp((2 Campaign management))\n Camp <--> C[(Campaign records)]\n Actors --> Gift((3 Donation processing))\n Gift <--> D[(Donation and attempt records)]\n Gift --> Pay((4 Demo payment))\n Pay --> Gift\n Gift --> Receipt((5 Receipt and impact))\n Receipt <--> R[(Receipt records)]\n Actors --> Report((6 Reports, notifications, support))\n Report <--> A[(Audit, support, notification records)]",
      "use-case-diagram": "flowchart LR\n Guest([Guest])\n Donor([Donor])\n Admin([Administrator])\n subgraph System[Goodwill Donation Management System]\n  Browse([Browse and search campaigns])\n  Auth([Register or sign in])\n  Donate([Submit a donation])\n  History([View own donations and receipts])\n  Profile([Manage profile and preferences])\n  Saved([Save or follow causes; request support])\n  Campaigns([Manage campaigns and donors])\n  Reports([Review donations and reports])\n  AdminSupport([Respond to support or deletion requests])\n  Validate([Validate gift and campaign details])\n  Payment([Simulate payment outcome])\n  Receipt([Issue receipt after successful payment])\n end\n Guest --> Browse\n Guest --> Auth\n Guest --> Donate\n Donor --> Browse\n Donor --> Donate\n Donor --> History\n Donor --> Profile\n Donor --> Saved\n Admin --> Campaigns\n Admin --> Reports\n Admin --> AdminSupport\n Note[Donation validated and simulated; receipt follows success]",
      "class-diagram": '''classDiagram
 class User {
   +UUID id <<PK>>
   +String email <<unique>>
   +String passwordHash
   +Role role
   +Boolean active
 }
 class Donor {
   +UUID id <<PK>>
   +UUID userId? <<unique FK>>
   +String name
   +String email
 }
 class Campaign {
   +UUID id <<PK>>
   +String slug <<unique>>
   +Decimal target
   +CampaignStatus status
 }
 class Donation {
   +UUID id <<PK>>
   +UUID campaignId <<FK>>
   +UUID donorId? <<FK>>
   +Decimal amount
   +DonationStatus status
 }
 class PaymentAttempt {
   +UUID id
   +UUID donationId <<FK>>
   +Int attemptNumber
   +PaymentStatus status
   +String reference <<unique>>
 }
 class Receipt {
   +UUID id
   +UUID donationId <<unique FK>>
   +String receiptNumber <<unique>>
 }
 class Notification {
   +UUID id
   +UUID userId <<FK>>
   +String category
   +DateTime readAt?
 }
 class AuditLog {
   +UUID id
   +UUID userId? <<FK>>
   +String action
   +String entity
 }
 class SupportTicket {
   +UUID id
   +UUID userId <<FK>>
   +String subject
   +String status
 }
 class SupportTicketReply {
   +UUID id
   +UUID ticketId <<FK>>
   +UUID userId? <<FK>>
   +String body
 }
 User "1" -- "0..1" Donor
 Donor "1" -- "0..*" Donation
 Campaign "1" -- "0..*" Donation
 Donation "1" -- "0..*" PaymentAttempt
 Donation "1" -- "0..1" Receipt
 User "1" -- "0..*" Notification
 User "1" -- "0..*" AuditLog
 User "1" -- "0..*" SupportTicket
 SupportTicket "1" -- "0..*" SupportTicketReply''',
      "er-diagram": "erDiagram\n USER ||--o| DONOR : profile\n DONOR ||--o{ DONATION : gives\n CAMPAIGN ||--o{ DONATION : receives\n DONATION ||--o{ PAYMENT_ATTEMPT : tracks\n DONATION ||--o| RECEIPT : issues\n USER ||--o{ REFRESH_TOKEN : owns\n USER ||--o{ NOTIFICATION : receives\n USER ||--o| DONOR_PREFERENCES : sets\n USER ||--o| NOTIFICATION_PREFERENCE : sets\n USER ||--o| DONOR_DASHBOARD_PREFERENCES : sets\n USER ||--o{ AUDIT_LOG : acts\n USER ||--o{ SUPPORT_TICKET : opens\n SUPPORT_TICKET ||--o{ SUPPORT_TICKET_REPLY : contains\n USER ||--o{ LOGIN_ACTIVITY : records\n USER ||--o{ ACCOUNT_DELETION_REQUEST : requests\n USER ||--o{ EMAIL_VERIFICATION : requests\n USER ||--o{ PASSWORD_RESET : requests\n DONOR ||--o{ DONOR_ACHIEVEMENT : earns\n ACHIEVEMENT_BADGE ||--o{ DONOR_ACHIEVEMENT : defines\n CAMPAIGN ||--o{ SAVED_CAMPAIGN : saved\n USER ||--o{ SAVED_CAMPAIGN : saves\n CAMPAIGN ||--o{ CAMPAIGN_FOLLOW : followed\n USER ||--o{ CAMPAIGN_FOLLOW : follows\n CAMPAIGN ||--o{ CAMPAIGN_UPDATE : posts",
    }
    for name, content in mmd.items():
        (DIAGRAMS / f"{name}.mmd").write_text(content + "\n", encoding="utf-8")
    for name, (title, subtitle, raw_nodes, edges, cols) in diagrams.items():
        nodes = [{"id": n[0], "title": n[1], "body": n[2], "kind": "data" if n[0] in {"postgres","db","store","U","C","D","R","A"} else ("actor" if n[0] in {"guest","donor","admin","actors"} else "process")} for n in raw_nodes]
        render_diagram(name, title, subtitle, nodes, edges, cols=cols, node_w=390 if cols == 2 else 355, node_h=145)
    render_architecture_diagram()
    render_use_case_diagram()


def parse_models():
    text = SCHEMA.read_text(encoding="utf-8")
    models = []
    for match in re.finditer(r"model\s+(\w+)\s*\{(.*?)\n\}", text, re.S):
        model, body = match.groups()
        fields = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("@@"):
                continue
            m = re.match(r"(\w+)\s+(\S+)(.*)", line)
            if not m:
                continue
            name, typ, rest = m.groups()
            if typ.endswith("[]") or typ in {"User", "Donor", "Campaign", "Donation", "PaymentAttempt", "Receipt", "AuditLog", "RefreshToken", "Notification", "DonorPreferences", "SavedCampaign", "CampaignFollow", "NotificationPreference", "AchievementBadge", "DonorAchievement", "SupportTicket", "SupportTicketReply", "LoginActivity", "AccountDeletionRequest", "CampaignUpdate", "DonorDashboardPreferences", "EmailVerification", "PasswordReset"}:
                # Relation fields are included in relationship overview, not scalar storage columns.
                if typ.endswith("[]") or name in {"user", "donor", "campaign", "donations", "attempts", "receipt", "achievements", "savedBy", "followedBy", "updates", "refreshTokens", "auditLogs", "notifications", "notificationPreference", "preferences", "savedCampaigns", "followedCampaigns", "loginActivity", "deletionRequests", "dashboardPreferences", "supportTickets", "supportTicketReplies", "emailVerifications", "passwordResets", "replies", "ticket", "badge"}:
                    continue
            constraints = []
            if "@id" in rest:
                constraints.append("PK")
            if "@unique" in rest or name in {"idempotencyKey", "transactionRef", "reference", "tokenHash", "receiptNumber", "slug", "key"}:
                constraints.append("unique")
            if "@relation" in rest:
                constraints.append("FK")
            if "?" in typ:
                constraints.append("nullable")
            detail = ", ".join(constraints) if constraints else "—"
            fields.append((name, typ, detail))
        models.append((model, fields))
    return models


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_page_field(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    inst = OxmlElement("w:instrText")
    inst.set(qn("xml:space"), "preserve")
    inst.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for el in [begin, inst, separate, text, end]:
        run._r.append(el)


def set_font(run, name="Times New Roman", size=12, bold=None, color=INK):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold


def add_table(doc, headers, rows, widths=None, font_size=10):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    if widths:
        for row in table.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_shading(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(str(text))
        set_font(r, size=max(10, font_size), bold=True, color=WHITE)
    for ri, row in enumerate(rows):
        cells = table.add_row().cells
        if widths:
            for i, w in enumerate(widths):
                cells[i].width = Inches(w)
        for ci, value in enumerate(row):
            cell = cells[ci]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri % 2 == 1:
                set_cell_shading(cell, "F3F7F8")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            r = p.add_run(str(value))
            set_font(r, size=max(10, font_size), color=INK)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        set_font(p.add_run(item), size=12)


def add_numbered(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(3)
        set_font(p.add_run(item), size=12)


def add_figure(doc, slug, caption, explanation):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(RENDERED / f"{slug}.png"), width=Inches(6.4))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.keep_with_next = True
    set_font(cap.add_run(caption), size=10, bold=True, color=NAVY)
    p2 = doc.add_paragraph(explanation)
    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def build_report():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(.72)
    sec.bottom_margin = Inches(.68)
    sec.left_margin = Inches(.78)
    sec.right_margin = Inches(.78)
    sec.header_distance = Inches(.32)
    sec.footer_distance = Inches(.32)
    styles = doc.styles
    for name in ["Normal", "Body Text"]:
        styles[name].font.name = "Times New Roman"
        styles[name]._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        styles[name]._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        styles[name].font.size = Pt(12)
        styles[name].font.color.rgb = RGBColor.from_string(INK)
        styles[name].paragraph_format.space_after = Pt(6)
        styles[name].paragraph_format.line_spacing = 1.08
    for name, size, color in [("Title", 20, NAVY), ("Heading 1", 18, NAVY), ("Heading 2", 14, TEAL), ("Heading 3", 14, NAVY)]:
        style = styles[name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = name != "Title" or True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(13 if name != "Title" else 0)
        style.paragraph_format.space_after = Pt(6)
    for name in ["List Bullet", "List Number"]:
        styles[name].font.name = "Times New Roman"
        styles[name]._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        styles[name]._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        styles[name].font.size = Pt(12)
    header = sec.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_font(header.add_run("GOODWILL FOUNDATION  |  SYSTEM DOCUMENTATION"), size=8, bold=True, color=TEAL)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(footer.add_run("Goodwill Foundation • Donation Management System  |  Page "), size=8, color=MUTED)
    add_page_field(footer)

    # Cover
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(92)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run("GOODWILL FOUNDATION"), size=13, bold=True, color=TEAL)
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.add_run("Donation Management System\nProject Documentation")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(16)
    set_font(p.add_run("System analysis • design • implementation • operations"), size=13, color=MUTED)
    for _ in range(3): doc.add_paragraph()
    for label, value in [("Live website", "https://goodwillcares.vercel.app/"), ("Repository", "https://github.com/myselfstdy/goodwill-foundation"), ("Documentation basis", "Repository audit, 14 November 2026")]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_font(p.add_run(label + "  "), size=10, bold=True, color=NAVY)
        set_font(p.add_run(value), size=10, color=INK)
    doc.add_page_break()

    doc.add_heading("Report guide", level=1)
    doc.add_paragraph("This report describes the Goodwill Foundation donation application as implemented in the inspected repository. It covers system requirements, roles, architecture, PostgreSQL/Prisma data design, donor and administrator workflows, security, deployment, and known limitations. Payment attempts are simulated; no money is collected or transferred.")
    doc.add_paragraph("The chapter list below is a static contents guide. Chapter and figure numbering is fixed for this delivered edition.")
    chapters = [
      "Project overview", "Problem statement", "Existing and proposed systems", "Project scope", "Users and responsibilities", "Technology stack", "System architecture", "Database design", "Main application workflow", "Use case model", "Class model", "Donation activity", "Donation sequence", "Data flow diagrams", "Functional requirements", "Non-functional requirements", "Deployment", "Screenshots and results", "Security and data management", "Limitations and future enhancements", "Conclusion"]
    add_table(doc, ["Chapter", "Subject"], [(f"{i+1:02d}", name) for i, name in enumerate(chapters)], [1.0, 5.6], 9)
    doc.add_page_break()

    def chapter(n, title, intro=None):
        doc.add_heading(f"Chapter {n} – {title}", level=1)
        if intro: doc.add_paragraph(intro)
    chapter(1, "Project Overview", "Goodwill Foundation is a responsive web application for publishing causes, recording simulated donations, issuing receipts for successful gifts, and giving donors self-service tools. Administrators manage campaign and donor operations through a protected workspace. The application separates its React/Vite client from an Express REST API and uses Prisma with PostgreSQL for persistent mode.")
    doc.add_heading("Purpose and objectives", level=2)
    add_bullets(doc, ["Centralize campaign, donor, donation, receipt, support, and audit records.", "Offer public campaign discovery and a simulated giving workflow.", "Give donors access to their own donation history, receipts, preferences, impact, and support cases.", "Provide administrators with campaign, donor, donation, reporting, and support tools.", "Apply server-side validation, role checks, donor ownership checks, and database constraints."])
    doc.add_heading("Motivation", level=2)
    doc.add_paragraph("Manual records can be fragmented across spreadsheets and paper forms. A shared application can make campaign status and giving records easier to access while applying consistent validation and traceable updates. This project demonstrates those workflows; its payment provider is a simulator rather than a financial processor.")

    chapter(2, "Problem Statement", "Donation programs need a dependable way to publish current fundraising goals, record giving attempts, provide receipts, and answer donor questions. Manual workflows can introduce duplicate entries, slow receipt delivery, inconsistent campaign totals, and unclear ownership of donor records.")
    doc.add_heading("System need", level=2)
    add_bullets(doc, ["Use one application to manage cause details, gifts, receipts, and donor support.", "Protect donor account information with authenticated, owner-scoped routes.", "Distinguish successful and failed simulated payment attempts so failed gifts do not receive receipts.", "Give administrators searchable operational records and CSV reporting.", "Record key actions and provide in-app donor notifications."])
    doc.add_paragraph("The system does not establish financial settlement or tax-deductibility. Its receipt documents record successful demo gifts only.")

    chapter(3, "Existing and Proposed Systems", "The supplied Goodwill document describes spreadsheets, notebooks, manual receipt handling, and manually calculated campaign progress as the traditional baseline. The repository provides a centralized web workflow for these tasks.")
    add_table(doc, ["Area", "Manual approach", "Implemented application"], [
      ("Campaigns", "Separate listings and manual progress calculations", "Public list/detail and admin campaign create, update, pause"),
      ("Gift records", "Spreadsheets or paper forms", "Donation records with status, payment attempts, and campaign link"),
      ("Receipts", "Manual preparation", "Unique receipt generated for successful simulated payment only"),
      ("Donor access", "Request records from staff", "Private donor dashboard, history, receipts, preferences, and export"),
      ("Reports", "Manual filters and totals", "Admin dashboard and CSV reports"),
      ("Security", "Local file access controls", "JWT, role checks, donor ownership checks, Zod validation, Helmet and rate limits"),
    ], [1.15,2.55,2.9], 8.5)
    doc.add_heading("Advantages", level=2)
    add_bullets(doc,["One source of operational records in PostgreSQL mode.","Repeatable campaign and donation workflows.","Donor access scoped to the authenticated user.","Payment outcomes and receipts remain distinct.","A modular API and schema support incremental enhancement."])

    chapter(4, "Project Scope", "Scope is based on the client routes, Express endpoints, Prisma schema, and migrations in this repository.")
    doc.add_heading("In scope", level=2)
    add_bullets(doc,["Public campaign browsing, searching, and donation entry.","Guest and donor simulated donations, payment retries, and successful-only receipts.","JWT registration, login, refresh, logout, donor access and profile controls.","Admin dashboard, campaign and donor management, donation/receipt review, reports and activity.","Donor dashboard, giving history, impact, saved/followed campaigns, preferences and notifications.","Support tickets, account deletion requests, security sessions/activity, PDF statements, and CSV/data export."])
    doc.add_heading("Out of scope or not configured", level=2)
    add_bullets(doc,["Real card/bank processing or money transfer.","Email or SMS delivery provider for recovery and verification tokens.","Automated account anonymization/retention and production object storage for profile images.","Recurring gifts, multi-currency checkout, mobile native app, and formal tax receipt treatment."])

    chapter(5, "Users and Responsibilities", "The application uses three user categories. Authorization is enforced in the API, and donor data routes apply ownership checks.")
    add_table(doc,["Capability","Guest","Donor","Administrator"],[
      ("View/search active campaigns","Yes","Yes","Yes"),("Register and sign in","Register / sign in","Yes","Sign in"),("Create simulated gift","Yes","Yes","Not donor flow"),("View own giving / receipts","No account history","Own records","Operational review"),("Save/follow campaign","No","Own saved/followed list","Manage campaign updates"),("Manage profile/preferences","No","Own profile","Own admin identity via auth record"),("Manage campaigns/donors","No","No","Yes"),("Admin dashboard/reports/activity","No","No","Yes"),("Support tickets","No","Own tickets","Respond/review queue")
    ],[2.3,1.35,1.35,1.6],8.5)

    chapter(6, "Technology Stack")
    doc.add_paragraph("The user interface is built with React and uses Vite for development and production builds. React Router manages public, donor, administrator, and account-recovery pages. Axios connects the client to the API, while Recharts and Lucide provide charts and interface icons. The application uses authored CSS for its responsive layouts.")
    doc.add_paragraph("The server runs on Node.js with Express. Prisma connects the application to PostgreSQL and manages schema migrations. JSON Web Tokens and bcryptjs support authentication, while Zod validates incoming data. Helmet and request rate limiting add common API protections.")
    doc.add_paragraph("The repository uses authored CSS for its interface rather than Tailwind CSS.")

    chapter(7, "System Architecture", "The browser serves the React application from Vercel. The Vercel rewrite forwards /api requests to the Express service on Render. In PostgreSQL mode, route handlers use Prisma to access the Neon-hosted PostgreSQL database.")
    add_figure(doc,"system-architecture","Figure 7.1. UML deployment architecture","Deployment nodes show the browser, Vercel web tier, Render application service, and PostgreSQL database. The Express artifacts and simulated payment component are contained in the application service.")
    doc.add_paragraph("The Express application installs Helmet, CORS, JSON parsing, and rate limiting. With DATABASE_URL configured and DEMO_MODE not true, it mounts the Prisma router; otherwise the demo store routes are selected. Production PostgreSQL mode requires JWT_SECRET and JWT_REFRESH_SECRET.")

    chapter(8,"Database Design","The Prisma schema is the source of truth for persistent models. PostgreSQL uses UUID primary keys, Decimal(12,2) for campaign targets and gift amounts, enums for user/campaign/donation/payment states, unique constraints, and lookup indexes. The main and donor-portal migrations are stored under server/prisma/migrations.")
    add_figure(doc,"er-diagram","Figure 8.1. Core giving ER diagram","This overview shows the main campaign-to-gift path. A user may have a donor profile; a donor may make many donations; each donation belongs to a campaign, can have multiple payment attempts, and can have one receipt after successful payment. Supporting account, notification, support, and audit records follow the same ownership model.")

    chapter(9,"Main Application Workflow","A visitor can browse and search public campaigns without authentication. A gift may be submitted as a guest or by a signed-in donor. Donor self-service features require an authenticated donor role. Admin operations require an administrator token.")
    add_figure(doc,"application-workflow","Figure 9.1. Main application workflow","A donation result branches by the payment simulator outcome. A receipt is created only for success. The donor workspace and admin reporting are protected routes.")

    chapter(10,"Use Case Model","The use-case view separates guest, donor, and administrator actions. Donation creation includes input validation and payment simulation. Receipt issuance extends the flow only on a successful payment outcome.")
    add_figure(doc,"use-case-diagram","Figure 10.1. UML use-case diagram","The system boundary groups the implemented use cases. Guest, donor, and administrator actions are separated; donation validation and simulated payment are included in giving, while receipt issuance applies only after success.")

    chapter(11,"Class Model","The repository uses Express route modules and Prisma-generated model access rather than a custom object-oriented domain-class layer. The class diagram therefore presents real Prisma entities and their relationships; operations remain in the API workflow and route modules.")
    add_figure(doc,"class-diagram","Figure 11.1. Domain model class view","Attributes are representative scalar fields from Prisma. Methods are intentionally omitted because there are no matching persistent domain methods in the source; behavior is in Express handlers and helper functions.")

    chapter(12,"Donation Activity","The client submits campaign, amount, contact information, optional anonymity, and demo payment selection. Zod validates the payload; the service checks campaign availability and amount before creating a pending donation and payment attempt.")
    add_figure(doc,"activity-diagram","Figure 12.1. Donation activity diagram","The success path records the successful outcome and creates a receipt. The failure path records failure, omits a receipt, and can offer a retry. These outcomes are simulations.")

    chapter(13,"Donation Sequence","This sequence follows the Express route flow from browser submission through validation and the demo processor. In database mode Prisma performs related writes in a transaction where the implementation uses transactional updates.")
    add_figure(doc,"sequence-diagram","Figure 13.1. Donation processing sequence","The diagram shows the success and failure branches and the response to React. A guest can donate without a JWT; a donor request includes a bearer token and is linked only to that authenticated donor account.")

    chapter(14,"Data Flow Diagrams","The context diagram treats the application as one system exchanging data with guests, donors, administrators, and an internal payment simulator. The Level 1 view breaks that system into the actual identity, campaign, donation, payment, receipt, and reporting/support processes.")
    add_figure(doc,"dfd-level-0","Figure 14.1. DFD Level 0","External actors exchange request and result data with one Goodwill DMS process. The payment simulator is shown separately to clarify that it is not an external financial institution.")
    add_figure(doc,"dfd-level-1","Figure 14.2. DFD Level 1","Data stores represent PostgreSQL model groups. Route handlers and Prisma are the application mechanisms that read and write those stores.")

    chapter(15,"Functional Requirements")
    doc.add_paragraph("The system lets visitors browse and search campaigns, register or sign in, and submit a donation to an eligible campaign. Each simulated payment attempt is recorded; eligible failed gifts can be retried, and a unique receipt is issued only after success.")
    doc.add_paragraph("Donors can view and export their own giving history, receipts, profile, preferences, and security activity. They can save or follow campaigns, review impact, manage support tickets, download statements, and request account deletion. Administrators manage campaigns and donor records, review donations, respond to support requests, and access operational reports and audit activity.")

    chapter(16,"Non-Functional Requirements")
    doc.add_paragraph("Security and privacy are supported through password hashing, signed tokens, administrator role checks, donor ownership checks, request validation, security headers, and rate limiting. Database constraints and idempotency controls support consistent records. Production secrets and migration operations must be managed in the hosting environment.")
    doc.add_paragraph("The interface includes responsive layouts, search and filtering, and loading and error states. The API uses pagination and database indexes where implemented. Deployment should define suitable accessibility and service-level expectations.")

    chapter(17,"Deployment")
    add_table(doc,["Component","Deployment location","Verified configuration"],[("Frontend","Vercel — https://goodwillcares.vercel.app/","Static Vite build; client/vercel.json forwards /api and rewrites SPA routes."),("Backend","Render — https://goodwill-foundation.onrender.com","Express service; endpoint configured as Vercel API rewrite destination."),("Database","Neon PostgreSQL","Prisma DATABASE_URL; production code requires JWT_SECRET and JWT_REFRESH_SECRET."),("Source","GitHub — https://github.com/myselfstdy/goodwill-foundation","Repository remote configured as origin.")],[1.2,2.3,3.2],8)
    doc.add_paragraph("Environment variable names are documented in .env.example and README. Secret values must be configured in the hosting providers and are intentionally excluded from this report. Deployment files identify hosting targets; runtime health and production database state are environment-dependent.")

    chapter(18,"Screenshots and Results")
    doc.add_paragraph("The following captures were taken from the local demo application using seeded, non-production records. They illustrate the public site, authentication, administrator workspace, and donor portal. They are evidence of the visible interface only; simulated giving and local demo mode do not demonstrate production payment processing or live database behavior.")
    screenshots = [
      ("home.png", "Figure 18.1 — Public home page"),
      ("campaigns.png", "Figure 18.2 — Public campaign listing"),
      ("login.png", "Figure 18.3 — Sign-in page"),
      ("register.png", "Figure 18.4 — Donor registration page"),
      ("admin-dashboard.png", "Figure 18.5 — Administrator dashboard"),
      ("admin-campaigns.png", "Figure 18.6 — Campaign management"),
      ("donor-dashboard.png", "Figure 18.7 — Donor dashboard"),
      ("donor-history.png", "Figure 18.8 — Donor giving history"),
    ]
    shot_dir = DOCS / "screenshots"
    for i, (filename, caption) in enumerate(screenshots):
        shot = shot_dir / filename
        if not shot.exists():
            continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(shot), width=Inches(6.15))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(4)
        cap.paragraph_format.keep_with_next = (i % 2 == 0 and i < len(screenshots) - 1)
        set_font(cap.add_run(caption), size=10, bold=True, color=NAVY)
        if i % 2 == 1 and i < len(screenshots) - 1:
            doc.add_page_break()

    chapter(19,"Security and Data Management")
    add_bullets(doc,["Passwords are compared using bcryptjs hashes; plaintext passwords are not stored in the database.","JWT access tokens are short-lived and include role/user identity; tokenVersion and refresh-token revocation invalidate sessions on selected security actions.","Admin middleware checks ADMIN role. Donor endpoints use authenticated owner IDs for private records.","Zod schemas validate request bodies; Helmet applies security headers and Express auth routes use rate limiting.","Prisma schema enforces unique emails, slugs, receipt numbers, donation idempotency keys and attempt references, plus required foreign keys.","AuditLog and LoginActivity store event and sign-in metadata; RefreshToken stores hash, expiry, revocation, user-agent, and IP fields.","Profile images are stored as validated data URLs; a production deployment should move larger files to object storage.","Database and JWT secrets are supplied through environment variables. Never put their values in source control or reports."])
    doc.add_paragraph("Important: checkout is simulated. The project does not collect card numbers, contact banks, or transfer donations.")

    chapter(20,"Limitations and Future Enhancements")
    add_table(doc,["Current limitation","Possible future enhancement"],[("Payments are simulated","Integrate a compliant payment provider with verified settlement and refund flows."),("No email/SMS delivery provider is configured","Add transactional email/SMS delivery for verification, reset, and notifications."),("No recurring donation schedule","Add donor-consented recurring contributions and cancellation controls."),("No MFA in current login flow","Add multi-factor authentication and recovery codes."),("Single currency default USD","Add validated multi-currency display and settlement rules."),("Profile image data URL storage","Use object storage with type/size restrictions and lifecycle policy."),("Deletion is request-and-review; approval disables sign-in","Define retention/legal policy and automated anonymization after approved review.")],[2.5,4.1],8.2)

    chapter(21,"Conclusion")
    doc.add_paragraph("The system brings campaign discovery, simulated giving, donor services, and administrator operations into one web application. It applies access controls to donor and administrator workflows. Future work includes real payment processing, communication delivery, and validation against a production-like database.")

    out = DOCS / "Goodwill_Donation_Management_System_Final_Report.docx"
    doc.save(out)
    return out


def write_markdown_files():
    (DOCS / "PROJECT_DOCUMENTATION_AUDIT.md").write_text("""# Goodwill Foundation documentation audit

**Audit date:** 14 November 2026  
**Evidence reviewed:** repository source, Prisma schema and migrations, package manifests, Vercel configuration, automated tests, and the two supplied Word documents. The reference financial-report generator is used for organization and visual presentation only; no accounting features are carried into the Goodwill report.

## Executive summary

The donation-system document provides useful context and role descriptions, but several technical claims do not match the current repository. The source and Prisma schema are authoritative. The updated report and supporting documents correct endpoint paths, database model names, stack details, payment semantics, current features, test evidence, and deployment boundaries.

## Implemented and verified in source

- Public campaign browsing/search/detail and admin campaign create/update/pause.
- Guest and donor simulated donation workflows, payment attempts, retry behavior, success-only receipt generation, receipt PDF, verification, and annual statement PDF.
- JWT registration/login/refresh/logout, bcryptjs password hashing, role checks, donor ownership checks, Zod validation, Helmet, and auth rate limiting.
- Admin dashboard, donor/campaign management, reports and CSV export, activity/audit feed.
- Donor dashboard, giving history and CSV, impact/badges, campaign saves/follows, preferences, notification controls, profile, support tickets, data export, session/activity review, and deletion requests.
- PostgreSQL Prisma schema, initial migration and donor-portal migration; explicit JSON demo store.
- Tests: 23 API integration cases and 3 client utility unit cases passed in the recorded run on 14 November 2026.

## Partially implemented or environment-dependent

- Email verification and password reset flows create short-lived tokens, but no mail provider is configured; production delivery requires integration.
- Account deletion is a request/review flow. Approval disables the account; automated anonymization and retention are not implemented.
- Admin deletion review and donor security flows are implemented in application logic but live database behavior depends on the deployed schema and migrations.
- The deployment configuration names Vercel, Render, and Neon. This audit does not certify current uptime or live database correctness.
- The JSON demo mode and Prisma production mode are alternate runtime paths; automated API tests exercise demo mode.

## Incorrect or outdated statements corrected

| Earlier documentation claim | Current evidence / correction |
| --- | --- |
| API base `/api/v1` | Routes are mounted under `/api`; Vercel rewrites `/api/*` to Render. |
| `Payment` model | Actual Prisma model is `PaymentAttempt`. |
| `targetAmount`, `collectedAmount`, `startDate`, `endDate` | Actual Campaign fields include `target`, `startsAt`, `endsAt`; raised totals are computed from successful donation records. |
| Receipt route `/receipts/my` and `/download` | Actual routes include `/receipts`, `/receipts/:id`, `/receipts/:id/pdf`, and `/receipt-verification/:receiptNumber`. |
| Profile routes as global GET/PUT `/profile` | Current donor self-service routes are `/donor/profile` with GET/PATCH; a general signed-in profile route also exists. |
| Reports have daily/weekly/monthly/yearly filters and under-500 ms response | Exact claims were unsupported; the code has report queries/exports but no measured latency objective or benchmark. |
| Email/SMS notifications, real payment gateway, or banking integration | No providers are configured; checkout and notification delivery are simulations/in-app only. |
| Every listed test case automated | Only the cases represented in `server/tests/api.test.js` and client tests are reported as executed. |

## Gaps in the original report

- Missing substantive contents, accurate field inventory for the current 22 Prisma models, deployment flow, and diagrams from actual schema/routes.
- Legacy ERD omitted donor-portal entities and used nonexistent model names.
- API table described hypothetical routes and an incorrect version prefix.
- Non-functional section included unmeasured performance figures.
- Screenshot section was an instruction to add screenshots; repository screenshot folder had no app captures at audit time.
- The report did not distinguish current implementation from planned real payments/email/MFA enhancements consistently.

## Not verified

- No migration apply or Prisma-backed end-to-end test was run against live Neon/PostgreSQL during this audit.
- No uptime/SLA, backup restore, load benchmark, independent accessibility audit, or payment compliance assessment was performed.
- No real payment or outbound email/SMS service was exercised.
""",encoding="utf-8")

    (DOCS / "SYSTEM_DESIGN_DOCUMENTATION.md").write_text("""# System design documentation

## Context and deployment

The React/Vite client is deployed to Vercel. `client/vercel.json` forwards `/api/*` to `https://goodwill-foundation.onrender.com/api/*` and routes other paths to the SPA entry point. The Express service selects the PostgreSQL Prisma router when `DATABASE_URL` is set and `DEMO_MODE` is not `true`; otherwise it uses the JSON demo store. PostgreSQL is configured for Neon by deployment documentation. Runtime health and seed state are environment-dependent.

## Request path

1. Browser sends a request to the same-origin `/api` path.
2. Vercel forwards it to the Render Express service.
3. Express applies security headers, CORS, body-size handling, and auth rate limits.
4. Protected route middleware verifies the JWT, active user, token version, and role; owner-scoped handlers constrain data by authenticated user ID.
5. Zod validates request bodies.
6. Prisma reads/writes PostgreSQL in database mode; the demo store persists JSON only for the local showcase.
7. API returns JSON, CSV, HTML printable receipt, or generated PDF according to route.

## Donation transaction

Campaign status and amount are validated before a donation is recorded. The payment provider is a local simulator. A successful result records the payment attempt, successful donation and receipt and updates related totals within the implementation's transaction flow. A failed result remains failed and has no receipt; retry is separately represented as another attempt. An optional idempotency key protects repeated requests.

## Data model

The schema defines 23 models: User, Donor, Campaign, Donation, PaymentAttempt, Receipt, AuditLog, RefreshToken, Notification, DonorPreferences, SavedCampaign, CampaignFollow, NotificationPreference, AchievementBadge, DonorAchievement, SupportTicket, SupportTicketReply, LoginActivity, AccountDeletionRequest, CampaignUpdate, DonorDashboardPreferences, EmailVerification, and PasswordReset. 

Primary identifiers are UUIDs. Gift/campaign amounts use Decimal(12,2). Unique values include User.email, Campaign.slug, Donation.idempotencyKey and transactionRef, PaymentAttempt.reference and (donationId, attemptNumber), Receipt.donationId and receiptNumber, token hashes, and user/campaign or donor/badge pairs. The authoritative schema and complete field/relationship details are in `server/prisma/schema.prisma`.

## Design decisions and boundaries

- Guest gifts can exist without an account-linked donor; registering with the same email does not automatically claim a guest record.
- Donor endpoints scope gifts, receipts, profile, support, notifications, and security history to the authenticated account.
- Admin endpoints provide organization-wide operational access.
- Receipts are unique per donation and created only on successful simulated outcomes.
- Password reset and email verification tokens are persisted as hashes, but production delivery requires a configured mail service.
- Deletion approval disables sign-in; it does not automatically erase historical records.

## Diagram source and exports

Editable Mermaid sources are under `docs/diagrams/`; rendered SVG and PNG assets are under `docs/diagrams/rendered/`. Diagrams use consistent navy/teal styling with short labels. The ER diagram emphasizes the core giving model; the system design and database inventory document supporting relations so the visual remains readable.
""",encoding="utf-8")

    (DOCS / "API_DOCUMENTATION.md").write_text("""# API documentation

## Conventions

- Base path: `/api` (no `/api/v1` prefix).
- JSON requests/responses unless a route returns CSV, PDF, or printable HTML.
- Authenticated requests send `Authorization: Bearer <access-token>`.
- Route definitions are in `server/src/prisma-router.js`; equivalent showcase routes are in `server/src/index.js`.
- Admin means authenticated `ADMIN`; donor means authenticated `DONOR` with server-side ownership checks where the resource is private.

## Authentication and public campaigns

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/health` | Public | Health check; database mode checks connection |
| POST | `/auth/register` | Public | Create donor account |
| POST | `/auth/login` | Public | Verify credentials and issue tokens |
| POST | `/auth/refresh` | Refresh token | Rotate refresh token |
| POST | `/auth/logout` | Signed in | Revoke refresh sessions and invalidate token version |
| GET | `/auth/me` | Signed in | Current identity |
| POST | `/auth/forgot-password` | Public | Create short-lived reset token; production response is generic |
| POST | `/auth/reset-password` | Reset token | Change password and revoke sessions |
| GET | `/campaigns` | Public | Search/list campaigns with pagination and filters |
| GET | `/campaigns/:id` | Public | Read by id or slug |
| POST | `/campaigns` | Admin | Create campaign |
| PATCH | `/campaigns/:id` | Admin | Update campaign |
| DELETE | `/campaigns/:id` | Admin | Pause campaign rather than hard-delete |
| GET | `/campaigns/:id/updates` | Public/role-aware | Read campaign updates |
| POST | `/campaigns/:id/updates` | Admin | Publish update and notify followers |

## Donations, receipts, reports

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| POST | `/donations` | Guest or donor | Create gift and simulate payment |
| GET | `/donations` | Donor/admin | List authorized donation records with filters |
| GET | `/donations/:id` | Owner/admin | Read one donation |
| POST | `/donations/:id/retry` | Owner | Retry eligible failed donation |
| GET | `/donor/donations/export.csv` | Donor | Export own giving history |
| GET | `/receipts` | Donor/admin | List authorized receipt records |
| GET | `/receipts/:id` | Owner/admin | Printable receipt page |
| GET | `/receipts/:id/pdf` | Owner/admin | Receipt PDF |
| GET | `/receipt-verification/:receiptNumber` | Public | Verify a receipt number |
| GET | `/donor/annual-statement.pdf` | Donor | Own annual statement PDF |
| GET | `/dashboard` | Admin | Admin aggregate dashboard |
| GET | `/reports` | Admin | Report summary data |
| GET | `/reports/export.csv` | Admin | Donation report CSV |
| GET | `/activity` | Admin | Audit/activity feed |
| GET | `/donors` | Admin | Search/paginate donor records |
| POST | `/donors` | Admin | Create donor record |
| GET/PATCH | `/donors/:id` | Admin | Read/update donor record/account status |
| GET | `/donors/export.csv` | Admin | Donor CSV export |

## Donor profile and self-service

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET/PATCH | `/donor/profile` | Donor | Read/update own profile |
| POST | `/donor/profile/email-verification` | Donor | Start verified email change |
| POST | `/donor/profile/email-verification/confirm` | Donor + token | Confirm new email |
| GET | `/donor/dashboard` | Donor | Own giving overview |
| GET | `/donor/impact` | Donor | Impact history and badge criteria |
| GET/POST/DELETE | `/donor/saved-campaigns[/:campaignId]` | Donor | List/save/remove saved campaign |
| GET/POST/DELETE | `/donor/followed-campaigns[/:campaignId]` | Donor | List/follow/unfollow cause |
| GET | `/donor/campaign-updates` | Donor | Updates from followed campaigns |
| GET/PATCH | `/donor/preferences` | Donor | Giving preferences |
| GET/PATCH | `/donor/dashboard-preferences` | Donor | Dashboard layout preferences |
| GET/PATCH | `/donor/notifications/preferences` | Donor | Notification preferences |
| GET | `/notifications` | Signed in | List own notifications |
| PATCH | `/notifications/:id/read` | Owner | Mark one notification read |
| PATCH | `/notifications/read-all` | Signed in | Mark all own notifications read |
| GET | `/donor/security/sessions` | Donor | List own sessions |
| DELETE | `/donor/security/sessions/:id` | Donor | Revoke own refresh session |
| GET | `/donor/security/activity` | Donor | Own login/security activity |
| POST | `/donor/security/delete-request` | Donor | Submit password-confirmed deletion request |
| GET | `/donor/data-export` | Donor | Export own account data as JSON |
| GET/POST | `/donor/support/tickets` | Donor | List/create own tickets |
| POST | `/donor/support/tickets/:id/replies` | Ticket owner | Reply to own open ticket |
| GET | `/admin/support/tickets` | Admin | List support queue |
| PATCH | `/admin/support/tickets/:id` | Admin | Update status and respond |
| GET | `/admin/deletion-requests` | Admin | Review deletion requests |
| PATCH | `/admin/deletion-requests/:id` | Admin | Approve/reject; approval disables account |

## General signed-in profile routes

`GET/PATCH /profile` and `PATCH /profile/password` exist for the general authenticated profile/password flow. The donor-specific profile endpoints above add donor account details and email verification.

## Error and validation behavior

Zod rejects invalid request bodies with a client error. Missing/invalid JWTs return unauthorized responses; donor/admin role mismatches return forbidden responses; private resources outside the current donor scope are hidden or denied. Exact status codes and DTOs are defined in the matching handler. Receipt creation and payment behavior are simulated.
""",encoding="utf-8")

    (DOCS / "TESTING_DOCUMENTATION.md").write_text("""# Testing documentation

## Commands executed

| Command | Result |
| --- | --- |
| `npm run test --workspace server` (part of root run) | 23 API tests passed, 0 failed |
| `npm run test --workspace client` (part of root run) | 3 client tests passed, 0 failed |
| `npm test` | Completed successfully; 26 tests total |

**Execution date:** 14 November 2026. The tests were run in the project workspace. A first sandbox-restricted attempt could not open local loopback test servers; the successful rerun used the permitted local test-server access. No claim is made from the failed attempt.

## API coverage recorded

The Node test runner and Supertest exercise health mode, admin authentication, public campaign listing, successful/failed donations, receipt rules, idempotency, donor registration, successful-only totals, filtering and CSV, guest donation privacy, campaign save/follow, donor preferences and notification controls, PDF receipt/verification privacy, support tickets, annual statements and data export, administrator support responses, deletion request review, password recovery/session revocation, campaign administration, payment retry, authorization, report CSV, and amount validation.

## Client coverage recorded

Vitest runs `client/src/money.test.js` (3 cases). This suite checks the client money helper; it is not an end-to-end visual-browser test.

## Not run

- Prisma migration application against a live or disposable PostgreSQL database.
- Database-mode endpoint integration tests against Neon.
- Load/performance, backup/restore, accessibility, or payment-provider certification.
- Automated screenshot or cross-browser test suite.

The production build was run during the prior branding work; it is not a test suite result. See the README for current build instructions.
""",encoding="utf-8")


def update_readme():
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    marker = "## Project documentation"
    section = """## Project documentation

- [Final project report](docs/Goodwill_Donation_Management_System_Final_Report.docx)
- [Project documentation audit](docs/PROJECT_DOCUMENTATION_AUDIT.md)
- [System design documentation](docs/SYSTEM_DESIGN_DOCUMENTATION.md)
- [API documentation](docs/API_DOCUMENTATION.md)
- [Testing documentation](docs/TESTING_DOCUMENTATION.md)
- [Editable diagrams and rendered images](docs/diagrams/)

"""
    if marker in text:
        text = text[:text.index(marker)] + section + text[text.index(marker):]
    else:
        text = text.rstrip() + "\n\n" + section
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    create_diagrams()
    write_markdown_files()
    report = build_report()
    update_readme()
    print(report)
