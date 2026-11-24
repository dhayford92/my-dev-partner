/**
 * Pagination adapter. Frontend-canonical shape is
 * { data, current_page, page_limit, total_count }; this normalizes whatever a backend returned
 * (also handles { total, limit, page } and { items, total, page_size, has_next }).
 * See ../../../../_shared-web/api-contract.md.
 */
/* eslint-disable @typescript-eslint/no-explicit-any */

export interface Paginated<T> {
  data: T[];
  current_page: number;
  page_limit: number;
  total_count: number;
}

export function toPaginated<T>(body: any): Paginated<T> {
  const data: T[] = body?.data ?? body?.items ?? [];
  return {
    data,
    current_page: body?.current_page ?? body?.page ?? 1,
    page_limit: body?.page_limit ?? body?.limit ?? body?.page_size ?? data.length,
    total_count: body?.total_count ?? body?.total ?? data.length,
  };
}

export const totalPages = (p: Paginated<unknown>): number =>
  p.total_count === 0 ? 0 : Math.ceil(p.total_count / p.page_limit);

export const hasNextPage = (p: Paginated<unknown>): boolean =>
  p.current_page < totalPages(p);
