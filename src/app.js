const viewMeta = {
  quality: {
    eyebrow: "Quality control",
    title: "Program QA priority queue",
    note: "Ranked by open checks, stale verification dates, source confidence, citation gaps, and pending data-tool updates."
  },
  updates: {
    eyebrow: "Data-tool maintenance",
    title: "Update plan for research tools",
    note: "Rows that need population, source reconciliation, definition documentation, or caveated publication."
  },
  requests: {
    eyebrow: "Research support",
    title: "Client and analyst request triage",
    note: "Research requests prioritized by deadline pressure, program risk, source needs, and audience."
  },
  briefs: {
    eyebrow: "Stakeholder communication",
    title: "Written summary builder",
    note: "Short findings that translate quality evidence into a clear next step for nontechnical reviewers."
  }
};

const numberFormatter = new Intl.NumberFormat("en-US");

function formatNumber(value) {
  return numberFormatter.format(Number(value || 0));
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function pill(value) {
  const normalized = String(value).toLowerCase().replaceAll(" ", "-");
  return `<span class="pill ${normalized}">${value}</span>`;
}

function qualityRows(rows) {
  return `
    <table>
      <thead>
        <tr>
          <th>Program</th>
          <th>Tool</th>
          <th>Score</th>
          <th>Checks</th>
          <th>Citations</th>
          <th>Next action</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map((row) => `
          <tr>
            <td><strong>${row.program_name}</strong><small>${row.program_area}</small></td>
            <td>${row.data_tool}</td>
            <td>${row.priority_score}</td>
            <td>${row.open_checks} open, ${formatNumber(row.affected_records)} records</td>
            <td>${row.missing_citations} gaps, ${row.avg_confidence_score} confidence</td>
            <td>${pill(row.recommended_action)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function updateRows(rows) {
  return `
    <div class="card-grid">
      ${rows.slice(0, 12).map((row) => `
        <article class="work-card">
          <div>
            <span>${row.update_id}</span>
            <strong>${row.data_tool}</strong>
          </div>
          <h3>${row.update_type}</h3>
          <dl>
            <div><dt>Rows</dt><dd>${formatNumber(row.records_pending)}</dd></div>
            <div><dt>Complete</dt><dd>${row.completeness_pct}%</dd></div>
            <div><dt>Blocker</dt><dd>${row.blocker}</dd></div>
          </dl>
          <p>${row.recommended_next_step}</p>
        </article>
      `).join("")}
    </div>
  `;
}

function requestRows(rows) {
  return `
    <table>
      <thead>
        <tr>
          <th>Request</th>
          <th>Audience</th>
          <th>Due</th>
          <th>Source need</th>
          <th>Response</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map((row) => `
          <tr>
            <td><strong>${row.request_type}</strong><small>${row.program_area}</small></td>
            <td>${row.audience}</td>
            <td>${row.due_date}</td>
            <td>${row.source_need}</td>
            <td>${row.recommended_response}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function briefRows(rows) {
  return `
    <div class="brief-list">
      ${rows.map((row, index) => `
        <article class="brief-row">
          <span>${String(index + 1).padStart(2, "0")}</span>
          <div>
            <h3>${row.headline}</h3>
            <p>${row.stakeholder_summary}</p>
            <small>${row.evidence}</small>
          </div>
        </article>
      `).join("")}
    </div>
  `;
}

function renderView(payload, view) {
  const meta = viewMeta[view];
  setText("surfaceEyebrow", meta.eyebrow);
  setText("surfaceTitle", meta.title);
  setText("surfaceNote", meta.note);

  const body = document.getElementById("surfaceBody");
  if (view === "quality") {
    body.innerHTML = qualityRows(payload.qualityQueue);
  }
  if (view === "updates") {
    body.innerHTML = updateRows(payload.toolPlan);
  }
  if (view === "requests") {
    body.innerHTML = requestRows(payload.requestTriage);
  }
  if (view === "briefs") {
    body.innerHTML = briefRows(payload.briefPack);
  }
}

async function boot() {
  const response = await fetch("analysis/outputs/app_payload.json");
  const payload = await response.json();
  const topProgram = payload.qualityQueue[0];

  setText("statPrograms", formatNumber(payload.summary.programs));
  setText("statSources", formatNumber(payload.summary.source_observations));
  setText("statChecks", formatNumber(payload.summary.open_quality_checks));
  setText("statUpdates", formatNumber(payload.summary.pending_tool_rows));
  setText("currentFocus", `${topProgram.program_id} ${topProgram.program_area}`);
  setText("focusCopy", `${topProgram.recommended_action} across ${formatNumber(topProgram.pending_updates)} pending rows and ${topProgram.open_checks} open checks.`);

  renderView(payload, "quality");

  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      renderView(payload, button.dataset.view);
    });
  });
}

boot();
