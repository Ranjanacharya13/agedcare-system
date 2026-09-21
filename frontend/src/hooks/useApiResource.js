import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createResourceApi } from "../api/resourceApi.js";
import { isAborted } from "../api/client.js";

export function useApiResource(config, parentId) {
  const api = useMemo(() => createResourceApi(config), [config]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const inFlight = useRef(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      inFlight.current?.abort();
    };
  }, []);

  const reload = useCallback(() => {
    inFlight.current?.abort();
    const controller = new AbortController();
    inFlight.current = controller;

    setLoading(true);
    setError(null);
    api
      .list({ parentId, signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted && mounted.current) {
          setItems(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isAborted(err) || controller.signal.aborted || !mounted.current) return;
        setError(err);
        setLoading(false);
      });
  }, [api, parentId]);

  useEffect(() => {
    reload();
  }, [reload]);

  const create = useCallback(
    async (data) => {
      const created = await api.create(data, { parentId });
      setItems((prev) => [created, ...prev]);
      return created;
    },
    [api, parentId]
  );

  const update = useCallback(
    async (id, data) => {
      const updated = await api.update(id, data, { parentId });
      setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
      return updated;
    },
    [api, parentId]
  );

  const remove = useCallback(
    async (id) => {
      await api.remove(id, { parentId });
      setItems((prev) => prev.filter((item) => item.id !== id));
    },
    [api, parentId]
  );

  return { items, loading, error, create, update, remove, reload };
}
