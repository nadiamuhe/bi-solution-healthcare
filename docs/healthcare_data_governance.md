# Healthcare Data Governance & Compliance

## Overview

This project demonstrates healthcare BI best practices following HIPAA (Health Insurance Portability and Accountability Act) and FIPPA (Freedom of Information and Protection of Privacy Act - Ontario) data governance principles.

---

## Regulatory Framework

### HIPAA (United States)
- Health Insurance Portability and Accountability Act
- Governs protected health information (PHI) privacy and security
- Applies to healthcare providers, payers, and business associates

### FIPPA (Ontario, Canada)
- Freedom of Information and Protection of Privacy Act
- Governs personal information handling by public institutions
- Applies to University of Toronto and affiliated healthcare facilities

### PHIPA (Ontario, Canada)
- Personal Health Information Protection Act
- Specifically governs health information custodians
- Stricter requirements than FIPPA for clinical data

---

## De-Identification Strategy

### HIPAA Safe Harbor Method

This project uses the HIPAA Safe Harbor de-identification approach, which requires removal of 18 specific identifiers:

**Identifiers Removed:**

1. ✅ **Names** - Only synthetic IDs used (P100000, P100001, etc.)
2. ✅ **Geographic subdivisions smaller than state** - Limited to facility names only
3. ✅ **Dates** - Aggregated to month/year in most reporting; specific dates only in operational tools
4. ✅ **Telephone numbers** - Not included
5. ✅ **Fax numbers** - Not included
6. ✅ **Email addresses** - Not included
7. ✅ **Social Security numbers** - Not included
8. ✅ **Medical record numbers** - Replaced with synthetic patient_id
9. ✅ **Health plan beneficiary numbers** - Not included
10. ✅ **Account numbers** - Not included
11. ✅ **Certificate/license numbers** - Not included
12. ✅ **Vehicle identifiers** - Not applicable
13. ✅ **Device identifiers/serial numbers** - Not applicable
14. ✅ **Web URLs** - Not included
15. ✅ **IP addresses** - Not included
16. ✅ **Biometric identifiers** - Not included
17. ✅ **Full-face photos** - Not applicable
18. ✅ **Other unique identifying numbers** - None included

**Result:** Data is de-identified per HIPAA Safe Harbor methodology and cannot be traced back to real individuals.

---

## Data Minimization Principles

### Aggregation for Privacy
- Dashboard 1-3: Display only aggregated metrics (counts, averages, rates)
- Individual patient records never shown to general users
- Small cell suppression (n<5) implemented where needed

### Operational Exception
- Dashboard 4 (Research Operations): Shows patient-level data for care coordination
- Access restricted via Row-Level Security to authorized care team only
- Justification: Required for operational patient outreach and case management

---

## Row-Level Security (RLS) Implementation

### Security Roles

**1. Facility Admin Role**
- **Access:** Limited to assigned facility only
- **Implementation:** DAX filter on `dim_facilities[facility_name]`
- **Use Case:** Department managers, facility-level clinical leadership
- **Data Scope:** Can see aggregate and patient-level data for their facility only
```dax
-- Facility Admin RLS Filter
[facility_name] = USERPRINCIPALNAME()
```

**2. Executive Role**
- **Access:** Full access across all facilities
- **Implementation:** No filters applied
- **Use Case:** C-suite, system-wide quality officers
- **Data Scope:** Can see all facilities, aggregate data only (Dashboards 1-3)

**3. Care Coordinator Role** (Production Recommendation)
- **Access:** Assigned patients only
- **Implementation:** Additional filter on patient assignments
- **Use Case:** Case managers, care coordinators
- **Data Scope:** Dashboard 4 access limited to their caseload
```dax
-- Care Coordinator RLS Filter (Production)
[assigned_coordinator_id] = USERNAME()
```

### RLS Testing
- Power BI "View As" feature used to validate role restrictions
- Multiple user personas tested (facility admin, executive)
- Cross-facility data leakage verified as prevented

---

## Data Access Controls

### Production Recommendations

**Authentication:**
- Azure Active Directory integration for Single Sign-On
- Multi-factor authentication required
- Service principal accounts for automated refreshes

**Authorization:**
- Role-based access control (RBAC) via Azure AD groups
- Principle of least privilege enforced
- Regular access reviews (quarterly minimum)

**Audit Logging:**
- Power BI audit logs enabled
- Azure SQL Database audit logging configured
- Log retention: 90 days minimum (Ontario regulatory requirement)
- Monitored events:
  - Report access
  - Data exports
  - Dashboard modifications
  - Failed authentication attempts

---

## Data Retention & Disposal

### Retention Policy (Production)
- **Operational data:** 7 years (HIPAA requirement)
- **Audit logs:** 90 days minimum (FIPPA requirement)
- **Dashboard configurations:** Version controlled indefinitely
- **Synthetic demo data:** Retained for training/demo purposes

### Secure Disposal
- Azure SQL database deletion includes automated backup removal
- Power BI workspace deletion cascades to all contained reports
- No data restoration after authorized disposal

---

## Consent Management

### Research Use
- `consent_for_research` flag in `dim_patients` table
- Dashboards filter to consented patients only (where applicable)
- Opt-out mechanism documented for production implementation

### Data Sharing
- Inter-departmental data sharing governed by formal agreements
- External sharing requires Ethics Board approval
- De-identification level documented for each data release

---

## Privacy Impact Assessment (PIA)

### Risk Assessment (Production Requirement)

**Identified Risks:**
1. **Unauthorized access to patient-level data**
   - Mitigation: Row-Level Security, audit logging
2. **Re-identification through data linkage**
   - Mitigation: Safe Harbor de-identification, small cell suppression
3. **Data breach during transmission**
   - Mitigation: TLS encryption, DirectQuery (no local data caching)
4. **Insider threats**
   - Mitigation: Segregation of duties, regular access reviews

**PIA Status:** Required before production deployment at healthcare facility

---

## Compliance Monitoring

### Ongoing Activities (Production)
- Monthly access review reports
- Quarterly security assessments
- Annual HIPAA risk analysis
- Incident response plan testing

### Compliance Metrics
- % of users with appropriate RLS restrictions
- Audit log review completion rate
- Time to remediate security findings
- User training completion rate

---

## Incident Response

### Data Breach Protocol
1. **Detection:** Audit log monitoring, user reports
2. **Containment:** Immediate access revocation, system isolation if needed
3. **Investigation:** Root cause analysis, scope determination
4. **Notification:** 
   - Internal: Privacy Officer, IT Security, Legal
   - External: Affected individuals (if applicable), regulatory bodies
   - Timeline: 60 days for HIPAA, "without unreasonable delay" for FIPPA
5. **Remediation:** Patch vulnerabilities, enhance controls
6. **Documentation:** Incident log, lessons learned

---

## Training & Awareness

### Required Training (Production)
- **Initial:** HIPAA/FIPPA fundamentals, system-specific data handling
- **Annual:** Privacy refresher, policy updates
- **Role-Based:** Dashboard-specific training for each user role
- **Attestation:** Annual acknowledgment of privacy policies

---

## Third-Party Risk Management

### Cloud Provider Compliance
- **Microsoft Azure:** HIPAA Business Associate Agreement (BAA) in place
- **Power BI Service:** Covered by Microsoft compliance certifications
- **Certifications:** ISO 27001, SOC 2, HITRUST

### Data Processing Agreement
- Formal agreement with Microsoft as data processor
- Specifies data handling, security, and breach notification requirements

---

## Production Deployment Checklist

Before deploying to production healthcare environment:

- [ ] Formal Privacy Impact Assessment completed
- [ ] HIPAA Business Associate Agreements signed
- [ ] Azure AD integration configured
- [ ] Row-Level Security tested with all roles
- [ ] Audit logging enabled and monitored
- [ ] Incident response plan documented
- [ ] User training program delivered
- [ ] Data retention policy implemented
- [ ] Access review process established
- [ ] Ethics Board approval obtained (if research use)

---

## References

- HIPAA Privacy Rule: 45 CFR Part 160 and Part 164, Subparts A and E
- FIPPA (Ontario): RSO 1990, c. F.31
- PHIPA (Ontario): SO 2004, c. 3, Sched. A
- U of T Guidelines for the Protection of Privacy
- HIPAA Safe Harbor Guidance: §164.514(b)(2)

---

## Disclaimer

This project uses synthetic data for demonstration purposes only. No real patient information is included. The governance framework described represents best practices and would require formal implementation and approval before use with actual protected health information.