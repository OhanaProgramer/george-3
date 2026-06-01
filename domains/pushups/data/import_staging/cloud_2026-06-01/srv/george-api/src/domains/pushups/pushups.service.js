const { appendLogEntry, getDashboardCounts } = require("../../../models/pushupsModel");
const {
  readEvents,
  readDerived,
  readPublish,
} = require("./pushups.store");
const { rebuildPushups } = require("./pushups.rebuild");
const { getLogHealthModel } = require("../health/health.service");

function formatLastLoggedAt(ts) {
  if (!ts) return "";
  const date = new Date(ts);
  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function buildStoplight(publish) {
  const weeklyJumpPct = Number(publish && publish.risk && publish.risk.weekly_jump_pct);
  const avg7d = Number(publish && publish.consistency && publish.consistency.avg_7d);
  const avg30d = Number(publish && publish.consistency && publish.consistency.avg_30d);
  const highRampRisk = Boolean(publish && publish.risk && publish.risk.high_ramp_risk);
  const baseline = avg30d > 0 ? avg30d : null;
  const recentSurge = baseline !== null && avg7d > baseline * 1.1;

  if (highRampRisk || weeklyJumpPct >= 30) {
    return {
      level: "red",
      label: "Slow down",
    };
  }

  if (recentSurge || weeklyJumpPct >= 15) {
    return {
      level: "yellow",
      label: "Use caution",
    };
  }

  return {
    level: "green",
    label: "Steady pace",
  };
}

async function getLogData(overrides = {}) {
  const [{ todayCount, lifetimeCount }, healthModel, publish, events] = await Promise.all([
    getDashboardCounts(),
    getLogHealthModel(),
    readPublish().catch(() => ({})),
    readEvents().catch(() => []),
  ]);
  const lastEvent = Array.isArray(events) && events.length > 0 ? events[events.length - 1] : null;

  return {
    message: "",
    error: "",
    last: "",
    recoveryMessage: "",
    recoveryError: "",
    painMessage: "",
    painError: "",
    todayCount,
    lifetimeCount,
    stoplight: buildStoplight(publish),
    lastLoggedAt: formatLastLoggedAt(lastEvent && lastEvent.ts),
    ...healthModel,
    ...overrides,
  };
}

async function getAnalyticsData() {
  return getAnalyticsJson();
}

async function addLogEntry(reps, source = "server") {
  await appendLogEntry(reps, source);
  return rebuildPushups();
}

async function getStatsJson() {
  const derived = await readDerived();
  if (derived && typeof derived === "object" && Object.keys(derived).length > 0) {
    return derived;
  }
  await rebuildPushups();
  return readDerived();
}

async function getAnalyticsJson() {
  const publish = await readPublish();
  if (publish && typeof publish === "object" && Object.keys(publish).length > 0) {
    return publish;
  }
  await rebuildPushups();
  return readPublish();
}

module.exports = {
  getLogData,
  getAnalyticsData,
  addLogEntry,
  getStatsJson,
  getAnalyticsJson,
  rebuildPushups,
};
