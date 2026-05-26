-- Program records with stale verification dates
select
  program_id,
  program_name,
  data_tool,
  last_verified_date,
  completeness_pct
from utility_programs
where last_verified_date < date('2026-05-26', '-60 day')
order by last_verified_date;

-- Source observations that need citation cleanup
select
  program_id,
  source_type,
  field_name,
  citation_status,
  confidence_score
from source_observations
where citation_status <> 'complete'
order by confidence_score asc;

-- Open quality checks by procedure step
select
  procedure_step,
  severity,
  count(*) as open_checks,
  sum(affected_records) as affected_records
from quality_checks
where status <> 'resolved'
group by 1, 2
order by affected_records desc;

-- Data-tool updates blocked by missing or conflicting evidence
select
  data_tool,
  blocker,
  count(*) as blocked_updates,
  sum(records_pending) as pending_rows
from data_tool_updates
where blocker <> 'none'
group by 1, 2
order by pending_rows desc;

-- Research requests due within seven days
select
  request_id,
  program_id,
  request_type,
  audience,
  due_date,
  source_need,
  status
from research_requests
where due_date <= date('2026-05-26', '+7 day')
order by due_date, request_type;
