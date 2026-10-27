-- ============================================================================
-- Ekasutra · SIH26264 · demo seed (generated, do not edit by hand)
--
-- Source : demo_seed.json  ·  generator: generate_demo_seed.py
-- Target : PostgreSQL 14+ with schema.sql already loaded
-- Rows   : 18 institutions, 27 aliases, 9 users, 32 cases,
--          129 case events, 109 documents, 3 overlap clusters,
--          7 overlap-case links, 3 rooms, 5 room activities,
--          18 audit entries
--
-- Chain  : genesis = 64 zeros · head =
--          748b44fc1aad8e9a1c05d0040b54e95f68d966ea5396dffc789139aab9fc6fe0
--
-- Load into an EMPTY database only. The guard below refuses to touch a
-- database that already has institutions, cases or audit rows, so this
-- file can never overwrite the 9,558-row national master.
--
--   createdb ekasutra_demo
--   psql -d ekasutra_demo -f schema.sql
--   psql -d ekasutra_demo -f seed_demo.sql
-- ============================================================================

\set ON_ERROR_STOP on

begin;

do $$
begin
  if (select count(*) from institutions) <> 0
     or (select count(*) from users) <> 0
     or (select count(*) from cases) <> 0
     or (select count(*) from audit_entries) <> 0 then
    raise exception 'seed_demo.sql: target database is not empty. Create a fresh database, e.g. createdb ekasutra_demo';
  end if;
end $$;

-- ------------------------------------------------------------------- users
insert into users (email, full_name, role, bureau) values
  ('r.menon@aicte.gov.in', 'R. Menon', 'lead', 'RB'),
  ('p.rao@aicte.gov.in', 'P. Rao', 'officer', 'PGRC'),
  ('k.nair@aicte.gov.in', 'K. Nair', 'officer', 'RB'),
  ('a.das@aicte.gov.in', 'A. Das', 'officer', 'PGRC'),
  ('a.kumar@aicte.gov.in', 'A. Kumar', 'officer', 'PGRC'),
  ('s.iyer@aicte.gov.in', 'S. Iyer', 'officer', 'RO'),
  ('m.das@aicte.gov.in', 'M. Das', 'officer', 'RO'),
  ('director@aicte.gov.in', 'Director, AICTE', 'director', null),
  ('admin@aicte.gov.in', 'System Administrator', 'admin', null);

-- ------------------------------------------------------------ institutions
insert into institutions (permanent_id, name, address, city, state, region, trust_name) values
  ('1-1234567', 'Vidyasagara College of Engineering', 'Pennalur, Sriperumbudur, Kanchipuram 602117', 'Kanchipuram', 'Tamil Nadu', 'South', 'Vidyasagara Educational Trust'),
  ('1-2345678', 'Vidyasagara Institute of Technology', 'Karakatamanchi, Tirupati 517502', 'Tirupati', 'Andhra Pradesh', 'South', 'Vidya Prasarana Society'),
  ('1-3456789', 'Annai Thilagam College of Engineering', 'Vembuliamman Koil St, K.K. Nagar, Chennai 600078', 'Chennai', 'Tamil Nadu', 'South', 'Annai Thilagam Educational Trust'),
  ('1-4567890', 'Annai Thilagam Polytechnic College', 'GST Road, Chengalpattu 603001', 'Chengalpattu', 'Tamil Nadu', 'South', 'Annai Thilagam Educational Trust'),
  ('1-5678901', 'Triloknath Government Polytechnic', 'Kangra 176001', 'Kangra', 'Himachal Pradesh', 'North', '—'),
  ('1-6789012', 'Kandhasor Government Polytechnic', 'Nabarangpur 764059', 'Nabarangpur', 'Odisha', 'East', '—'),
  ('1-7890123', 'Rajhans College of Science & Technology', 'Bypass Road, Indore 452020', 'Indore', 'Madhya Pradesh', 'Central', 'Rajhans Education Society'),
  ('1-8901234', 'Rajhans Institute of Management', 'Hoshangabad Road, Bhopal 462047', 'Bhopal', 'Madhya Pradesh', 'Central', 'Rajhans Education Society'),
  ('1-9012345', 'St. Ives Technical Institute', 'Mahim, Mumbai 400016', 'Mumbai', 'Maharashtra', 'West', 'St. Ives Society'),
  ('1-0123456', 'Chalukya Institute of Technology', 'Cholanayakanahalli, Bengaluru 560032', 'Bengaluru', 'Karnataka', 'South', '—'),
  ('1-1122334', 'Kovai College of Engineering', 'Vattamalaipalayam, Coimbatore 641042', 'Coimbatore', 'Tamil Nadu', 'South', 'Kovai Educational Trust'),
  ('1-2233445', 'Kovai Institute of Technology', 'Vinayaka Nagar, Coimbatore 641035', 'Coimbatore', 'Tamil Nadu', 'South', 'Nallur Educational Trust'),
  ('1-3344556', 'Sahyadri Vidyapeeth''s Technical Institute', 'Nandanvan College Road, Pune 411004', 'Pune', 'Maharashtra', 'West', 'Sahyadri Vidyapeeth Society'),
  ('1-4455667', 'Anandashram College (Autonomous)', 'N.C. Road, Pune 411004', 'Pune', 'Maharashtra', 'West', 'Sahyadri Vidyapeeth Society'),
  ('1-5566778', 'Vidyanidhi Institute of Technology', 'Gandipet, Hyderabad 500075', 'Hyderabad', 'Telangana', 'South', 'Vidyanidhi Educational Society'),
  ('1-6677889', 'Kodiyur Government Engineering College', 'Ramavarmapuram, Thrissur 680009', 'Thrissur', 'Kerala', 'South', '—'),
  ('1-7788990', 'Sardar Rajhans Institute of Technology', 'Andheri West, Mumbai 400058', 'Mumbai', 'Maharashtra', 'West', 'Rajhans Memorial Trust'),
  ('1-8899001', 'Kancheepuram Institute of Design & Manufacturing', 'Melakottaiyur, Kancheepuram 600127', 'Kancheepuram', 'Tamil Nadu', 'South', '—');

insert into institution_aliases (institution_id, alias, source)
select i.id, v.alias, v.source
from (values
  ('1-1234567', 'V.S. College of Engineering', 'master'),
  ('1-1234567', 'Vidyasagar Engineering College', 'complaint'),
  ('1-1234567', 'VCE Kanchipuram', 'manual'),
  ('1-2345678', 'VSIT Tirupati', 'master'),
  ('1-2345678', 'Vidyasagar Institute of Technology', 'complaint'),
  ('1-3456789', 'ATCE Chennai', 'master'),
  ('1-3456789', 'Annai Thilagam Engg College', 'complaint'),
  ('1-4567890', 'ATPC Chengalpattu', 'master'),
  ('1-5678901', 'T.G.P. Kangra', 'master'),
  ('1-5678901', 'Triloknath Govt Polytechnic', 'complaint'),
  ('1-6789012', 'K.G.P. Nabarangpur', 'master'),
  ('1-7890123', 'Rajhans College of Sci & Tech', 'master'),
  ('1-7890123', 'RCST Indore', 'complaint'),
  ('1-8901234', 'RIM Bhopal', 'master'),
  ('1-9012345', 'SITI Mumbai', 'master'),
  ('1-9012345', 'St Ives Technical Institute', 'complaint'),
  ('1-0123456', 'CIT Bengaluru', 'master'),
  ('1-1122334', 'KCE Coimbatore', 'master'),
  ('1-1122334', 'Kovai College of Engg', 'complaint'),
  ('1-2233445', 'KIT Coimbatore', 'master'),
  ('1-3344556', 'SV Technical Institute', 'master'),
  ('1-3344556', 'SVTI Pune', 'complaint'),
  ('1-4455667', 'Anandashram College Pune', 'master'),
  ('1-5566778', 'VNIET Hyderabad', 'master'),
  ('1-6677889', 'KGEC Thrissur', 'master'),
  ('1-7788990', 'SRIT Mumbai', 'master'),
  ('1-8899001', 'KIDM Kancheepuram', 'master')) as v(pid, alias, source)
join institutions i on i.permanent_id = v.pid;

-- ------------------------------------------------------------------- cases
insert into cases (case_no, institution_id, bureau, category, status, transfer_to,
                   received_on, sla_days, officer_id, last_action, last_action_on,
                   next_action, expected_disposal, summary)
select v.case_no, i.id, v.bureau, v.category, v.status, v.transfer_to,
       v.received_on::date, v.sla_days::int, u.id, v.last_action,
       v.last_action_on::date, v.next_action, v.expected::date, v.summary
from (values
  ('C-2026-0031', '1-3456789', 'RB', 'Unauthorized intake', 'Disposed', null, '2026-02-04'::date, '60'::int, 'S. Iyer', 'Show-cause closed, admissions re-verified', '2026-02-26'::date, 'None — disposed', '2026-03-20'::date, 'Institution admitted 38 students beyond sanctioned intake in two PG programmes.'),
  ('C-2026-0042', '1-4567890', 'PGRC', 'Fee refund / scholarship', 'Disposed', null, '2026-02-18'::date, '60'::int, 'P. Rao', 'Refund schedule filed with PGRC', '2026-03-12'::date, 'None — disposed', '2026-04-02'::date, 'Students allege excess lab and development fee collected for 2025-26.'),
  ('C-2026-0057', '1-5678901', 'PGRC', 'Scholarship delay', 'Disposed', null, '2026-03-03'::date, '60'::int, 'A. Kumar', 'State scholarship portal reconciled', '2026-03-28'::date, 'None — disposed', '2026-04-17'::date, 'Post-matric scholarship amounts not credited to 61 eligible students.'),
  ('C-2026-0068', '1-6789012', 'RB', 'Approval violation', 'Disposed', null, '2026-03-21'::date, '90'::int, 'R. Menon', 'Programme closure undertaking accepted', '2026-04-30'::date, 'None — disposed', '2026-05-20'::date, 'Unapproved engineering programme advertised without AICTE approval for 2026-27.'),
  ('C-2026-0079', '1-7890123', 'RB', 'Faculty shortage', 'Disposed', null, '2026-04-07'::date, '60'::int, 'K. Nair', 'Faculty list verified against payroll', '2026-05-02'::date, 'None — disposed', '2026-05-27'::date, 'Core faculty shortfall of 22% against the approved intake for the academic year.'),
  ('C-2026-0091', '1-8901234', 'RO', 'Infrastructure deficiency', 'Disposed', null, '2026-04-22'::date, '60'::int, 'M. Das', 'Joint inspection report closed', '2026-05-19'::date, 'None — disposed', '2026-06-11'::date, 'Laboratory equipment and built-up area below the approved norms.'),
  ('C-2026-0104', '1-9012345', 'RO', 'Land / building violation', 'Disposed', null, '2026-05-11'::date, '60'::int, 'S. Iyer', 'Land documents and lease deed verified', '2026-06-08'::date, 'None — disposed', '2026-07-01'::date, 'Campus operated from a site not reflected in the approved land documents.'),
  ('C-2026-0118', '1-0123456', 'PGRC', 'Harassment complaint', 'Disposed', null, '2026-06-02'::date, '45'::int, 'P. Rao', 'Internal committee report and action taken', '2026-07-01'::date, 'None — disposed', '2026-07-22'::date, 'Complaint referred to the institution internal committee; report received.'),
  ('C-2026-0129', '1-1122334', 'PGRC', 'Fee refund / scholarship', 'Disposed', null, '2026-06-19'::date, '60'::int, 'A. Kumar', 'Refund proof submitted by institution', '2026-07-14'::date, 'None — disposed', '2026-08-05'::date, 'Caution deposit not refunded after withdrawal from the first year.'),
  ('C-2026-0131', '1-2233445', 'RB', 'Unauthorized intake', 'Disposed', null, '2026-07-02'::date, '60'::int, 'R. Menon', 'Penalty order issued, intake capped', '2026-07-29'::date, 'None — disposed', '2026-08-21'::date, 'Management quota seats offered without the approved admission matrix.'),
  ('C-2026-0142', '1-1234567', 'PGRC', 'Fee refund / scholarship', 'Under Process', null, '2026-09-12'::date, '60'::int, 'P. Rao', 'College response sought', '2026-10-18'::date, 'Verify fee receipts', '2026-11-01'::date, 'Batch of 14 students alleges excess lab fee and unpaid scholarship refunds.'),
  ('C-2026-0167', '1-1234567', 'RB', 'Unauthorized intake', 'Under Process', null, '2026-10-02'::date, '90'::int, 'R. Menon', 'Records requested', '2026-10-20'::date, 'Schedule inspection', '2026-11-15'::date, 'Institution reportedly admitted students beyond sanctioned intake in two programs.'),
  ('C-2026-0198', '1-1234567', 'PGRC', 'Scholarship delay', 'Pending', null, '2026-10-21'::date, '60'::int, null, 'Case created', '2026-10-21'::date, 'Assign officer', '2026-12-20'::date, 'Late disbursal of state scholarship for 2025-26 batch.'),
  ('C-2026-0180', '1-2345678', 'PGRC', 'Faculty shortage', 'Escalated', null, '2026-08-28'::date, '60'::int, 'S. Iyer', 'Escalated to Director', '2026-10-16'::date, 'Personal hearing', '2026-10-30'::date, 'Only 41% faculty positions filled against sanctioned strength.'),
  ('C-2026-0181', '1-2345678', 'RB', 'Approval violation', 'Under Process', null, '2026-09-05'::date, '90'::int, 'K. Nair', 'Show-cause issued', '2026-10-19'::date, 'Inspect records', '2026-11-10'::date, 'New program started without AICTE approval for 2026-27.'),
  ('C-2026-0155', '1-3456789', 'PGRC', 'Harassment complaint', 'Under Process', null, '2026-09-20'::date, '45'::int, 'A. Das', 'Inquiry committee formed', '2026-10-17'::date, 'Inquiry report', '2026-11-05'::date, 'Complaint by three faculty members against departmental head.'),
  ('C-2026-0160', '1-4567890', 'RB', 'Land / building violation', 'Under Process', null, '2026-09-25'::date, '30'::int, 'R. Menon', 'Site plan obtained', '2026-10-15'::date, 'Site inspection', '2026-12-01'::date, 'Unauthorized construction on land shown as playground in approved plan.'),
  ('C-2026-0171', '1-7890123', 'RB', 'Unapproved course', 'Pending', null, '2026-10-10'::date, '90'::int, null, 'Case created', '2026-10-10'::date, 'Assign officer', '2026-12-01'::date, 'New AI & Data Science course advertised without approval.'),
  ('C-2026-0172', '1-8901234', 'PGRC', 'Fee grievance', 'Disposed', null, '2026-08-15'::date, '60'::int, 'P. Rao', 'Refund confirmed', '2026-09-30'::date, '—', '2026-09-30'::date, 'Excess fee refunded to 9 students.'),
  ('C-2026-0185', '1-5678901', 'PGRC', 'Scholarship delay', 'Pending', null, '2026-08-01'::date, '60'::int, 'S. Iyer', 'Notice to state office', '2026-09-02'::date, 'Follow up with state', '2026-09-30'::date, 'Post-matric scholarship not released for 38 students.'),
  ('C-2026-0186', '1-6789012', 'RB', 'Infrastructure deficiency', 'Transferred', 'PGRC', '2026-09-01'::date, '45'::int, 'K. Nair', 'Transferred by PGRC', '2026-10-10'::date, 'Accept custody', '2026-10-15'::date, 'Lab and library deficiency; PGRC transferred to RB on 10 Oct. Custody not accepted.'),
  ('C-2026-0190', '1-9012345', 'RB', 'Unapproved intake', 'Under Process', null, '2026-09-28'::date, '90'::int, 'R. Menon', 'Show-cause notice', '2026-10-19'::date, 'Reply review', '2026-11-20'::date, 'Diploma intake exceeds approved seats by 60.'),
  ('C-2026-0191', '1-0123456', 'PGRC', 'Fee refund', 'Disposed', null, '2026-08-20'::date, '60'::int, 'A. Das', 'Refund processed', '2026-10-01'::date, '—', '2026-10-01'::date, 'Refund of admission fee after withdrawal.'),
  ('C-2026-0192', '1-1122334', 'PGRC', 'Faculty behaviour', 'Pending', null, '2026-10-18'::date, '45'::int, null, 'Case created', '2026-10-18'::date, 'Assign officer', '2026-12-15'::date, 'Allegation of discriminatory behaviour in classroom.'),
  ('C-2026-0193', '1-2233445', 'RB', 'Approval violation', 'Under Process', null, '2026-10-05'::date, '90'::int, 'K. Nair', 'Documents under verification', '2026-10-20'::date, 'Document verification', '2026-11-25'::date, 'Lab equipment shown for approval not found on site.'),
  ('C-2026-0194', '1-3344556', 'PGRC', 'Fee grievance', 'Under Process', null, '2026-09-30'::date, '60'::int, 'P. Rao', 'College response sought', '2026-10-18'::date, 'Seek response', '2026-11-10'::date, 'Fee charged for activity not listed in fee structure.'),
  ('C-2026-0195', '1-4455667', 'RB', 'Compliance', 'Pending', null, '2026-10-12'::date, '90'::int, null, 'Case created', '2026-10-12'::date, 'Assign officer', '2026-12-10'::date, 'Autonomy compliance documents pending verification.'),
  ('C-2026-0196', '1-5566778', 'PGRC', 'Admission irregularity', 'Under Process', null, '2026-10-01'::date, '60'::int, 'S. Iyer', 'Statements obtained', '2026-10-19'::date, 'Inquiry', '2026-11-15'::date, 'Admissions made outside the approved counseling process.'),
  ('C-2026-0197', '1-5566778', 'RB', 'Unapproved course', 'Under Process', null, '2026-10-08'::date, '90'::int, 'R. Menon', 'Inspection scheduled', '2026-10-20'::date, 'Inspection', '2026-11-30'::date, 'Evening MBA program launched without approval.'),
  ('C-2026-0165', '1-8899001', 'PGRC', 'Faculty shortage', 'Disposed', null, '2026-07-10'::date, '60'::int, 'A. Das', 'Compliance confirmed', '2026-09-15'::date, '—', '2026-09-15'::date, 'Faculty shortage rectified; case closed.'),
  ('C-2026-0168', '1-6677889', 'PGRC', 'Fee grievance', 'Under Process', null, '2026-09-18'::date, '60'::int, 'P. Rao', 'College response sought', '2026-10-16'::date, 'Seek response', '2026-11-01'::date, 'Excess fee charged for lab consumables.'),
  ('C-2026-0169', '1-7788990', 'RB', 'Unapproved course', 'Pending', null, '2026-10-14'::date, '90'::int, null, 'Case created', '2026-10-14'::date, 'Assign officer', '2026-12-15'::date, 'New PG diploma advertised before approval.'))
as v(case_no, pid, bureau, category, status, transfer_to, received_on, sla_days,
     officer, last_action, last_action_on, next_action, expected, summary)
join institutions i on i.permanent_id = v.pid
left join users u on u.full_name = v.officer;

-- -------------------------------------------------------------- case events
insert into case_events (case_id, at, actor, kind, detail)
select c.id, v.at::timestamptz, v.actor, v.kind, v.detail
from (values
  ('C-2026-0031', '2026-02-04 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0031', '2026-02-04 10:30:00+00'::timestamptz, 'S. Iyer', 'document', '3 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0031', '2026-02-04 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to S. Iyer · RB'),
  ('C-2026-0031', '2026-02-26 15:30:00+00'::timestamptz, 'S. Iyer', 'disposal', 'Show-cause closed, admissions re-verified'),
  ('C-2026-0042', '2026-02-18 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0042', '2026-02-18 10:30:00+00'::timestamptz, 'P. Rao', 'document', '4 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0042', '2026-02-18 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to P. Rao · PGRC'),
  ('C-2026-0042', '2026-03-12 15:30:00+00'::timestamptz, 'P. Rao', 'disposal', 'Refund schedule filed with PGRC'),
  ('C-2026-0057', '2026-03-03 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0057', '2026-03-03 10:30:00+00'::timestamptz, 'A. Kumar', 'document', '2 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0057', '2026-03-03 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to A. Kumar · PGRC'),
  ('C-2026-0057', '2026-03-28 15:30:00+00'::timestamptz, 'A. Kumar', 'disposal', 'State scholarship portal reconciled'),
  ('C-2026-0068', '2026-03-21 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0068', '2026-03-21 10:30:00+00'::timestamptz, 'R. Menon', 'document', '5 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0068', '2026-03-21 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to R. Menon · RB'),
  ('C-2026-0068', '2026-04-30 15:30:00+00'::timestamptz, 'R. Menon', 'disposal', 'Programme closure undertaking accepted'),
  ('C-2026-0079', '2026-04-07 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0079', '2026-04-07 10:30:00+00'::timestamptz, 'K. Nair', 'document', '2 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0079', '2026-04-07 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to K. Nair · RB'),
  ('C-2026-0079', '2026-05-02 15:30:00+00'::timestamptz, 'K. Nair', 'disposal', 'Faculty list verified against payroll'),
  ('C-2026-0091', '2026-04-22 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0091', '2026-04-22 10:30:00+00'::timestamptz, 'M. Das', 'document', '6 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0091', '2026-04-22 11:15:00+00'::timestamptz, 'M. Das', 'assigned', 'Assigned to M. Das · RO'),
  ('C-2026-0091', '2026-05-19 15:30:00+00'::timestamptz, 'M. Das', 'disposal', 'Joint inspection report closed'),
  ('C-2026-0104', '2026-05-11 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0104', '2026-05-11 10:30:00+00'::timestamptz, 'S. Iyer', 'document', '4 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0104', '2026-05-11 11:15:00+00'::timestamptz, 'M. Das', 'assigned', 'Assigned to S. Iyer · RO'),
  ('C-2026-0104', '2026-06-08 15:30:00+00'::timestamptz, 'S. Iyer', 'disposal', 'Land documents and lease deed verified'),
  ('C-2026-0118', '2026-06-02 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0118', '2026-06-02 10:30:00+00'::timestamptz, 'P. Rao', 'document', '7 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0118', '2026-06-02 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to P. Rao · PGRC'),
  ('C-2026-0118', '2026-07-01 15:30:00+00'::timestamptz, 'P. Rao', 'disposal', 'Internal committee report and action taken'),
  ('C-2026-0129', '2026-06-19 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0129', '2026-06-19 10:30:00+00'::timestamptz, 'A. Kumar', 'document', '3 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0129', '2026-06-19 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to A. Kumar · PGRC'),
  ('C-2026-0129', '2026-07-14 15:30:00+00'::timestamptz, 'A. Kumar', 'disposal', 'Refund proof submitted by institution'),
  ('C-2026-0131', '2026-07-02 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0131', '2026-07-02 10:30:00+00'::timestamptz, 'R. Menon', 'document', '4 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0131', '2026-07-02 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to R. Menon · RB'),
  ('C-2026-0131', '2026-07-29 15:30:00+00'::timestamptz, 'R. Menon', 'disposal', 'Penalty order issued, intake capped'),
  ('C-2026-0142', '2026-09-12 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0142', '2026-09-12 10:30:00+00'::timestamptz, 'P. Rao', 'document', '3 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0142', '2026-09-12 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to P. Rao · PGRC'),
  ('C-2026-0142', '2026-10-18 15:30:00+00'::timestamptz, 'P. Rao', 'note', 'College response sought'),
  ('C-2026-0167', '2026-10-02 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0167', '2026-10-02 10:30:00+00'::timestamptz, 'R. Menon', 'document', '5 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0167', '2026-10-02 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to R. Menon · RB'),
  ('C-2026-0167', '2026-10-20 15:30:00+00'::timestamptz, 'R. Menon', 'note', 'Records requested'),
  ('C-2026-0198', '2026-10-21 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0198', '2026-10-21 10:30:00+00'::timestamptz, 'P. Rao', 'document', '1 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0198', '2026-10-21 11:15:00+00'::timestamptz, 'P. Rao', 'note', 'Unassigned — queued for PGRC lead'),
  ('C-2026-0198', '2026-10-21 15:30:00+00'::timestamptz, 'P. Rao', 'note', 'Case created'),
  ('C-2026-0180', '2026-08-28 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0180', '2026-08-28 10:30:00+00'::timestamptz, 'S. Iyer', 'document', '4 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0180', '2026-08-28 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to S. Iyer · PGRC'),
  ('C-2026-0180', '2026-10-16 15:30:00+00'::timestamptz, 'S. Iyer', 'escalation', 'Escalated to Director'),
  ('C-2026-0181', '2026-09-05 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0181', '2026-09-05 10:30:00+00'::timestamptz, 'K. Nair', 'document', '6 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0181', '2026-09-05 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to K. Nair · RB'),
  ('C-2026-0181', '2026-10-19 15:30:00+00'::timestamptz, 'K. Nair', 'note', 'Show-cause issued'),
  ('C-2026-0155', '2026-09-20 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0155', '2026-09-20 10:30:00+00'::timestamptz, 'A. Das', 'document', '7 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0155', '2026-09-20 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to A. Das · PGRC'),
  ('C-2026-0155', '2026-10-17 15:30:00+00'::timestamptz, 'A. Das', 'note', 'Inquiry committee formed'),
  ('C-2026-0160', '2026-09-25 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0160', '2026-09-25 10:30:00+00'::timestamptz, 'R. Menon', 'document', '4 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0160', '2026-09-25 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to R. Menon · RB'),
  ('C-2026-0160', '2026-10-15 15:30:00+00'::timestamptz, 'R. Menon', 'note', 'Site plan obtained'),
  ('C-2026-0171', '2026-10-10 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0171', '2026-10-10 10:30:00+00'::timestamptz, 'R. Menon', 'document', '2 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0171', '2026-10-10 11:15:00+00'::timestamptz, 'R. Menon', 'note', 'Unassigned — queued for RB lead'),
  ('C-2026-0171', '2026-10-10 15:30:00+00'::timestamptz, 'R. Menon', 'note', 'Case created'),
  ('C-2026-0172', '2026-08-15 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0172', '2026-08-15 10:30:00+00'::timestamptz, 'P. Rao', 'document', '3 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0172', '2026-08-15 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to P. Rao · PGRC'),
  ('C-2026-0172', '2026-09-30 15:30:00+00'::timestamptz, 'P. Rao', 'disposal', 'Refund confirmed'),
  ('C-2026-0185', '2026-08-01 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0185', '2026-08-01 10:30:00+00'::timestamptz, 'S. Iyer', 'document', '2 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0185', '2026-08-01 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to S. Iyer · PGRC'),
  ('C-2026-0185', '2026-09-02 15:30:00+00'::timestamptz, 'S. Iyer', 'note', 'Notice to state office'),
  ('C-2026-0186', '2026-09-01 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0186', '2026-09-01 10:30:00+00'::timestamptz, 'K. Nair', 'document', '3 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0186', '2026-09-01 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to K. Nair · RB'),
  ('C-2026-0186', '2026-10-10 15:30:00+00'::timestamptz, 'K. Nair', 'transfer', 'Transferred by PGRC'),
  ('C-2026-0190', '2026-09-28 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0190', '2026-09-28 10:30:00+00'::timestamptz, 'R. Menon', 'document', '4 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0190', '2026-09-28 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to R. Menon · RB'),
  ('C-2026-0190', '2026-10-19 15:30:00+00'::timestamptz, 'R. Menon', 'note', 'Show-cause notice'),
  ('C-2026-0191', '2026-08-20 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0191', '2026-08-20 10:30:00+00'::timestamptz, 'A. Das', 'document', '2 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0191', '2026-08-20 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to A. Das · PGRC'),
  ('C-2026-0191', '2026-10-01 15:30:00+00'::timestamptz, 'A. Das', 'disposal', 'Refund processed'),
  ('C-2026-0192', '2026-10-18 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0192', '2026-10-18 10:30:00+00'::timestamptz, 'P. Rao', 'document', '1 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0192', '2026-10-18 11:15:00+00'::timestamptz, 'P. Rao', 'note', 'Unassigned — queued for PGRC lead'),
  ('C-2026-0192', '2026-10-18 15:30:00+00'::timestamptz, 'P. Rao', 'note', 'Case created'),
  ('C-2026-0193', '2026-10-05 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0193', '2026-10-05 10:30:00+00'::timestamptz, 'K. Nair', 'document', '3 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0193', '2026-10-05 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to K. Nair · RB'),
  ('C-2026-0193', '2026-10-20 15:30:00+00'::timestamptz, 'K. Nair', 'note', 'Documents under verification'),
  ('C-2026-0194', '2026-09-30 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0194', '2026-09-30 10:30:00+00'::timestamptz, 'P. Rao', 'document', '2 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0194', '2026-09-30 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to P. Rao · PGRC'),
  ('C-2026-0194', '2026-10-18 15:30:00+00'::timestamptz, 'P. Rao', 'note', 'College response sought'),
  ('C-2026-0195', '2026-10-12 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0195', '2026-10-12 10:30:00+00'::timestamptz, 'R. Menon', 'document', '2 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0195', '2026-10-12 11:15:00+00'::timestamptz, 'R. Menon', 'note', 'Unassigned — queued for RB lead'),
  ('C-2026-0195', '2026-10-12 15:30:00+00'::timestamptz, 'R. Menon', 'note', 'Case created'),
  ('C-2026-0196', '2026-10-01 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0196', '2026-10-01 10:30:00+00'::timestamptz, 'S. Iyer', 'document', '4 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0196', '2026-10-01 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to S. Iyer · PGRC'),
  ('C-2026-0196', '2026-10-19 15:30:00+00'::timestamptz, 'S. Iyer', 'note', 'Statements obtained'),
  ('C-2026-0197', '2026-10-08 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0197', '2026-10-08 10:30:00+00'::timestamptz, 'R. Menon', 'document', '3 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0197', '2026-10-08 11:15:00+00'::timestamptz, 'R. Menon', 'assigned', 'Assigned to R. Menon · RB'),
  ('C-2026-0197', '2026-10-20 15:30:00+00'::timestamptz, 'R. Menon', 'note', 'Inspection scheduled'),
  ('C-2026-0165', '2026-07-10 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0165', '2026-07-10 10:30:00+00'::timestamptz, 'A. Das', 'document', '5 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0165', '2026-07-10 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to A. Das · PGRC'),
  ('C-2026-0165', '2026-09-15 15:30:00+00'::timestamptz, 'A. Das', 'disposal', 'Compliance confirmed'),
  ('C-2026-0168', '2026-09-18 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0168', '2026-09-18 10:30:00+00'::timestamptz, 'P. Rao', 'document', '2 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0168', '2026-09-18 11:15:00+00'::timestamptz, 'P. Rao', 'assigned', 'Assigned to P. Rao · PGRC'),
  ('C-2026-0168', '2026-10-16 15:30:00+00'::timestamptz, 'P. Rao', 'note', 'College response sought'),
  ('C-2026-0169', '2026-10-14 09:30:00+00'::timestamptz, 'System', 'created', 'Case created from complaint'),
  ('C-2026-0169', '2026-10-14 10:30:00+00'::timestamptz, 'R. Menon', 'document', '1 document(s) uploaded and hashed (SHA-256)'),
  ('C-2026-0169', '2026-10-14 11:15:00+00'::timestamptz, 'R. Menon', 'note', 'Unassigned — queued for RB lead'),
  ('C-2026-0169', '2026-10-14 15:30:00+00'::timestamptz, 'R. Menon', 'note', 'Case created'),
  ('C-2026-0186', '2026-10-21 09:15:00+00'::timestamptz, 'System', 'escalation', 'Custody not accepted — escalated to Director')) as v(case_no, at, actor, kind, detail)
join cases c on c.case_no = v.case_no;

-- ---------------------------------------------------------------- documents
insert into documents (case_id, filename, mime, bytes, sha256, storage_key,
                       uploaded_by, uploaded_at)
select c.id, v.filename, v.mime, v.bytes::bigint, v.sha, v.key, u.id,
       v.at::timestamptz
from (values
  ('C-2026-0031', 'c-2026-0031_01_complaint.pdf', 'application/pdf', '1220656'::bigint, 'dea821d09c7585891975f5cf431da94058dde1f3559a4a5e400d808171d96692', 'demo/C-2026-0031/01-complaint.pdf', 'S. Iyer', '2026-02-05 00:01:00+00'::timestamptz),
  ('C-2026-0031', 'c-2026-0031_02_annexure-a.pdf', 'application/pdf', '995274'::bigint, '86617a6a45e8d85c0e5735ed6ed8fc2701c5ad90f471b5c8317804b8e7b06bb9', 'demo/C-2026-0031/02-annexure-a.pdf', 'S. Iyer', '2026-02-06 00:02:00+00'::timestamptz),
  ('C-2026-0031', 'c-2026-0031_03_institution-response.pdf', 'application/pdf', '2348766'::bigint, 'f0087f7e78b9f6b757647e5ade8679704bd13ed293f2ff1859e957e624fdba2a', 'demo/C-2026-0031/03-institution-response.pdf', 'S. Iyer', '2026-02-07 00:03:00+00'::timestamptz),
  ('C-2026-0042', 'c-2026-0042_01_complaint.pdf', 'application/pdf', '2244366'::bigint, '84e1b4ae5540f6a673fe2c93f83fa8b6c2a07f009e7ef6e746562828393fa6ae', 'demo/C-2026-0042/01-complaint.pdf', 'P. Rao', '2026-02-19 00:01:00+00'::timestamptz),
  ('C-2026-0042', 'c-2026-0042_02_annexure-a.pdf', 'application/pdf', '1120235'::bigint, '4f99818bb14320b9dfe746a557b1001b018598810071d201fa7ee80d9c74c97e', 'demo/C-2026-0042/02-annexure-a.pdf', 'P. Rao', '2026-02-20 00:02:00+00'::timestamptz),
  ('C-2026-0042', 'c-2026-0042_03_institution-response.pdf', 'application/pdf', '1499874'::bigint, '9d4c8d8202e8d761900851c5808af6d57510a60e8e1a5f8e1313f61a1796f00f', 'demo/C-2026-0042/03-institution-response.pdf', 'P. Rao', '2026-02-21 00:03:00+00'::timestamptz),
  ('C-2026-0042', 'c-2026-0042_04_inspection-note.pdf', 'application/pdf', '160563'::bigint, '3ca8e0d3a024c23ed9757434caa95e482146ddefc5bf01f3c6ec67dfc21780aa', 'demo/C-2026-0042/04-inspection-note.pdf', 'P. Rao', '2026-02-22 00:04:00+00'::timestamptz),
  ('C-2026-0057', 'c-2026-0057_01_complaint.pdf', 'application/pdf', '1529325'::bigint, 'de1a5b8dde0c092074f7f5a229cb19bad193c7127cf4e2169caf2034761b42ee', 'demo/C-2026-0057/01-complaint.pdf', 'A. Kumar', '2026-03-04 00:01:00+00'::timestamptz),
  ('C-2026-0057', 'c-2026-0057_02_annexure-a.pdf', 'application/pdf', '411084'::bigint, 'fe5da96c819d9bb77922baee12a24e9ae783a00ad1368640c3eab641fb9133a9', 'demo/C-2026-0057/02-annexure-a.pdf', 'A. Kumar', '2026-03-05 00:02:00+00'::timestamptz),
  ('C-2026-0068', 'c-2026-0068_01_complaint.pdf', 'application/pdf', '1642235'::bigint, '9b4e079beb834a5ba15c60b8ec903a4dc2c222221202bb7d41f795bdd9b2129d', 'demo/C-2026-0068/01-complaint.pdf', 'R. Menon', '2026-03-22 00:01:00+00'::timestamptz),
  ('C-2026-0068', 'c-2026-0068_02_annexure-a.pdf', 'application/pdf', '466724'::bigint, '49fb4fc4d855dbfb270c83ca0218c8e97739612b8e20f742107c4b68b88e23a1', 'demo/C-2026-0068/02-annexure-a.pdf', 'R. Menon', '2026-03-23 00:02:00+00'::timestamptz),
  ('C-2026-0068', 'c-2026-0068_03_institution-response.pdf', 'application/pdf', '1557300'::bigint, '9fe09bd469197e343f36c953b3abcdd6ff56644effa0357aebacbd257d22c4ff', 'demo/C-2026-0068/03-institution-response.pdf', 'R. Menon', '2026-03-24 00:03:00+00'::timestamptz),
  ('C-2026-0068', 'c-2026-0068_04_inspection-note.pdf', 'application/pdf', '1803545'::bigint, 'fabac2b95447ac67d2a0ddac8363eb04e8ffd60f032b7db7d0cc557c8ad07a43', 'demo/C-2026-0068/04-inspection-note.pdf', 'R. Menon', '2026-03-25 00:04:00+00'::timestamptz),
  ('C-2026-0068', 'c-2026-0068_05_fee-ledger.pdf', 'application/pdf', '1014583'::bigint, 'c39b99d772baeb10a330e5915eaee25d5a892eee72173a0f8b37d6edbff245f2', 'demo/C-2026-0068/05-fee-ledger.pdf', 'R. Menon', '2026-03-26 00:05:00+00'::timestamptz),
  ('C-2026-0079', 'c-2026-0079_01_complaint.pdf', 'application/pdf', '69856'::bigint, 'f67a4b80415c49e336a34f28e6adaead86104966f0160ceb55f2cf00b6a4bc8d', 'demo/C-2026-0079/01-complaint.pdf', 'K. Nair', '2026-04-08 00:01:00+00'::timestamptz),
  ('C-2026-0079', 'c-2026-0079_02_annexure-a.pdf', 'application/pdf', '1498735'::bigint, 'a950b50fb166ddf3290773330bb087d3f76ed83aea91888abfe58718f1c40d1a', 'demo/C-2026-0079/02-annexure-a.pdf', 'K. Nair', '2026-04-09 00:02:00+00'::timestamptz),
  ('C-2026-0091', 'c-2026-0091_01_complaint.pdf', 'application/pdf', '1848068'::bigint, 'd7af45a4ac1ce13e41aef65f29f51659448988b165c0f429c10e4afbb580b994', 'demo/C-2026-0091/01-complaint.pdf', 'M. Das', '2026-04-23 00:01:00+00'::timestamptz),
  ('C-2026-0091', 'c-2026-0091_02_annexure-a.pdf', 'application/pdf', '310159'::bigint, '0bbebf2fab469517a3cff0bd268f8d1bc95b733e34558e05030c47de14c270fe', 'demo/C-2026-0091/02-annexure-a.pdf', 'M. Das', '2026-04-24 00:02:00+00'::timestamptz),
  ('C-2026-0091', 'c-2026-0091_03_institution-response.pdf', 'application/pdf', '2331977'::bigint, 'eebea6e9f2f8620dd6b0a99aa067bee0e59495137298d89a827962b94393c08c', 'demo/C-2026-0091/03-institution-response.pdf', 'M. Das', '2026-04-25 00:03:00+00'::timestamptz),
  ('C-2026-0091', 'c-2026-0091_04_inspection-note.pdf', 'application/pdf', '2197270'::bigint, '3eed45b64bb37a924cc75c43e2fa209ed0826f5f27fd5599e21a3b4b16b011a9', 'demo/C-2026-0091/04-inspection-note.pdf', 'M. Das', '2026-04-26 00:04:00+00'::timestamptz),
  ('C-2026-0091', 'c-2026-0091_05_fee-ledger.pdf', 'application/pdf', '1303795'::bigint, 'd8cbef93fc6e570d689294ca261c8158ab559cfdc95de4996110efcc6caf2afd', 'demo/C-2026-0091/05-fee-ledger.pdf', 'M. Das', '2026-04-27 00:05:00+00'::timestamptz),
  ('C-2026-0091', 'c-2026-0091_06_attendance-register.pdf', 'application/pdf', '169977'::bigint, '375e0a992fae67dd10d2ded0802c21e70528747dc0ecc95deca959adde8ac6ea', 'demo/C-2026-0091/06-attendance-register.pdf', 'M. Das', '2026-04-28 00:06:00+00'::timestamptz),
  ('C-2026-0104', 'c-2026-0104_01_complaint.pdf', 'application/pdf', '2234130'::bigint, '48a811b2bbdd8bdfc23d9fecf393ae02ab9d7b67316cd9120f971a5af5bbc115', 'demo/C-2026-0104/01-complaint.pdf', 'S. Iyer', '2026-05-12 00:01:00+00'::timestamptz),
  ('C-2026-0104', 'c-2026-0104_02_annexure-a.pdf', 'application/pdf', '1151163'::bigint, 'f31be35bbc51d9394b02fd451fa48884c7d8d537c7adfafe6b137e954425b2b1', 'demo/C-2026-0104/02-annexure-a.pdf', 'S. Iyer', '2026-05-13 00:02:00+00'::timestamptz),
  ('C-2026-0104', 'c-2026-0104_03_institution-response.pdf', 'application/pdf', '936103'::bigint, 'cc9d88474a5161c87cb3cc8ed3844c94906a99afc3085d2ea8635911d09ce730', 'demo/C-2026-0104/03-institution-response.pdf', 'S. Iyer', '2026-05-14 00:03:00+00'::timestamptz),
  ('C-2026-0104', 'c-2026-0104_04_inspection-note.pdf', 'application/pdf', '1960873'::bigint, 'ea251d49b530078c04c1201429544f0f32d37154b2468a546ca4a047dd02e320', 'demo/C-2026-0104/04-inspection-note.pdf', 'S. Iyer', '2026-05-15 00:04:00+00'::timestamptz),
  ('C-2026-0118', 'c-2026-0118_01_complaint.pdf', 'application/pdf', '280983'::bigint, '36840237eede400aa2798d51050349df161b7c3b74a6f384ab4845553871a049', 'demo/C-2026-0118/01-complaint.pdf', 'P. Rao', '2026-06-03 00:01:00+00'::timestamptz),
  ('C-2026-0118', 'c-2026-0118_02_annexure-a.pdf', 'application/pdf', '1183130'::bigint, '2f217a3a4030f898a0cfb660d9cdb4c479b2ce1fc4246fa526c2fa40f0983e0c', 'demo/C-2026-0118/02-annexure-a.pdf', 'P. Rao', '2026-06-04 00:02:00+00'::timestamptz),
  ('C-2026-0118', 'c-2026-0118_03_institution-response.pdf', 'application/pdf', '2147042'::bigint, 'ea4c9382721ee1201af5c8aa2d348c24cb4a769a240a6e9d7f10d6d89ec403e1', 'demo/C-2026-0118/03-institution-response.pdf', 'P. Rao', '2026-06-05 00:03:00+00'::timestamptz),
  ('C-2026-0118', 'c-2026-0118_04_inspection-note.pdf', 'application/pdf', '180349'::bigint, 'de73a31dea15b68a637e7a10fac6cd2e13976fe4ddec2a158364adafe1fd73c9', 'demo/C-2026-0118/04-inspection-note.pdf', 'P. Rao', '2026-06-06 00:04:00+00'::timestamptz),
  ('C-2026-0118', 'c-2026-0118_05_fee-ledger.pdf', 'application/pdf', '374683'::bigint, '20eba73bdd7d78839f710736bda404639b630d5d2cf7b8ec1f909c3010dae05e', 'demo/C-2026-0118/05-fee-ledger.pdf', 'P. Rao', '2026-06-07 00:05:00+00'::timestamptz),
  ('C-2026-0118', 'c-2026-0118_06_attendance-register.pdf', 'application/pdf', '122290'::bigint, 'baf8b852cffb0712d2877d24c6cb4218522afb74f4cb39864a4b09fc5b3b7ba4', 'demo/C-2026-0118/06-attendance-register.pdf', 'P. Rao', '2026-06-08 00:06:00+00'::timestamptz),
  ('C-2026-0118', 'c-2026-0118_07_correspondence.pdf', 'application/pdf', '2298042'::bigint, 'da00135a64e14cec3871826ff558a50bc6ab5892b680270fe5f1777575acefd8', 'demo/C-2026-0118/07-correspondence.pdf', 'P. Rao', '2026-06-08 00:07:00+00'::timestamptz),
  ('C-2026-0129', 'c-2026-0129_01_complaint.pdf', 'application/pdf', '2352710'::bigint, '2e5798e63b71a9f1269fed0a5efd237ecdaa1da7ecec03654afaf75139aa38ff', 'demo/C-2026-0129/01-complaint.pdf', 'A. Kumar', '2026-06-20 00:01:00+00'::timestamptz),
  ('C-2026-0129', 'c-2026-0129_02_annexure-a.pdf', 'application/pdf', '277817'::bigint, 'e4e512d964c1f27a07a56297c1335c33626f36a26d5c823e67b4a7891ae85ae6', 'demo/C-2026-0129/02-annexure-a.pdf', 'A. Kumar', '2026-06-21 00:02:00+00'::timestamptz),
  ('C-2026-0129', 'c-2026-0129_03_institution-response.pdf', 'application/pdf', '2100635'::bigint, '232b4e3b3491a5cd5b785672152184a93aeb023d576d5e7e2f0f4089f895be4e', 'demo/C-2026-0129/03-institution-response.pdf', 'A. Kumar', '2026-06-22 00:03:00+00'::timestamptz),
  ('C-2026-0131', 'c-2026-0131_01_complaint.pdf', 'application/pdf', '978495'::bigint, '226313dfe2d55dd97a68e3a44050e633bb04b541277b66f7a2294ea44186cbf2', 'demo/C-2026-0131/01-complaint.pdf', 'R. Menon', '2026-07-03 00:01:00+00'::timestamptz),
  ('C-2026-0131', 'c-2026-0131_02_annexure-a.pdf', 'application/pdf', '1105875'::bigint, '735c8f7319a9e688a7d2047c81f96ff98d6e55c6cc55b76505f9e7c27c4000c3', 'demo/C-2026-0131/02-annexure-a.pdf', 'R. Menon', '2026-07-04 00:02:00+00'::timestamptz),
  ('C-2026-0131', 'c-2026-0131_03_institution-response.pdf', 'application/pdf', '2167716'::bigint, '35e9b144e0dfc44a3d0cc4d76715d1fcc5082467c75f22f38f1483b5bcbf3a75', 'demo/C-2026-0131/03-institution-response.pdf', 'R. Menon', '2026-07-05 00:03:00+00'::timestamptz),
  ('C-2026-0131', 'c-2026-0131_04_inspection-note.pdf', 'application/pdf', '326450'::bigint, '845693d23a04db9e91644b498f9d3df00c4c5b97d45a19790554da2c69090af7', 'demo/C-2026-0131/04-inspection-note.pdf', 'R. Menon', '2026-07-06 00:04:00+00'::timestamptz),
  ('C-2026-0142', 'c-2026-0142_01_complaint.pdf', 'application/pdf', '951903'::bigint, 'ed16c2ff254825789506f8e9d735bb92824676892645b81036b8f46e7e8d0e3a', 'demo/C-2026-0142/01-complaint.pdf', 'P. Rao', '2026-09-13 00:01:00+00'::timestamptz),
  ('C-2026-0142', 'c-2026-0142_02_annexure-a.pdf', 'application/pdf', '449992'::bigint, '7e5660680e2b24722563c8869f406e09c682fa95569ed25cfe2943ab092c2582', 'demo/C-2026-0142/02-annexure-a.pdf', 'P. Rao', '2026-09-14 00:02:00+00'::timestamptz),
  ('C-2026-0142', 'c-2026-0142_03_institution-response.pdf', 'application/pdf', '740353'::bigint, '5b4ea3a10b5a8ecdc258566ada1655d5bd9aa0feb518451c6cd98ad7d282d433', 'demo/C-2026-0142/03-institution-response.pdf', 'P. Rao', '2026-09-15 00:03:00+00'::timestamptz),
  ('C-2026-0167', 'c-2026-0167_01_complaint.pdf', 'application/pdf', '2017022'::bigint, '5e63299ea1808b667a8f5c6146ad021795a278dcbf6e815f95fd5475b2de8ae6', 'demo/C-2026-0167/01-complaint.pdf', 'R. Menon', '2026-10-03 00:01:00+00'::timestamptz),
  ('C-2026-0167', 'c-2026-0167_02_annexure-a.pdf', 'application/pdf', '2003925'::bigint, '5b3d4c75b4591c6de0a2462f980abbc97bfafa930fa275b2058b1603677db399', 'demo/C-2026-0167/02-annexure-a.pdf', 'R. Menon', '2026-10-04 00:02:00+00'::timestamptz),
  ('C-2026-0167', 'c-2026-0167_03_institution-response.pdf', 'application/pdf', '1235611'::bigint, 'c9ea4d3bf2edcc4f7e39c4cdb5641533959f797c9b57a6a0ca4a1c9ac07a48fe', 'demo/C-2026-0167/03-institution-response.pdf', 'R. Menon', '2026-10-05 00:03:00+00'::timestamptz),
  ('C-2026-0167', 'c-2026-0167_04_inspection-note.pdf', 'application/pdf', '1860482'::bigint, 'd8669122c915bd3c5805e444b312df326ad002abd10d7c8238fa579618415e62', 'demo/C-2026-0167/04-inspection-note.pdf', 'R. Menon', '2026-10-06 00:04:00+00'::timestamptz),
  ('C-2026-0167', 'c-2026-0167_05_fee-ledger.pdf', 'application/pdf', '338350'::bigint, '9982ae4ee0358b30d39b11512da80621db3e777248cb6124e29c1bd109096be8', 'demo/C-2026-0167/05-fee-ledger.pdf', 'R. Menon', '2026-10-07 00:05:00+00'::timestamptz),
  ('C-2026-0198', 'c-2026-0198_01_complaint.pdf', 'application/pdf', '430939'::bigint, '07e3d1fb1369629be6a54084787a6ebc5e8a7d8eab8767e275737261eb880c9b', 'demo/C-2026-0198/01-complaint.pdf', null, '2026-10-22 00:01:00+00'::timestamptz),
  ('C-2026-0180', 'c-2026-0180_01_complaint.pdf', 'application/pdf', '1965674'::bigint, 'ac0fa20a4d528b8999747be571eaf2b20c320f3d9a8aafdcfb8577e39c2ce769', 'demo/C-2026-0180/01-complaint.pdf', 'S. Iyer', '2026-08-29 00:01:00+00'::timestamptz),
  ('C-2026-0180', 'c-2026-0180_02_annexure-a.pdf', 'application/pdf', '1477599'::bigint, 'b630487f06eab3b6a7e0a4bd11e8db274396dd9d05d54d1bf89fcd03d135b3d9', 'demo/C-2026-0180/02-annexure-a.pdf', 'S. Iyer', '2026-08-30 00:02:00+00'::timestamptz),
  ('C-2026-0180', 'c-2026-0180_03_institution-response.pdf', 'application/pdf', '2451219'::bigint, '2b0ed0b3b1ffa4fa008daace85e414136b02bf8b6802314e5c2e830bdf68b1cc', 'demo/C-2026-0180/03-institution-response.pdf', 'S. Iyer', '2026-08-31 00:03:00+00'::timestamptz),
  ('C-2026-0180', 'c-2026-0180_04_inspection-note.pdf', 'application/pdf', '1825007'::bigint, '50edd98f7f00971f27cca13a3d9117d0cff266a76dbd2ee2fec404493fb6430c', 'demo/C-2026-0180/04-inspection-note.pdf', 'S. Iyer', '2026-09-01 00:04:00+00'::timestamptz),
  ('C-2026-0181', 'c-2026-0181_01_complaint.pdf', 'application/pdf', '857164'::bigint, '12c986ec2be5ad66208cf0753461ccfc6e8db637a80964b0c602ccd49b4e5ed9', 'demo/C-2026-0181/01-complaint.pdf', 'K. Nair', '2026-09-06 00:01:00+00'::timestamptz),
  ('C-2026-0181', 'c-2026-0181_02_annexure-a.pdf', 'application/pdf', '651548'::bigint, 'e3a12fbc1dadd8b561895389e27679280e5a55ca06accc71561e663dc9756e2a', 'demo/C-2026-0181/02-annexure-a.pdf', 'K. Nair', '2026-09-07 00:02:00+00'::timestamptz),
  ('C-2026-0181', 'c-2026-0181_03_institution-response.pdf', 'application/pdf', '1630127'::bigint, 'b6e9b74f70ff7fff7d17dbd3b8207307cb92b61b727e99e1652c9d0862f2e3f8', 'demo/C-2026-0181/03-institution-response.pdf', 'K. Nair', '2026-09-08 00:03:00+00'::timestamptz),
  ('C-2026-0181', 'c-2026-0181_04_inspection-note.pdf', 'application/pdf', '1980313'::bigint, '2a2be73905d21cccce8d5260bd5181e0bb6ed1acb2dea421b3360b7807fe15cc', 'demo/C-2026-0181/04-inspection-note.pdf', 'K. Nair', '2026-09-09 00:04:00+00'::timestamptz),
  ('C-2026-0181', 'c-2026-0181_05_fee-ledger.pdf', 'application/pdf', '566467'::bigint, '851158632d6f1af38eff9a538811dd2d9f90d17eca365e853160117f1af9f4f3', 'demo/C-2026-0181/05-fee-ledger.pdf', 'K. Nair', '2026-09-10 00:05:00+00'::timestamptz),
  ('C-2026-0181', 'c-2026-0181_06_attendance-register.pdf', 'application/pdf', '853678'::bigint, '02560c4e6875daff658ea1fe8c2c1e136666422b7e360aba6457f9c9702ec0cd', 'demo/C-2026-0181/06-attendance-register.pdf', 'K. Nair', '2026-09-11 00:06:00+00'::timestamptz),
  ('C-2026-0155', 'c-2026-0155_01_complaint.pdf', 'application/pdf', '2211760'::bigint, '40ee3050509869fcab57cf29b3c2552b16e35bf1b71ba8644571105749283d67', 'demo/C-2026-0155/01-complaint.pdf', 'A. Das', '2026-09-21 00:01:00+00'::timestamptz),
  ('C-2026-0155', 'c-2026-0155_02_annexure-a.pdf', 'application/pdf', '1602043'::bigint, '2a6f5f9bc897e7e7efa4141841baacaca66e68ef3bc7451dda79597860c9170a', 'demo/C-2026-0155/02-annexure-a.pdf', 'A. Das', '2026-09-22 00:02:00+00'::timestamptz),
  ('C-2026-0155', 'c-2026-0155_03_institution-response.pdf', 'application/pdf', '1693736'::bigint, '9ebdb8c884001e6cd26c90c6a443e5eb05b3c5bae1178df69fc98c6f62c94096', 'demo/C-2026-0155/03-institution-response.pdf', 'A. Das', '2026-09-23 00:03:00+00'::timestamptz),
  ('C-2026-0155', 'c-2026-0155_04_inspection-note.pdf', 'application/pdf', '1709936'::bigint, '2f298410eef975dbd3aca479f84f0387271870720bbf51788e194d36b21b9faf', 'demo/C-2026-0155/04-inspection-note.pdf', 'A. Das', '2026-09-24 00:04:00+00'::timestamptz),
  ('C-2026-0155', 'c-2026-0155_05_fee-ledger.pdf', 'application/pdf', '1858652'::bigint, '22b9bffc06850e0b43df79c239f6e0897d708047612599b634300034a2db78b7', 'demo/C-2026-0155/05-fee-ledger.pdf', 'A. Das', '2026-09-25 00:05:00+00'::timestamptz),
  ('C-2026-0155', 'c-2026-0155_06_attendance-register.pdf', 'application/pdf', '2056944'::bigint, '60d2549089deed469eddbbdce1dd29991a8811f7bf5551eb4b6e01949bdb6468', 'demo/C-2026-0155/06-attendance-register.pdf', 'A. Das', '2026-09-26 00:06:00+00'::timestamptz),
  ('C-2026-0155', 'c-2026-0155_07_correspondence.pdf', 'application/pdf', '987962'::bigint, '153a14da81b959099c30dc4c5cb62d3ee0b2baaee98c915cce1fd199fb3f4570', 'demo/C-2026-0155/07-correspondence.pdf', 'A. Das', '2026-09-26 00:07:00+00'::timestamptz),
  ('C-2026-0160', 'c-2026-0160_01_complaint.pdf', 'application/pdf', '1674784'::bigint, '61839ac004cfdde5d4203633f9e21c7d0d0f1f41146c83bf1436d659de6cf940', 'demo/C-2026-0160/01-complaint.pdf', 'R. Menon', '2026-09-26 00:01:00+00'::timestamptz),
  ('C-2026-0160', 'c-2026-0160_02_annexure-a.pdf', 'application/pdf', '2421076'::bigint, 'c3fa4df445f8dc4c4d5df8e04d1766565933c24605095c6c4f77bb32a16500c3', 'demo/C-2026-0160/02-annexure-a.pdf', 'R. Menon', '2026-09-27 00:02:00+00'::timestamptz),
  ('C-2026-0160', 'c-2026-0160_03_institution-response.pdf', 'application/pdf', '554245'::bigint, 'cd980da5a193908cb111a47e7901672b9fece1da94548e6619a49d0f60ace46c', 'demo/C-2026-0160/03-institution-response.pdf', 'R. Menon', '2026-09-28 00:03:00+00'::timestamptz),
  ('C-2026-0160', 'c-2026-0160_04_inspection-note.pdf', 'application/pdf', '1708928'::bigint, '8522c7201a72d3783a6b4e93efd36583c971248613ce4750a34e044e1039a8f1', 'demo/C-2026-0160/04-inspection-note.pdf', 'R. Menon', '2026-09-29 00:04:00+00'::timestamptz),
  ('C-2026-0171', 'c-2026-0171_01_complaint.pdf', 'application/pdf', '937389'::bigint, 'b771a14d70c5b5ac00056c00782dfcd86bab6ae84ef50d50a17145dded352dae', 'demo/C-2026-0171/01-complaint.pdf', null, '2026-10-11 00:01:00+00'::timestamptz),
  ('C-2026-0171', 'c-2026-0171_02_annexure-a.pdf', 'application/pdf', '2000546'::bigint, 'a5325a42540463f32639e3d3f6650845a9764dd55f292abccfd16f4cbe772290', 'demo/C-2026-0171/02-annexure-a.pdf', null, '2026-10-12 00:02:00+00'::timestamptz),
  ('C-2026-0172', 'c-2026-0172_01_complaint.pdf', 'application/pdf', '570434'::bigint, '607267e27964016e7a50750525f9b6563404c452c992f0b8717f7a327df83f31', 'demo/C-2026-0172/01-complaint.pdf', 'P. Rao', '2026-08-16 00:01:00+00'::timestamptz),
  ('C-2026-0172', 'c-2026-0172_02_annexure-a.pdf', 'application/pdf', '2351587'::bigint, '29e853837e940f91281eb43ece6a59a23b0316360d96df714fc0eab7b3d8a36d', 'demo/C-2026-0172/02-annexure-a.pdf', 'P. Rao', '2026-08-17 00:02:00+00'::timestamptz),
  ('C-2026-0172', 'c-2026-0172_03_institution-response.pdf', 'application/pdf', '342791'::bigint, '7608b7a79933e42f724f2359ca06155589b662e2067c0aed98157b784f62a31e', 'demo/C-2026-0172/03-institution-response.pdf', 'P. Rao', '2026-08-18 00:03:00+00'::timestamptz),
  ('C-2026-0185', 'c-2026-0185_01_complaint.pdf', 'application/pdf', '1379374'::bigint, 'f94613ce0780924a64f7be65836608d5940df6118c0101494bfaf118f1751975', 'demo/C-2026-0185/01-complaint.pdf', 'S. Iyer', '2026-08-02 00:01:00+00'::timestamptz),
  ('C-2026-0185', 'c-2026-0185_02_annexure-a.pdf', 'application/pdf', '748763'::bigint, 'fed0ad7b7d606b83270208be269b93719f321c993ef6fdcea8cead8e62089308', 'demo/C-2026-0185/02-annexure-a.pdf', 'S. Iyer', '2026-08-03 00:02:00+00'::timestamptz),
  ('C-2026-0186', 'c-2026-0186_01_complaint.pdf', 'application/pdf', '1798013'::bigint, 'ea6bdf1d92cd7dc471874b71a5897bfe137071c52c326c5bfc4eb094d5a56a2e', 'demo/C-2026-0186/01-complaint.pdf', 'K. Nair', '2026-09-02 00:01:00+00'::timestamptz),
  ('C-2026-0186', 'c-2026-0186_02_annexure-a.pdf', 'application/pdf', '1887605'::bigint, '7f236b150a38400d67308cf9023a5adf9084e83985b633cd10991fb8985d7239', 'demo/C-2026-0186/02-annexure-a.pdf', 'K. Nair', '2026-09-03 00:02:00+00'::timestamptz),
  ('C-2026-0186', 'c-2026-0186_03_institution-response.pdf', 'application/pdf', '346430'::bigint, 'd9bdacdef36bc53f025476602e457f98be3af693a3d39771a7582178b1684726', 'demo/C-2026-0186/03-institution-response.pdf', 'K. Nair', '2026-09-04 00:03:00+00'::timestamptz),
  ('C-2026-0190', 'c-2026-0190_01_complaint.pdf', 'application/pdf', '800943'::bigint, 'f7f3a94f488c8fa6a278089e07ddce619dd4778e68ff93671391ac75e2c2b8d8', 'demo/C-2026-0190/01-complaint.pdf', 'R. Menon', '2026-09-29 00:01:00+00'::timestamptz),
  ('C-2026-0190', 'c-2026-0190_02_annexure-a.pdf', 'application/pdf', '2321743'::bigint, '0a4a9befe15fedab5fa0bae9ef18ff9dc7d8ce14580859395796aa95c5d80160', 'demo/C-2026-0190/02-annexure-a.pdf', 'R. Menon', '2026-09-30 00:02:00+00'::timestamptz),
  ('C-2026-0190', 'c-2026-0190_03_institution-response.pdf', 'application/pdf', '1132129'::bigint, 'd10fc7012863da1c806d04034d7f7760c022fabbedbc668e5325972e68363a67', 'demo/C-2026-0190/03-institution-response.pdf', 'R. Menon', '2026-10-01 00:03:00+00'::timestamptz),
  ('C-2026-0190', 'c-2026-0190_04_inspection-note.pdf', 'application/pdf', '780075'::bigint, '6476fecb38cd3bd7b3939ed946703ab048f2713ff86e6ba91d4171c23e068d93', 'demo/C-2026-0190/04-inspection-note.pdf', 'R. Menon', '2026-10-02 00:04:00+00'::timestamptz),
  ('C-2026-0191', 'c-2026-0191_01_complaint.pdf', 'application/pdf', '1814026'::bigint, '4cc7abaafd6b56d980db7dd16211381308b8c58e97f05bce943975d9cce2601d', 'demo/C-2026-0191/01-complaint.pdf', 'A. Das', '2026-08-21 00:01:00+00'::timestamptz),
  ('C-2026-0191', 'c-2026-0191_02_annexure-a.pdf', 'application/pdf', '1363357'::bigint, 'b02c743dbec9578b494f5de3cdce9fdcf5995a59628c4438795f61ada184249b', 'demo/C-2026-0191/02-annexure-a.pdf', 'A. Das', '2026-08-22 00:02:00+00'::timestamptz),
  ('C-2026-0192', 'c-2026-0192_01_complaint.pdf', 'application/pdf', '302832'::bigint, '829ec3909aaf04360c2e143d6c78186b4916e947fb6ebe32e69eb394515a0ce6', 'demo/C-2026-0192/01-complaint.pdf', null, '2026-10-19 00:01:00+00'::timestamptz),
  ('C-2026-0193', 'c-2026-0193_01_complaint.pdf', 'application/pdf', '1619135'::bigint, 'd1a9b15fe3374ad939e93ebf2dc75fb0cee659c718e552c384c93b2e8441a5e2', 'demo/C-2026-0193/01-complaint.pdf', 'K. Nair', '2026-10-06 00:01:00+00'::timestamptz),
  ('C-2026-0193', 'c-2026-0193_02_annexure-a.pdf', 'application/pdf', '1039184'::bigint, '16a912f095268a82396e24f41d2fa6f09ab762957cdba5b46be6f5e1b12ef937', 'demo/C-2026-0193/02-annexure-a.pdf', 'K. Nair', '2026-10-07 00:02:00+00'::timestamptz),
  ('C-2026-0193', 'c-2026-0193_03_institution-response.pdf', 'application/pdf', '1187315'::bigint, 'e73ce393176187cd34b3d3f8e8eee7164c442a13d0bdc9aca0243b1668373f34', 'demo/C-2026-0193/03-institution-response.pdf', 'K. Nair', '2026-10-08 00:03:00+00'::timestamptz),
  ('C-2026-0194', 'c-2026-0194_01_complaint.pdf', 'application/pdf', '228125'::bigint, 'd9973fbd94bb1adae51a21d20b4505694c3f5cbec6909a667ffdae92ff1be7c0', 'demo/C-2026-0194/01-complaint.pdf', 'P. Rao', '2026-10-01 00:01:00+00'::timestamptz),
  ('C-2026-0194', 'c-2026-0194_02_annexure-a.pdf', 'application/pdf', '1969307'::bigint, 'f203673bb1b5a4eaad35ca4f0e30eab7cecd8080644df860e811d7551dc5a7f8', 'demo/C-2026-0194/02-annexure-a.pdf', 'P. Rao', '2026-10-02 00:02:00+00'::timestamptz),
  ('C-2026-0195', 'c-2026-0195_01_complaint.pdf', 'application/pdf', '752936'::bigint, '502662c89071d4b33de3a8ebe889598ca56748b5d5a30a2afca327905618a459', 'demo/C-2026-0195/01-complaint.pdf', null, '2026-10-13 00:01:00+00'::timestamptz),
  ('C-2026-0195', 'c-2026-0195_02_annexure-a.pdf', 'application/pdf', '1911374'::bigint, '71d604ee9c7d39f69a03300d74a71b46c10d4d7bd1e6b9a4bf87340f1e7d963c', 'demo/C-2026-0195/02-annexure-a.pdf', null, '2026-10-14 00:02:00+00'::timestamptz),
  ('C-2026-0196', 'c-2026-0196_01_complaint.pdf', 'application/pdf', '1446261'::bigint, '10d1d215f8f16bd201c2da7d3b7c5c7e2ed98ad16cb1916d43dde3a5206a4da9', 'demo/C-2026-0196/01-complaint.pdf', 'S. Iyer', '2026-10-02 00:01:00+00'::timestamptz),
  ('C-2026-0196', 'c-2026-0196_02_annexure-a.pdf', 'application/pdf', '811019'::bigint, '61088fab2d7b2b8e196f6b15f1278d7216f2fd90af555576ab28e6400790c95b', 'demo/C-2026-0196/02-annexure-a.pdf', 'S. Iyer', '2026-10-03 00:02:00+00'::timestamptz),
  ('C-2026-0196', 'c-2026-0196_03_institution-response.pdf', 'application/pdf', '2175826'::bigint, '032153f2b2506671ab9bb689e39f683883ee271b38b2eee77dff310528d696d5', 'demo/C-2026-0196/03-institution-response.pdf', 'S. Iyer', '2026-10-04 00:03:00+00'::timestamptz),
  ('C-2026-0196', 'c-2026-0196_04_inspection-note.pdf', 'application/pdf', '1534202'::bigint, '31dea29a0a10b2e1deea4e3d9d2d595398b69f0c32f00a5260ef8ce4211a84b2', 'demo/C-2026-0196/04-inspection-note.pdf', 'S. Iyer', '2026-10-05 00:04:00+00'::timestamptz),
  ('C-2026-0197', 'c-2026-0197_01_complaint.pdf', 'application/pdf', '1005973'::bigint, '86f420358a929fca95f37346f9e15eaf3dc1e431d3771e17ad3c5f2bd57a26e9', 'demo/C-2026-0197/01-complaint.pdf', 'R. Menon', '2026-10-09 00:01:00+00'::timestamptz),
  ('C-2026-0197', 'c-2026-0197_02_annexure-a.pdf', 'application/pdf', '2181129'::bigint, '6cb3c6a9e3f23c266e0494b6eac6cdb1704212dda0e5f119a367ccc972e02889', 'demo/C-2026-0197/02-annexure-a.pdf', 'R. Menon', '2026-10-10 00:02:00+00'::timestamptz),
  ('C-2026-0197', 'c-2026-0197_03_institution-response.pdf', 'application/pdf', '915720'::bigint, 'a4d88ea8524e64fbb4483fa03d8a3d46d55d9fa9792307f568e650ee4421caae', 'demo/C-2026-0197/03-institution-response.pdf', 'R. Menon', '2026-10-11 00:03:00+00'::timestamptz),
  ('C-2026-0165', 'c-2026-0165_01_complaint.pdf', 'application/pdf', '1655798'::bigint, '70888796663bfe74fdf21c846e2f4288a91b2f0a0e57efe4836aa7af43abafcc', 'demo/C-2026-0165/01-complaint.pdf', 'A. Das', '2026-07-11 00:01:00+00'::timestamptz),
  ('C-2026-0165', 'c-2026-0165_02_annexure-a.pdf', 'application/pdf', '787494'::bigint, '1b5dbac62b38f40d12178a459d9c0d0708b9dc1d9b0fe9de7a6e0dd7b2848af4', 'demo/C-2026-0165/02-annexure-a.pdf', 'A. Das', '2026-07-12 00:02:00+00'::timestamptz),
  ('C-2026-0165', 'c-2026-0165_03_institution-response.pdf', 'application/pdf', '137469'::bigint, '782ae69da57f2f3004b99e15aa6fe7c6a0b9157b2e476d094c3a5a5e712e9470', 'demo/C-2026-0165/03-institution-response.pdf', 'A. Das', '2026-07-13 00:03:00+00'::timestamptz),
  ('C-2026-0165', 'c-2026-0165_04_inspection-note.pdf', 'application/pdf', '931992'::bigint, '9ffbb038cf6d099abb9d499d382656a78f665082e135ed61d199d2816926fda6', 'demo/C-2026-0165/04-inspection-note.pdf', 'A. Das', '2026-07-14 00:04:00+00'::timestamptz),
  ('C-2026-0165', 'c-2026-0165_05_fee-ledger.pdf', 'application/pdf', '2272883'::bigint, '88e38813e3fc7209a969db4d12c9c6bf5ca31beaf9f6735307669cd67cb2a8f4', 'demo/C-2026-0165/05-fee-ledger.pdf', 'A. Das', '2026-07-15 00:05:00+00'::timestamptz),
  ('C-2026-0168', 'c-2026-0168_01_complaint.pdf', 'application/pdf', '1525461'::bigint, '7dd44d757c9868b478e0ebb5570b3dff37e62993abdff59beeffb954495e5139', 'demo/C-2026-0168/01-complaint.pdf', 'P. Rao', '2026-09-19 00:01:00+00'::timestamptz),
  ('C-2026-0168', 'c-2026-0168_02_annexure-a.pdf', 'application/pdf', '2303788'::bigint, 'd590e8ccca7ed1fdfccf3d955c3603301bab023cebe3bb9b7a67b05e1a61f471', 'demo/C-2026-0168/02-annexure-a.pdf', 'P. Rao', '2026-09-20 00:02:00+00'::timestamptz),
  ('C-2026-0169', 'c-2026-0169_01_complaint.pdf', 'application/pdf', '1280687'::bigint, '4c086d4f8206188f71b105022838b30336319e6a0fbae6ebe0013fe3faf1d9f8', 'demo/C-2026-0169/01-complaint.pdf', null, '2026-10-15 00:01:00+00'::timestamptz)) as v(case_no, filename, mime, bytes, sha, key, officer, at)
join cases c on c.case_no = v.case_no
left join users u on u.full_name = v.officer;

-- ------------------------------------------------------- overlap clusters
insert into overlap_clusters (ref, institution_id, confidence, state, reason, detected_at)
select v.ref, i.id, v.confidence::numeric, v.state, v.reason::jsonb,
       v.detected_at::timestamptz
from (values
  ('CL-01', '1-1234567', '98'::numeric, 'open', '["Same AICTE Permanent ID", "Alias matched: V.S. College of Engineering", "Same issue cluster: fee / scholarship", "Location match: Kanchipuram"]'::jsonb, '2026-10-20 10:38:00+00'::timestamptz),
  ('CL-02', '1-2345678', '94'::numeric, 'open', '["Same AICTE Permanent ID", "Same issue cluster: approval / faculty", "Both open across PGRC and RB"]'::jsonb, '2026-10-19 15:10:00+00'::timestamptz),
  ('CL-03', '1-5566778', '97'::numeric, 'open', '["Same AICTE Permanent ID", "Alias matched: VNIET Hyderabad", "Same issue cluster: admission / course approval"]'::jsonb, '2026-10-21 09:12:00+00'::timestamptz)) as v(ref, pid, confidence, state, reason, detected_at)
join institutions i on i.permanent_id = v.pid;

insert into overlap_cases (overlap_id, case_id)
select o.id, c.id
from (values
  ('CL-01', 'C-2026-0142'),
  ('CL-01', 'C-2026-0167'),
  ('CL-01', 'C-2026-0198'),
  ('CL-02', 'C-2026-0180'),
  ('CL-02', 'C-2026-0181'),
  ('CL-03', 'C-2026-0196'),
  ('CL-03', 'C-2026-0197')) as v(ref, case_no)
join overlap_clusters o on o.ref = v.ref
join cases c on c.case_no = v.case_no;

-- ------------------------------------------------------------------- rooms
insert into rooms (ref, overlap_id, lead_bureau, custody, state, opened_at)
select v.ref, o.id, v.lead_bureau, v.custody, 'open', v.opened_at::timestamptz
from (values
  ('CR-01', 'CL-01', null::text, 'Each case keeps its bureau of origin', '2026-10-20 10:45:00+00'::timestamptz),
  ('CR-02', 'CL-02', null::text, 'Each case keeps its bureau of origin', '2026-10-19 15:12:00+00'::timestamptz),
  ('CR-03', 'CL-03', null::text, 'Each case keeps its bureau of origin', '2026-10-21 09:20:00+00'::timestamptz)) as v(ref, overlap_ref, lead_bureau, custody, opened_at)
join overlap_clusters o on o.ref = v.overlap_ref;

insert into room_activity (room_id, at, actor, action)
select r.id, v.at::timestamptz, v.actor, v.action
from (values
  ('CR-01', '2026-10-20 10:38:00+00'::timestamptz, 'System', 'detected overlap with 98% confidence'),
  ('CR-01', '2026-10-20 10:42:00+00'::timestamptz, 'R. Menon', 'linked C-2026-0167 to C-2026-0142'),
  ('CR-01', '2026-10-20 10:45:00+00'::timestamptz, 'P. Rao', 'opened Coordination Room CR-01'),
  ('CR-02', '2026-10-19 15:10:00+00'::timestamptz, 'System', 'detected overlap with 94% confidence'),
  ('CR-03', '2026-10-21 09:12:00+00'::timestamptz, 'System', 'detected overlap with 97% confidence')) as v(ref, at, actor, action)
join rooms r on r.ref = v.ref;

-- ------------------------------------------------------------- audit chain
-- Oldest first. Each row commits to the hash of the row above it.
insert into audit_entries (at, actor, action, object, prev_hash, hash) values
  ('2026-10-16 10:30:00+00'::timestamptz, 'S. Iyer', 'Escalated to Director', 'C-2026-0180', '0000000000000000000000000000000000000000000000000000000000000000', 'c66427ddb32f7b32aec69e875146088b29acfed581d1995dd59a85f1f70d0739'),
  ('2026-10-16 14:05:00+00'::timestamptz, 'P. Rao', 'College response sought', 'C-2026-0168', 'c66427ddb32f7b32aec69e875146088b29acfed581d1995dd59a85f1f70d0739', '076cd4da31df9212b946ac8fa6c2d4bda763d81e7f57262cf5425d9d764d410b'),
  ('2026-10-17 15:20:00+00'::timestamptz, 'A. Das', 'Inquiry committee formed', 'C-2026-0155', '076cd4da31df9212b946ac8fa6c2d4bda763d81e7f57262cf5425d9d764d410b', '6237f9a96de5e8dbf3852e197227cd1c11a4d7e5141bbece2df32d1878129fc9'),
  ('2026-10-18 09:40:00+00'::timestamptz, 'System', 'Case created from portal', 'C-2026-0192', '6237f9a96de5e8dbf3852e197227cd1c11a4d7e5141bbece2df32d1878129fc9', '14e6b4c095229ff2585bb0a089a38071d1c45227ecb94f872a1c99c9263eefb1'),
  ('2026-10-18 11:15:00+00'::timestamptz, 'P. Rao', 'College response sought', 'C-2026-0142', '14e6b4c095229ff2585bb0a089a38071d1c45227ecb94f872a1c99c9263eefb1', 'e4bce96e6178c46325333c379ba9aa01b12b7d15db34891bf52ef63a77800465'),
  ('2026-10-18 16:05:00+00'::timestamptz, 'P. Rao', 'College response sought', 'C-2026-0194', 'e4bce96e6178c46325333c379ba9aa01b12b7d15db34891bf52ef63a77800465', '8a0ccba4e6dc98260eef20efbf2b4fc264d6af540e87e408dbaedae32a335505'),
  ('2026-10-19 12:30:00+00'::timestamptz, 'R. Menon', 'Show-cause notice issued', 'C-2026-0190', '8a0ccba4e6dc98260eef20efbf2b4fc264d6af540e87e408dbaedae32a335505', '713e2811337cdc654c7c2a349a7ba5df4a0139e0558827144b3b2b256b3abfff'),
  ('2026-10-19 15:10:00+00'::timestamptz, 'System', 'Overlap detected (94%)', 'CL-02', '713e2811337cdc654c7c2a349a7ba5df4a0139e0558827144b3b2b256b3abfff', '19fc1540c7b66e4861038146ca6420edb396f02790d39064b5a016a2b531d786'),
  ('2026-10-19 16:45:00+00'::timestamptz, 'S. Iyer', 'Statements obtained', 'C-2026-0196', '19fc1540c7b66e4861038146ca6420edb396f02790d39064b5a016a2b531d786', '0df0aba0b856df8f1d3a9609cb708de1196a676fec3706d2a10a1bc639d2451b'),
  ('2026-10-20 10:42:00+00'::timestamptz, 'R. Menon', 'Linked cases', 'C-2026-0167 → C-2026-0142', '0df0aba0b856df8f1d3a9609cb708de1196a676fec3706d2a10a1bc639d2451b', 'c1193940d0bbfd0592cd90dbf1d06537505ce4e057086432955752d37eb27efd'),
  ('2026-10-20 10:45:00+00'::timestamptz, 'P. Rao', 'Opened Coordination Room', 'CR-01', 'c1193940d0bbfd0592cd90dbf1d06537505ce4e057086432955752d37eb27efd', '6e591458f9de1e3aea1c9be79fb73a0cf717569cb20a4d05aa115adf11cf8c84'),
  ('2026-10-20 10:47:00+00'::timestamptz, 'R. Menon', 'Assigned lead bureau: RB', 'CR-01', '6e591458f9de1e3aea1c9be79fb73a0cf717569cb20a4d05aa115adf11cf8c84', '707ef6dc563d04b721bed46ea44ab1f7cd3cb6f2c862c67960505af694a2df23'),
  ('2026-10-20 14:20:00+00'::timestamptz, 'R. Menon', 'Records requested', 'C-2026-0167', '707ef6dc563d04b721bed46ea44ab1f7cd3cb6f2c862c67960505af694a2df23', 'a739f0dd5126ec5a5670346757f41e53a50a66a92be64874a4cc6e8dfcaa2f2a'),
  ('2026-10-20 15:35:00+00'::timestamptz, 'K. Nair', 'Documents under verification', 'C-2026-0193', 'a739f0dd5126ec5a5670346757f41e53a50a66a92be64874a4cc6e8dfcaa2f2a', '473c7c5bd6aa7af1eeaf76d9bf8faaa879625247dd6e9d6fa533ed86ff9d45c5'),
  ('2026-10-20 17:10:00+00'::timestamptz, 'R. Menon', 'Inspection scheduled', 'C-2026-0197', '473c7c5bd6aa7af1eeaf76d9bf8faaa879625247dd6e9d6fa533ed86ff9d45c5', 'f0e0d32ad309320defddedda5cb11b65c7027e67fb590f1f8e5c62deaa8f9479'),
  ('2026-10-21 09:12:00+00'::timestamptz, 'System', 'Overlap detected (97%)', 'CL-03', 'f0e0d32ad309320defddedda5cb11b65c7027e67fb590f1f8e5c62deaa8f9479', 'c88c9861a6367d86d1634ab357fc926383874929f62a99663b17cfbdc5151cfc'),
  ('2026-10-21 09:15:00+00'::timestamptz, 'System', 'Custody not accepted — escalated to Director', 'C-2026-0186', 'c88c9861a6367d86d1634ab357fc926383874929f62a99663b17cfbdc5151cfc', '03ec1d00f11f0613cd1f75ed5fe3611a3356d464834fbaee0914065564e6e421'),
  ('2026-10-21 11:40:00+00'::timestamptz, 'P. Rao', 'Case created from complaint email', 'C-2026-0198', '03ec1d00f11f0613cd1f75ed5fe3611a3356d464834fbaee0914065564e6e421', '748b44fc1aad8e9a1c05d0040b54e95f68d966ea5396dffc789139aab9fc6fe0');

commit;

analyze;

-- ---------------------------------------------------------------- verify
select 'institutions' as table_name, count(*) as row_count from institutions
union all select 'institution_aliases', count(*) from institution_aliases
union all select 'users', count(*) from users
union all select 'cases', count(*) from cases
union all select 'case_events', count(*) from case_events
union all select 'documents', count(*) from documents
union all select 'overlap_clusters', count(*) from overlap_clusters
union all select 'overlap_cases', count(*) from overlap_cases
union all select 'rooms', count(*) from rooms
union all select 'room_activity', count(*) from room_activity
union all select 'audit_entries', count(*) from audit_entries
order by table_name;

select * from audit_verify();

-- This hash must equal the one shown on the Data Layer screen.
select hash as chain_head from audit_entries order by id desc limit 1;
