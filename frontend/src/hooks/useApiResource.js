import { useCallback, useEffect, useMemo, useState } from "react";
import { createResourceApi } from "../api/resourceApi.js";

// Drives ResourcePanel: list/create/update/delete state for one resource
// config, optionally scoped to a parentId (resident/employee).
export function useApiResource(config, parentId) {
  const api = useMemo(() => createResourceApi(config), [config]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    api
      .list({ parentId })
      .then(setItems)
      .catch(setError)
      .finally(() => setLoading(false));
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
