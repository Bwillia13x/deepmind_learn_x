# Privacy and FOIP Compliance

## Data Handling Principles

### Minimal PII Collection

- Only collect: user ID, grade band, L1 (first language)
- No biometric templates stored
- No personally identifiable information beyond class codes

### Audio/Video Processing

- **Default**: On-device processing (no audio leaves device)
- **If uploaded** (with explicit consent):
  - Anonymize before storage
  - Short retention: 24-72 hours maximum
  - Automatic deletion after processing

### Data Residency

- All cloud workloads hosted in Canada (AWS ca-central-1, GCP Montreal)
- No data transferred outside Canadian jurisdiction
- Local edge boxes for maximum privacy

## FOIP/PIPA Compliance

### Consent

- Explicit opt-in for any data collection beyond local processing
- Clear explanation of data use in plain language
- Parental consent required for students under 18

### Admin Controls

- Disable translation for assessments
- Lock prompts to prevent misuse
- Export all student data on request
- Delete all student data on request
- Audit trails for all data access

## Technical Safeguards

### Encryption

- TLS 1.3 for all network traffic
- AES-256 encryption at rest
- Secure key management

### Access Control

- Role-based access (student, teacher, admin)
- Session tokens with short expiry
- IP allowlisting for admin functions

### Audit Logging

- All API access logged
- No raw audio in logs
- No full transcripts in logs
- Metrics only: latency, counts, error rates

## Feature Flags

Default privacy-preserving settings:

```
SAVE_AUDIO_BY_DEFAULT=false
SAVE_TRANSCRIPTS_BY_DEFAULT=false
L1_ENABLED_BY_DEFAULT=true
```

## Retention Schedule

| Data Type | Retention | Notes |
|-----------|-----------|-------|
| Session tokens | 24 hours | Auto-expire |
| Uploaded audio | 72 hours | Auto-delete after scoring |
| Transcripts | User choice | Only if save=true |
| Reading scores | 1 school year | Exportable |
| Analytics | Aggregated only | No PII |
