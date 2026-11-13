const clean = value => String(value ?? '').normalize('NFKD').replace(/[^\x20-\x7E]/g, '?').replaceAll('\\', '\\\\').replaceAll('(', '\\(').replaceAll(')', '\\)');

export function createPdf(lines, { title = 'Goodwill Foundation' } = {}) {
  const safeLines = [title, '', ...lines].slice(0, 48);
  const stream = ['BT', '/F1 11 Tf', '50 790 Td'];
  safeLines.forEach((line, index) => {
    if (index) stream.push('0 -16 Td');
    stream.push(`(${clean(line)}) Tj`);
  });
  stream.push('ET');
  const content = stream.join('\n');
  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    `<< /Length ${Buffer.byteLength(content)} >>\nstream\n${content}\nendstream`,
  ];
  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  objects.forEach((object, index) => {
    offsets.push(Buffer.byteLength(pdf));
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });
  const xrefOffset = Buffer.byteLength(pdf);
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  offsets.slice(1).forEach(offset => { pdf += `${String(offset).padStart(10, '0')} 00000 n \n`; });
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
  return Buffer.from(pdf, 'binary');
}
