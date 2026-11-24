import { redirect } from "next/navigation";
import { getAccessToken } from "@/lib/actions/auth";

/**
 * Protected shell. Server component: guards on token presence before rendering. Add your sidebar
 * (SidebarProvider + AppSidebar) and any global context provider (e.g. UserTeamProvider) here.
 */
export default async function PortalLayout({ children }: { children: React.ReactNode }) {
  const token = await getAccessToken();
  if (!token) redirect("/login");

  return (
    <div className="min-h-screen bg-muted/30">
      <main className="mx-auto max-w-6xl p-6">{children}</main>
    </div>
  );
}
