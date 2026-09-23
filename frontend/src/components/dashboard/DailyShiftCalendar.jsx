import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { shiftLabel, shiftsOnDay, dayBounds, useStaffStatus } from "../../hooks/useStaffStatus.js";
import { useAsync } from "../../hooks/useAsync.js";
import { useDirectory } from "../../hooks/useDirectory.js";
import { getCareSchedule } from "../../api/assignments.js";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

const HOURS = Array.from({ length: 13 }, (_, i) => i * 2);

/** One day, one row per person on shift or with a care visit, bars on a 24-hour ruler.
 *  Shifts are the pale bar; each hourly care visit sits inside it, labelled with the resident.
 *  Everyone with no shift that day is listed underneath in red. */
export default function DailyShiftCalendar() {
  const [day, setDay] = useState(() => new Date());
  const { staff, shifts, loading, error } = useStaffStatus();
  const { residentsById } = useDirectory();
  const [dayStart, dayEnd] = dayBounds(day);
  const schedule = useAsync(
    (signal) => getCareSchedule(dayStart, dayEnd, { signal }),
    [dayStart.getTime()]
  );

  const { rows, off } = useMemo(() => {
    const todays = shiftsOnDay(shifts, day);
    const visits = schedule.data || [];
    const rows = staff
      .map((s) => ({
        s,
        mine: todays.filter((x) => x.employee_id === s.employee_id),
        visits: visits.filter((v) => v.employee_id === s.employee_id),
      }))
      .filter((r) => r.mine.length || r.visits.length);
    const off = staff.filter((s) => !todays.some((x) => x.employee_id === s.employee_id));
    return { rows, off };
  }, [day, shifts, staff, schedule.data]);

  const visitLabel = (v) => {
    const r = residentsById[v.resident_id];
    const who = r ? `${r.first_name} ${r.last_name}${r.room_number ? ` · ${r.room_number}` : ""}` : "Resident";
    return `${shiftLabel({ shift_start: v.start_at, shift_end: v.end_at })} ${who}${v.task ? ` — ${v.task}` : ""}`;
  };
  const pct = (v) => Math.min(100, Math.max(0, ((new Date(v) - dayStart) / 864e5) * 100));
  const move = (n) => setDay((d) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n));

  return (
    <section className="card fade-slide-in day-cal">
      <div className="day-cal-head">
        <h2>Daily roster</h2>
        <div className="day-cal-nav">
          <button type="button" onClick={() => move(-1)} aria-label="Previous day">‹</button>
          <strong>
            {day.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "short" })}
          </strong>
          <button type="button" onClick={() => move(1)} aria-label="Next day">›</button>
          <button type="button" onClick={() => setDay(new Date())}>Today</button>
        </div>
      </div>
      <ErrorBanner error={error || schedule.error} />
      {loading ? (
        <Skeleton rows={4} />
      ) : (
        <>
          <div className="day-cal-grid">
            <div className="day-cal-ruler">
              <span />
              <div className="day-cal-scale">
                {HOURS.map((h) => (
                  <span key={h} style={{ left: `${(h / 24) * 100}%` }}>
                    {String(h).padStart(2, "0")}
                  </span>
                ))}
              </div>
            </div>
            {rows.length === 0 && <p className="text-muted">Nobody is rostered or scheduled this day.</p>}
            {rows.map(({ s, mine, visits }) => (
              <div key={s.employee_id} className="day-cal-row">
                <Link to={`/admin/employees/${s.employee_id}`} className="day-cal-name">
                  {s.first_name} {s.last_name}
                  <small>{s.role || "—"} · {s.active_residents} resident{s.active_residents === 1 ? "" : "s"}</small>
                </Link>
                <div className="day-cal-track">
                  {mine.map((x) => (
                    <span
                      key={x.id}
                      className="day-cal-bar"
                      title={`${shiftLabel(x)} ${x.location || ""}`}
                      style={{ left: `${pct(x.shift_start)}%`, width: `${pct(x.shift_end) - pct(x.shift_start)}%` }}
                    >
                      {shiftLabel(x)}
                    </span>
                  ))}
                  {visits.map((v) => (
                    <Link
                      key={v.id}
                      to={`/admin/residents/${v.resident_id}/care-visits`}
                      className="day-cal-visit"
                      title={visitLabel(v)}
                      style={{ left: `${pct(v.start_at)}%`, width: `${pct(v.end_at) - pct(v.start_at)}%` }}
                    >
                      {residentsById[v.resident_id]?.first_name || "Resident"}
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
          {off.length > 0 && (
            <p className="day-cal-off">
              <strong>No shift:</strong>{" "}
              {off.map((s) => (
                <Link key={s.employee_id} to={`/admin/employees/${s.employee_id}/shifts`} className="off-chip">
                  {s.first_name} {s.last_name}
                </Link>
              ))}
            </p>
          )}
        </>
      )}
    </section>
  );
}
