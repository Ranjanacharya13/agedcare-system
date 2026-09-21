import { get, post, patch, del } from "./client.js";

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
    async list({ parentId, skip = 0, limit = 100, signal } = {}) {
      const path = `${basePath(config, parentId)}?skip=${skip}&limit=${limit}`;
      return get(path, { signal });
    },
    async getOne(id, { parentId, signal } = {}) {
      return get(`${basePath(config, parentId)}/${id}`, { signal });
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
