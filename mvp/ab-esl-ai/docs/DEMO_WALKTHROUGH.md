# AB-ESL-AI Demo Walkthrough Guide

## Pre-Demo Checklist

- [ ] Docker containers running (`make up`)
- [ ] API server started (`make api`) - <http://localhost:8000>
- [ ] Teacher Portal running (`npm run dev` in apps/teacher-portal) - <http://localhost:3000>
- [ ] Student App running (`npm run dev` in apps/student-app) - <http://localhost:3001>
- [ ] Sample student accounts ready
- [ ] Projector/screen sharing configured

---

## Demo Flow (30 minutes)

### Opening (2 minutes)

**Key Message:** "AB-ESL-AI embeds ESL specialist expertise into AI that works at scale—it's not another content app, it's a teacher amplifier."

**Show:** Teacher Portal home page with feature cards

---

### Act 1: Teacher Content Creation (8 minutes)

#### Scene 1.1: Text Leveler (3 min)

**Navigate to:** `/leveler`

**Demo Script:**

1. Paste this sample text:

   ```
   The water cycle is a continuous process that describes how water moves through Earth's atmosphere, land, and oceans. When the sun heats water in oceans, lakes, and rivers, it evaporates and rises into the atmosphere as water vapor. As the vapor rises, it cools and condenses into tiny water droplets that form clouds. When these droplets combine and become heavy enough, they fall as precipitation—rain, snow, sleet, or hail.
   ```

2. Select target levels: **A2 (Elementary)** and **B1 (Intermediate)**

3. Select L1 for glossary: **Arabic**

4. Click **Generate Leveled Versions**

**Talking Points:**

- "Watch how the AI preserves key concepts while adjusting vocabulary and sentence complexity"
- "The Arabic glossary automatically identifies challenging words and provides translations"
- "Teachers save 2+ hours per lesson on differentiation"

---

#### Scene 1.2: Decodable Generator (3 min)

**Navigate to:** `/decodable`

**Demo Script:**

1. Show the phonics scope/sequence checkboxes
2. Select: **CVC words**, **short a**, **digraph sh**
3. Click **Generate Decodable Text**

**Talking Points:**

- "Perfect for early readers and SLIFE students who need phonics-controlled text"
- "Follows Alberta's recommended scope and sequence"
- "No more hunting for decodable readers that match your current phonics unit"

---

#### Scene 1.3: Bilingual Glossary (2 min)

**Navigate to:** `/glossary`

**Demo Script:**

1. Enter: "photosynthesis, chlorophyll, carbon dioxide, oxygen"
2. Select language: **Ukrainian** (timely given current newcomer demographics)
3. Generate glossary

**Talking Points:**

- "Supports 13 languages including Ukrainian, Arabic, Tagalog, Punjabi"
- "Export to PDF for classroom word walls"
- "Parents can use the same glossary at home"

---

### Act 2: Student Experience (8 minutes)

#### Scene 2.1: Student App Overview (1 min)

**Navigate to:** Student App (<http://localhost:3001>)

**Talking Points:**

- "Students join with a class code—no accounts needed"
- "Mobile-first design, works on Chromebooks and phones"
- "Works offline for rural and remote communities"

---

#### Scene 2.2: Reading Buddy (4 min)

**Navigate to:** `/reading` in student app

**Demo Script:**

1. Select a sample passage (Grade 2-3 level)
2. Click **Start Recording**
3. Read the passage aloud (or play audio sample)
4. Show the results: WPM, accuracy, highlighted errors

**Talking Points:**

- "Instant feedback that used to require 1:1 teacher time"
- "Tracks progress over time—see growth graphs"
- "Identifies specific phonics patterns to practice"

---

#### Scene 2.3: Speaking Practice (3 min)

**Navigate to:** `/speaking` in student app

**Demo Script:**

1. Select L1: **Spanish**
2. Show minimal pairs exercise (e.g., /b/ vs /v/)
3. Record pronunciation
4. Show feedback

**Talking Points:**

- "L1-specific exercises target the sounds Spanish speakers actually struggle with"
- "Different exercises for Arabic, Chinese, Korean speakers based on their unique challenges"
- "This is L1 Transfer Intelligence in action"

---

### Act 3: Novel Alberta-Specific Features (10 minutes)

#### Scene 3.1: L1 Transfer Intelligence (3 min)

**Navigate to:** API docs (<http://localhost:8000/docs>) → `/v1/l1-transfer/`

**Demo Script:**

1. Call `GET /v1/l1-transfer/patterns/ar` (Arabic)
2. Show the phonology challenges (no /p/, no /v/)
3. Show grammar challenges (no articles, VSO word order)

**Talking Points:**

- "This is ESL specialist knowledge encoded into the system"
- "When a student makes an error, we don't just say 'wrong'—we explain WHY based on their L1"
- "Intervention plans target the specific transfer issues for each language"

---

#### Scene 3.2: Predictive Intervention Engine (3 min)

**Navigate to:** API docs → `/v1/interventions/`

**Demo Script:**

1. Show `POST /v1/interventions/assess-risk` with sample student data
2. Show the risk assessment output (risk level, warning indicators)
3. Show `POST /v1/interventions/generate-plan` for intervention plan

**Talking Points:**

- "Traditional assessment catches struggling students at report card time—too late"
- "Our predictive engine identifies at-risk students 4-6 weeks early"
- "Generates specific intervention plans aligned to Alberta benchmarks"

---

#### Scene 3.3: Curriculum Mapping (2 min)

**Navigate to:** API docs → `/v1/curriculum/`

**Demo Script:**

1. Show `POST /v1/curriculum/map-activity`
2. Show how a reading activity maps to specific Alberta ELA outcomes

**Talking Points:**

- "Every activity automatically maps to Alberta ELA outcomes and ESL Benchmarks"
- "Progress reports speak Alberta's language—no translation needed"
- "Teachers know exactly which outcomes they're addressing"

---

#### Scene 3.4: Family Literacy (2 min)

**Navigate to:** API docs → `/v1/family/`

**Demo Script:**

1. Show `POST /v1/family/homework-helper` with sample assignment
2. Show bilingual output (English + Arabic)
3. Show SMS micro-lesson format

**Talking Points:**

- "Many newcomer parents are also learning English—they can't help with homework they can't read"
- "Bilingual homework helpers include instructions in the home language"
- "SMS delivery means no app installation needed"

---

### Closing (2 minutes)

**Navigate to:** Teacher Portal home page

**Key Messages:**

1. "This isn't about replacing teachers—it's about giving every teacher ESL specialist capabilities"
2. "7 hours/week saved per teacher, 25:1 ROI"
3. "Purpose-built for Alberta: our curriculum, our benchmarks, our compliance requirements"
4. "Ready for pilot deployment"

**Questions?**

---

## Backup Demos (if time permits or questions arise)

### Analytics Dashboard

**Navigate to:** `/analytics` in Teacher Portal

- Show class overview
- Show student progress table
- Show intervention alerts

### SLIFE Content

**API:** `/v1/slife/content`

- Show age-appropriate content for older students with limited schooling
- "A 14-year-old with 2 years of schooling can't use Grade 8 materials, but 'See Spot Run' is insulting"

### Cultural Responsiveness

**API:** `/v1/cultural/profile/{culture_code}`

- Show cultural profiles with learning preferences
- "We don't just translate—we adapt for cultural context"

### FOIP Compliance

**API:** `/v1/privacy/compliance-report`

- Show privacy-by-design features
- "Canadian data residency, k-anonymity, audit trails"

---

## Common Questions & Answers

**Q: How does it handle students with no English?**
A: The system starts with visual supports, L1 instructions, and oral language priority. The SLIFE pathway is designed for absolute beginners.

**Q: What about rural schools with poor internet?**
A: Offline-first architecture. Content pre-caches, works without connectivity, syncs when connected.

**Q: How accurate is the ASR for non-native speakers?**
A: We use models trained on diverse accents. Accuracy improves as students use the system (adaptive).

**Q: Can teachers customize content?**
A: Yes—all generated content is editable. Teachers remain in control.

**Q: What training do teachers need?**
A: 30 minutes self-paced online training. Most features are intuitive.

**Q: How is student data protected?**
A: FOIP-compliant architecture, Canadian data residency, no data sharing with third parties, full audit trails.

---

## Technical Requirements

- **Browser:** Chrome 90+, Edge 90+, Firefox 88+, Safari 14+
- **Devices:** Chromebooks, laptops, tablets, phones
- **Internet:** Works offline after initial sync
- **Audio:** Microphone required for speaking/reading practice

---

## Troubleshooting

### API won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Check Docker containers are running
docker compose ps

# View API logs
make api  # Shows live logs
```

### Frontend shows "Failed to fetch"

- Ensure API is running at `http://localhost:8000`
- Check CORS settings in `.env` (should include localhost:3000)
- Verify `NEXT_PUBLIC_API_URL` is set correctly

### Live Captions not working

- Check microphone permissions in browser
- Ensure WebSocket connection (green indicator)
- Verify API has `ENABLE_ASR=true` in `.env`

### Database connection fails

```bash
# Restart Postgres
docker compose restart db

# Check connection
docker compose exec db psql -U dev -d ab_esl_ai
```

### Quick Reset for Fresh Demo

```bash
make down          # Stop and remove containers
make up            # Start fresh containers
make seed          # Reseed demo data
```
