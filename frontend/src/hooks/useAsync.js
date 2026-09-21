import { useEffect, useState } from "react";
import { isAborted } from "../api/client.js";

export function useAsync(asyncFn, deps) {
  const [state, setState] = useState({ data: null, loading: true, error: null });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    setState({ data: null, loading: true, error: null });

    Promise.resolve(asyncFn(controller.signal))
      .then((data) => {
        if (active) setState({ data, loading: false, error: null });
      })
      .catch((error) => {
        // A cancelled request is not a failure and must never render as one.
        if (!active || isAborted(error)) return;
        setState({ data: null, loading: false, error });
      });

    return () => {
      active = false;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
