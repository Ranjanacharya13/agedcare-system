import { get, post, patch, del } from "./client.js";

// The backend's flat `/{slug}` router only registers GET (see
// backend/api/v1/parent_scoped_router.py) -- there is no create/update/delete
// on a flat path for a parent-scoped resource. Any attempt to mutate without
// a parentId on such a resource is a wiring bug, so it throws immediately
// instead of silently 404ing against a route that doesn't exist.
function requireParentId(config, parentId) {
  if (config.parent && !parentId) {
    throw new Error(
      `${config.slug}: a parentId is required to mutate this parent-scoped resource`
    );
  }
}

function basePath(config, parentId) {
  if (!config.parent) return `/${config.slug}`;
  if (parentId) return `/${config.parent.resource}/${parentId}/${config.slug}`;
  return `/${config.slug}`; // flat, read-only fallback
}

export function createResourceApi(config) {
  return {
    async list({ parentId, skip = 0, limit = 100 } = {}) {
      const path = `${basePath(config, parentId)}?skip=${skip}&limit=${limit}`;
      return get(path);
    },
    async getOne(id, { parentId } = {}) {
      return get(`${basePath(config, parentId)}/${id}`);
    },
    async create(data, { parentId } = {}) {
      requireParentId(config, parentId);
      return post(basePath(config, parentId), data);
    },
    async update(id, data, { parentId } = {}) {
      requireParentId(config, parentId);
      return patch(`${basePath(config, parentId)}/${id}`, data);
    },
    async remove(id, { parentId } = {}) {
      requireParentId(config, parentId);
      return del(`${basePath(config, parentId)}/${id}`);
    },
  };
}
