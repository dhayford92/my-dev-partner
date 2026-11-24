import apiFetch from "@/hooks/apiFetch";
import { API_URLS } from "@/libs/api-urls";

export interface UserProfile {
  id: string;
  [key: string]: unknown;
}

/** Unwrap-or-throw — used directly in useQuery. See ../../../../_shared-mobile/data-layer.md. */
export async function getMe(): Promise<UserProfile> {
  return apiFetch<UserProfile>({ method: "GET", url: API_URLS.USERS.PROFILE.ME, autoAuth: true });
}
