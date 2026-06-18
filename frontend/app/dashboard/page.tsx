// Redirect /dashboard → /dashboard/home
import { redirect } from "next/navigation";
export default function DashboardRoot() {
  redirect("/dashboard/home");
}