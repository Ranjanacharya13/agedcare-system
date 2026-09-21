import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { shiftLabel, shiftsOnDay, dayBounds, useStaffStatus } from "../../hooks/useStaffStatus.js";
import Skeleton from "../common/Skeleton.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

const HOURS = Array.from({ length: 13 }, (_, i) => i * 2);

/** One day, one row per person on shift, bars on a 24-hour ruler.
 *  Everyone with no shift that day is listed underneath in red. */
export default function DailyShiftCalendar() {
  const [day, setDay] = useState(() => new Date());
  const { staff, shifts, loading, error } = useStaffStatus();

  const { rows, off } = useMemo(() => {
    const todays = shiftsOnDay(shifts, day);
    const rows = staff
      .map((s) => ({ s, mine: todays.filter((x) => x.employee_id === s.employee_id) }))
      .filter((r) => r.mine.length);
    const off = staff.filter((s) => !todays.some((x) => x.employee_id === s.employee_id));
    return { rows, off };
  }, [day, shifts, staff]);

  const [dayStart] = dayBounds(day);
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
      <ErrorBanner error={error} />
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
            {rows.length === 0 && <p className="text-muted">Nobody is rostered this day.</p>}
            {rows.map(({ s, mine }) => (
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
