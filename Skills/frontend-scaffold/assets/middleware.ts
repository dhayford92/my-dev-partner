import { NextResponse, type NextRequest } from "next/server";
import { cookies } from "next/headers";
import { ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE } from "@/lib/constants/api-urls";
import { clearTokenCookies, refreshTokenAction } from "@/lib/actions/auth";

/**
 * Route protection for /portal/*. Trusts token presence for performance (API 401s are handled
 * client-side); refreshes when only the refresh cookie remains; bounces authed users off /login.
 * See ../../_shared-web/api-contract.md.
 */
export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const store = await cookies();
  const access = store.get(ACCESS_TOKEN_COOKIE)?.value;
  const refresh = store.get(REFRESH_TOKEN_COOKIE)?.value;

  const loginUrl = () => {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    return url;
  };

  if (pathname.startsWith("/portal")) {
    if (access) return NextResponse.next();
    if (refresh) {
      const res = await refreshTokenAction(refresh);
      if (!res.error) return NextResponse.next();
    }
    await clearTokenCookies();
    return NextResponse.redirect(loginUrl());
  }

  if (pathname === "/login" && access) {
    const url = request.nextUrl.clone();
    url.pathname = "/portal";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
