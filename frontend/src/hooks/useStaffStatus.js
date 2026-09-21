import { useMemo } from "react";
import { useAsync } from "./useAsync.js";
import { get } from "../api/client.js";
import { getStaffWorkload } from "../api/assignments.js";

const WORKING = new Set(["Scheduled", "Confirmed", "Completed"]);

export function dayBounds(date) {
  const start = new Date(date);
  start.setHours(0, 0, 0, 0);
  const end = new Date(start);
  end.setDate(end.getDate() + 1);
  return [start, end];
}

export function shiftsOnDay(shifts, date) {
  const [start, end] = dayBounds(date);
  return shifts.filter(
    (s) => WORKING.has(s.status) && new Date(s.shift_start) < end && new Date(s.shift_end) > start
  );
}

export function useStaffStatus() {
  const { data, loading, error } = useAsync(
    async (signal) => {
      const [shifts, workload] = await Promise.all([
        get("/shifts?skip=0&limit=1000", { signal }),
        getStaffWorkload({ signal }),
      ]);
      return { shifts, workload };
    },
    []
  );

  const byId = useMemo(() => {
    if (!data) return {};
    const today = shiftsOnDay(data.shifts, new Date());
    const out = {};
    for (const w of data.workload.staff) {
      const mine = today.filter((s) => s.employee_id === w.employee_id);
      const reason = !mine.length
        ? "No shift today"
        : w.active_residents === 0
          ? "No residents assigned"
          : null;
      out[w.employee_id] = {
        ...w,
        shiftsToday: mine,
        tone: reason ? "unavailable" : "available",
        reason,
      };
    }
    return out;
  }, [data]);

  return { byId, shifts: data?.shifts || [], staff: data?.workload.staff || [], loading, error };
}

export function shiftLabel(shift) {
  const t = (v) => new Date(v).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  return `${t(shift.shift_start)}–${t(shift.shift_end)}`;
}
