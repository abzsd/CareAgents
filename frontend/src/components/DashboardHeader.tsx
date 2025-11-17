import { Activity } from "lucide-react";

export function DashboardHeader() {
  const currentTime = new Date().toLocaleString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="bg-white border-b">
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1>Doctor's Dashboard</h1>
              <p className="text-slate-600">{currentTime}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-right">
              <p className="text-slate-600">Dr. Alexandra Smith</p>
              <p className="text-slate-500">Emergency Department</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
