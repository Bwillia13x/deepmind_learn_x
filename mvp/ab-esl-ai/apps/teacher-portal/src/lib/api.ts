const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export async function createSession(teacherName: string, gradeLevel: string = 'K-6') {
  const res = await fetch(`${API_BASE}/api/auth/create-session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ teacher_name: teacherName, grade_level: gradeLevel }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function simplifyText(text: string, strength: number) {
  const res = await fetch(`${API_BASE}/api/v1/captions/simplify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, strength, focus_commands: true }),
  });
  if (!res.ok) throw new Error('Failed to simplify');
  return res.json();
}

export async function getGloss(text: string, l1: string, topK: number = 8) {
  const res = await fetch(`${API_BASE}/api/v1/captions/gloss`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, l1, top_k: topK }),
  });
  if (!res.ok) throw new Error('Failed to get gloss');
  return res.json();
}

export async function levelText(text: string, targets: string[], l1?: string) {
  const res = await fetch(`${API_BASE}/api/v1/authoring/level-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, targets, l1 }),
  });
  if (!res.ok) throw new Error('Failed to level text');
  return res.json();
}

export async function generateDecodable(graphemes: string[], lengthSentences: number) {
  const res = await fetch(`${API_BASE}/api/v1/reading/generate_decodable`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ graphemes, length_sentences: lengthSentences }),
  });
  if (!res.ok) throw new Error('Failed to generate decodable');
  return res.json();
}
